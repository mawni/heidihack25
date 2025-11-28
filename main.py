import pyautogui
from pynput import keyboard


def locate_image(image_path, confidence=0.9):
    """Safely locate an image on screen"""
    try:
        return pyautogui.locateOnScreen(image_path, confidence=confidence)
    except Exception:
        return None


def scroll_page(direction='down', steps=5):
    """Scroll the page using arrow keys"""
    key = 'down' if direction == 'down' else 'up'
    for _ in range(steps):
        pyautogui.press(key)


def find_and_click(image_path):
    """Find an image on screen and click it"""
    screenWidth, screenHeight = pyautogui.size()
    screenshot = pyautogui.screenshot()
    scale = screenshot.size[0] / screenWidth

    print(f"\nSearching for {image_path}...")
    location = locate_image(image_path)

    # Scroll down to find it (from current mouse position)
    if not location:
        for _ in range(20):
            scroll_page('down', steps=10)
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
        return True
    else:
        print(f"{image_path} not found")
        return False


def on_activate():
    """Called when hotkey is pressed"""
    print("\n" + "="*50)
    print("Starting automation sequence...")
    print("="*50)

    # Step 1
    if not find_and_click('step1.png'):
        return

    # Step 2
    if not find_and_click('step2.png'):
        return

    # Paste from clipboard
    print("\nPasting from clipboard...")
    pyautogui.hotkey('command', 'v')

    # Step 3: Type "skull"
    if not find_and_click('step3.png'):
        return
    print("\nTyping 'skull'...")
    pyautogui.write('skull')

    # Step 4: Find and select
    if not find_and_click('step4.png'):
        return

    # Step 5: Scroll down to find
    find_and_click('step5.png')


def main():
    # Set to track if cmd and shift are pressed
    current_keys = set()

    def on_press(key):
        """Track key presses"""
        current_keys.add(key)

        # Check if Cmd+Shift+K is pressed
        if (keyboard.Key.cmd in current_keys and
            keyboard.Key.shift in current_keys and
            hasattr(key, 'char') and key.char == 'k'):
            on_activate()

    def on_release(key):
        """Track key releases"""
        try:
            current_keys.discard(key)
        except KeyError:
            pass

        # Exit on ESC key
        if key == keyboard.Key.esc:
            print("\nESC pressed. Exiting...")
            return False

    print("Hotkey listener started!")
    print("Press Cmd+Shift+K to search for and click the button")
    print("Press ESC to exit\n")

    # Start listening for keyboard events
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
