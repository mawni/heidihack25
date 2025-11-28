import pyautogui
import time
import tagui as r


def move_mouse_to_button(image_path, confidence=0.9):
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


def find_and_click_with_scroll(image_path, text, confidence=0.5, max_attempts=5):
    """
    Try to find the image on screen, click and type text. If not found, scroll down and retry up to max_attempts.
    Raises ImageNotFoundException if not found after all attempts.
    """
    from pyautogui import ImageNotFoundException

    attempt = 0
    while attempt < max_attempts:
        try:
            if move_mouse_to_button(image_path, confidence=confidence):
                click_and_type(text)
                return True
            else:
                raise ImageNotFoundException
        except ImageNotFoundException:
            pyautogui.scroll(-10)
            attempt += 1
    raise ImageNotFoundException(
        f"Could not find {image_path} after {max_attempts} scroll attempts."
    )


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
    print("\nSearching for goal.png on screen...")
    # Take a screenshot first to see what we're working with
    screenshot = pyautogui.screenshot()
    print(f"Screenshot size: {screenshot.size}")

    try:
        find_and_click_with_scroll(
            "goal_3.png", "Hello, DuckDuckGo!", confidence=0.5, max_attempts=5
        )
        print("Done! ✅")
    except pyautogui.ImageNotFoundException as e:
        print(f"Button not found on screen after scrolling: {e}")


if __name__ == "__main__":
    main()
