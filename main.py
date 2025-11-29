import pyautogui
from pynput import keyboard
import json
import os
import logging
import sys

# Setup logging
logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_sequence_from_config(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    steps = config.get("steps", [])
    for step in steps:
        action = step.get("action")
        image_path = step.get("stepImage")
        logging.info(f"Step: {step}")
        if action == "find_and_click" and image_path:
            print(f"Finding and clicking: {image_path}")
            logging.info(f"Finding and clicking: {image_path}")
            if not find_and_click(image_path):
                print(f"Image not found: {image_path}")
                logging.warning(f"Image not found: {image_path}")
                return
        elif action == "paste_from_clipboard":
            print("Pasting from clipboard...")
            logging.info("Pasting from clipboard...")
            paste_from_clipboard()
        elif action == "type":
            text = step.get("stepText", "")
            print(f"Typing: {text}")
            logging.info(f"Typing: {text}")
            write_text(text)
        elif action == "find_with_scroll" and image_path:
            print(f"Finding with scroll: {image_path}")
            logging.info(f"Finding with scroll: {image_path}")
            if not find_with_scroll_and_click(image_path):
                print(f"Image not found after scrolling: {image_path}")
                logging.warning(f"Image not found after scrolling: {image_path}")
                return
        else:
            print(f"Unknown or incomplete step: {step}")
            logging.error(f"Unknown or incomplete step: {step}")
            return


def locate_image_gd(image_path, min_conf=0.1, max_conf=1.0):
    """Safely locate an image on screen, reducing confidence if not found or exception occurs."""
    conf = max_conf
    while conf > min_conf:
        # pyautogui.sleep(0.1)
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=conf)
            logging.info(f"locate_image_gd: Trying {image_path} with confidence {conf}")
            if location:
                logging.info(
                    f"locate_image_gd: Found {image_path} at {location} with confidence {conf}"
                )
                return location
        except Exception as e:
            logging.error(
                f"locate_image_gd: Exception for {image_path} with confidence {conf}: {e}"
            )
        conf -= 0.1
    logging.warning(
        f"locate_image_gd: {image_path} not found with confidence >= {min_conf}"
    )
    return None


def locate_image(image_path, confidence=0.5):
    """Safely locate an image on screen"""
    try:
        return pyautogui.locateOnScreen(image_path, confidence=confidence)
    except Exception:
        return None


def scroll_page(direction="down", steps=5):
    """Scroll the page using arrow keys"""
    pyautogui.scroll(-2)
    # key = "down" if direction == "down" else "up"
    # for _ in range(steps):
    #     pyautogui.press(key)


def find_with_scroll_and_click(image_path):
    """Find an image on screen and click it"""
    screenWidth, screenHeight = pyautogui.size()
    screenshot = pyautogui.screenshot()
    scale = screenshot.size[0] / screenWidth

    print(f"\nSearching for {image_path}...")
    logging.info(f"Searching for {image_path}...")
    location = locate_image(image_path)

    # Scroll down to find it (from current mouse position)
    if not location:
        for _ in range(10):
            scroll_page("down", steps=5)
            logging.info(f"Scrolling to find {image_path}")
            location = locate_image(image_path)
            if location:
                break

    # Click if found
    if location:
        center = pyautogui.center(location)
        adjusted_x = int(center.x / scale)
        adjusted_y = int(center.y / scale)

        pyautogui.moveTo(adjusted_x, adjusted_y, duration=0.1)
        pyautogui.click(adjusted_x, adjusted_y)
        pyautogui.click(adjusted_x, adjusted_y)
        print(f"Clicked {image_path}!")
        logging.info(f"Clicked {image_path} at ({adjusted_x}, {adjusted_y})")
        return True
    else:
        print(f"{image_path} not found")
        logging.warning(f"{image_path} not found after scrolling")
        return False


def find_and_click(image_path):
    """Find an image on screen and click it"""
    screenWidth, screenHeight = pyautogui.size()
    screenshot = pyautogui.screenshot()
    scale = screenshot.size[0] / screenWidth

    print(f"\nSearching for {image_path}...")
    logging.info(f"Searching for {image_path}...")
    location = locate_image_gd(image_path)

    # Click if found
    if location:
        center = pyautogui.center(location)
        adjusted_x = int(center.x / scale)
        adjusted_y = int(center.y / scale)

        pyautogui.moveTo(adjusted_x, adjusted_y, duration=0.1)
        pyautogui.click(adjusted_x, adjusted_y)
        pyautogui.click(adjusted_x, adjusted_y)
        print(f"Clicked {image_path}!")
        logging.info(f"Clicked {image_path} at ({adjusted_x}, {adjusted_y})")
        return True
    else:
        print(f"{image_path} not found")
        logging.warning(f"{image_path} not found")
        return False


def paste_from_clipboard():
    """Paste from clipboard using Cmd+V"""
    pyautogui.hotkey("command", "v")
    logging.info("Pasted from clipboard using Cmd+V")


def write_text(text):
    """Type text using pyautogui"""
    pyautogui.write(text)
    logging.info(f"Typed text: {text}")


def on_activate(emr_profile="open-mrs"):
    """Called when hotkey is pressed"""
    print("\n" + "=" * 50)
    print("Starting automation sequence...")
    print("=" * 50)
    logging.info("Automation sequence started")

    config_path = os.path.join("emr_profiles", emr_profile, "config.json")
    run_sequence_from_config(config_path)


def main():
    # Get EMR profile from command line argument, default to 'open-mrs'
    emr_profile = sys.argv[1] if len(sys.argv) > 1 else "open-mrs"
    # Set to track if cmd and shift are pressed
    current_keys = set()

    def on_press(key):
        """Track key presses"""
        current_keys.add(key)

        # Check if Cmd+Shift+K is pressed
        if (
            keyboard.Key.cmd in current_keys
            and keyboard.Key.shift in current_keys
            and hasattr(key, "char")
            and key.char == "k"
        ):
            on_activate(emr_profile)

    def on_release(key):
        """Track key releases"""
        try:
            current_keys.discard(key)
        except KeyError:
            pass

        # Exit on ESC key
        if key == keyboard.Key.esc:
            print("\nESC pressed. Exiting...")
            logging.info("ESC pressed. Exiting...")
            return False

    print("Hotkey listener started!")
    print("Press Cmd+Shift+K to search for and click the button")
    print("Press ESC to exit\n")
    logging.info("Hotkey listener started. Waiting for hotkey...")

    # Start listening for keyboard events
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
