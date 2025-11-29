import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# Path to the emr_profiles directory
EMR_PROFILES_DIR = "emr_profiles"


# Function to run download_profiles.py
def run_download_profiles():
    try:
        subprocess.run(["python", "download_profiles.py"], check=True)
        messagebox.showinfo("Success", "Profiles downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download profiles: {e}")


# Function to run main.py for a selected profile
def run_main_for_profile(profile_folder):
    config_path = os.path.join(EMR_PROFILES_DIR, profile_folder, "config.json")
    env = os.environ.copy()
    env["PROFILE_CONFIG"] = config_path
    try:
        subprocess.Popen(["python", "main.py"], env=env)
        messagebox.showinfo("Started", f"Started automation for {profile_folder}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start automation: {e}")


# Create the main window
root = tk.Tk()
root.title("EMR Automation Frontend")
root.geometry("400x600")

# Download profiles button
download_btn = tk.Button(
    root, text="Download Profiles", command=run_download_profiles, height=2, width=30
)
download_btn.pack(pady=20)

# List EMR profile folders and create buttons for each
profile_folders = [
    f
    for f in os.listdir(EMR_PROFILES_DIR)
    if os.path.isdir(os.path.join(EMR_PROFILES_DIR, f))
]

for folder in profile_folders:
    btn = tk.Button(
        root,
        text=folder,
        command=lambda f=folder: run_main_for_profile(f),
        height=2,
        width=30,
    )
    btn.pack(pady=10)

root.mainloop()
