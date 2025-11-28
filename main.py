import pyautogui
import time
import tagui as r


def move_mouse_to_button(image_path, confidence=0.5):
    """
    Locate a button on the screen using the given image and move the mouse to its center.
    Returns True if found and moved, False otherwise.
    """
    screenWidth, screenHeight = pyautogui.size()
    screenshot = pyautogui.screenshot()
    location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    if location:
        scale = screenshot.size[0] / screenWidth
        center = pyautogui.center(location)
        adjusted_x = int(center.x / scale)
        adjusted_y = int(center.y / scale)
        pyautogui.moveTo(adjusted_x, adjusted_y, duration=0.1)
        return True
    else:
        return False


def click_and_type(text):
    pyautogui.click()
    pyautogui.write(text)


def main():
    r.init(visual_automation=True)
    r.url("https://duckduckgo.com")
    r.wait(2)
    # Get screen size
    screenWidth, screenHeight = pyautogui.size()
    print(f"Screen size: {screenWidth}x{screenHeight}")

    # Get current mouse position
    currentX, currentY = pyautogui.position()
    print(f"Current mouse position: ({currentX}, {currentY})")

    # Try to locate a button on screen
    print("\nSearching for button.png on screen...")
    # Take a screenshot first to see what we're working with
    screenshot = pyautogui.screenshot()
    print(f"Screenshot size: {screenshot.size}")

    if move_mouse_to_button("testsearch.png", confidence=0.5):
        click_and_type("Hello, DuckDuckGo!")
        print("Done! ✅")
    else:
        print("Button not found on screen ❌")


if __name__ == "__main__":
    main()
