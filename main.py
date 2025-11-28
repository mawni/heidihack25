import pyautogui
import time


def main():
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
    
    location = pyautogui.locateOnScreen('button.png', confidence=0.8)

    if location:
        print(f"Found button at: {location}")
        
        # Account for Retina display scaling
        scale = screenshot.size[0] / screenWidth
        print(f"Display scale factor: {scale}")
        
        center = pyautogui.center(location)
        adjusted_x = int(center.x / scale)
        adjusted_y = int(center.y / scale)
        print(f"Adjusted coordinates: ({adjusted_x}, {adjusted_y})")

        # Move mouse to the button
        print("Moving mouse to the button...")
        pyautogui.moveTo(adjusted_x, adjusted_y, duration=0.5)
        print("Done! ✅")
    else:
        print("Button not found on screen ❌")


if __name__ == "__main__":
    main()
