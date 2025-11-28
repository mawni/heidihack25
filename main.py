import pyautogui


def main():
    screenWidth, screenHeight = pyautogui.size()
    print(f"Screen size: {screenWidth}x{screenHeight}")
    pyautogui.moveTo(100, 150)
    print("Hello, heidihack25!")
    distance = 200


if __name__ == "__main__":
    main()
