from PIL import ImageGrab
import os

def take_screenshot(save_path=None):
    """
    Takes a screenshot of the entire screen and saves it to the specified path.

    :param save_path: The file path where the screenshot will be saved.
                      If None, saves to the default "supporting/screenshot.png".
    """
    if save_path is None:
        # Ensure the supporting directory exists
        os.makedirs("supporting", exist_ok=True)
        save_path = "supporting/screenshot.png"

    # Capture the screen
    screenshot = ImageGrab.grab()
    
    # Save the screenshot to the specified path
    screenshot.save(save_path, "PNG")
    print(f"Screenshot saved to {save_path}") 