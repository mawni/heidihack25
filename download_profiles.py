import os
import hashlib
import requests
import json
from pathlib import Path


BASE_URL = "https://pub-20e40d03340f4605b91ef74246e6d487.r2.dev"
PROFILES_DIR = "emr_profiles"

# List of EMR profiles to download
EMR_PROFILES = [
    "open-mrs",
    "openmrsv4",
    "test",
    "openmrsv7",
    # Add more profiles here as needed
]


def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    if not os.path.exists(filepath):
        return None

    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def download_file(url, filepath):
    """Download a file from URL to filepath"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  ✓ Downloaded: {filepath}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to download {url}: {e}")
        return False


def needs_update(url, local_path):
    """Check if local file needs to be updated"""
    if not os.path.exists(local_path):
        return True

    try:
        # Get remote file metadata
        response = requests.head(url)
        response.raise_for_status()

        remote_size = int(response.headers.get("content-length", 0))
        local_size = os.path.getsize(local_path)

        # Compare file sizes
        if remote_size != local_size:
            return True

        # Optionally download and compare hashes for same-size files
        temp_response = requests.get(url)
        remote_hash = hashlib.md5(temp_response.content).hexdigest()
        local_hash = get_file_hash(local_path)

        return remote_hash != local_hash

    except requests.exceptions.RequestException:
        # If we can't check, assume it needs update
        return True


def download_config(profile_name):
    """Download config.json for a given EMR profile"""
    print(f"  - Downloading config.json for {profile_name}")

    profile_dir = Path(PROFILES_DIR) / profile_name
    profile_dir.mkdir(parents=True, exist_ok=True)

    url = f"{BASE_URL}/{profile_name}/config.json"
    local_path = profile_dir / "config.json"

    if needs_update(url, local_path):
        if download_file(url, local_path):
            return True
    else:
        print(f"  ≈ Skipped (up to date): config.json")
        return True

    return False


def update_config_step(profile_name):
    """
    Overwrite the stepImage in config.json for a given profile to point to the correct local step image path.
    """
    config_path = Path(PROFILES_DIR) / profile_name / "config.json"
    if not config_path.exists():
        print(f"Config not found for profile: {profile_name}")
        return
    with open(config_path, "r") as f:
        config = json.load(f)
    steps = config.get("steps", [])
    for step in steps:
        order = step.get("order")
        if order:
            step["stepImage"] = f"./emr_profiles/{profile_name}/step{order}.png"
    config["steps"] = steps
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Overwritten stepImage paths in {config_path}")


def download_profile_images(profile_name, max_steps=10):
    """Download all step images for a given EMR profile"""
    print(f"\nProcessing profile: {profile_name}")

    # Create profile directory
    profile_dir = Path(PROFILES_DIR) / profile_name
    profile_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    skipped = 0

    # Try to download step images (step1.png, step2.png, etc.)
    for step_num in range(1, max_steps + 1):
        filename = f"step{step_num}.png"
        url = f"{BASE_URL}/{profile_name}/{filename}"
        local_path = profile_dir / filename

        # Check if file exists at URL
        try:
            response = requests.head(url)
            if response.status_code == 404:
                print(f"  - No step {step_num} found )")
                continue
        except requests.exceptions.RequestException:
            print(f"  - Could not check {filename}, stopping")
            break

        # Check if we need to download
        if needs_update(url, local_path):
            if download_file(url, local_path):
                downloaded += 1
        else:
            print(f"  ≈ Skipped (up to date): {filename}")
            skipped += 1

    print(f"  Summary: {downloaded} downloaded, {skipped} skipped")
    return downloaded, skipped


def main():
    """Download all EMR profile images"""
    print("=" * 50)
    print("EMR Profile Image Downloader")
    print("=" * 50)

    total_downloaded = 0
    total_skipped = 0

    for profile in EMR_PROFILES:
        downloaded, skipped = download_profile_images(profile)
        total_downloaded += downloaded
        total_skipped += skipped
    download_config(profile)
    update_config_step(profile)
    print("\n" + "=" * 50)
    print(f"Total: {total_downloaded} downloaded, {total_skipped} skipped")
    print("=" * 50)


if __name__ == "__main__":
    main()
