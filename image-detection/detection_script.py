import cv2
import numpy as np
import os
import shutil
from pathlib import Path
import platform

def detect_red_circle(image_path):
    image = cv2.imread(image_path)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # define red color range 
    # CAN TWEAK LATER IF NEEDED
    # value thresholds. 
    lower_red1 = np.array([0, 150, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 150, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # create masks for red color
    # masks do a bitwise OR to combine both ranges
    mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    masked_image = cv2.bitwise_and(image, image, mask=red_mask)
    gray_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (9, 9), 2)
    
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # check each contour to see if it's circular
    for contour in contours:
        # skip very small contours (increased minimum size)
        area = cv2.contourArea(contour)
        if area < 200:  # Increased minimum area threshold
            continue
        
        # fit a circle to the contour
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        circularity = 4 * np.pi * area / (perimeter ** 2)
        
        # strict circularity threshold - must be more circular
        # perfect circle = 1.0 
        # CAN CHANGE
        if circularity > 0.75:
            # Get the circle's center and radius
            (x, y), radius = cv2.minEnclosingCircle(contour)
            return (int(x), int(y), int(radius))
    
    return None

def crop_circle(image, x, y, r):
    # added padding to make crop less tight (increase by 50%)
    padding = int(r * 0.5)
    r_padded = r + padding
    
    top_left_x = max(0, x - r_padded)
    top_left_y = max(0, y - r_padded)
    bottom_right_x = min(image.shape[1], x + r_padded)
    bottom_right_y = min(image.shape[0], y + r_padded)
    
    cropped_image = image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
    return cropped_image

def load_image(image_path):
    """
    load an image from the path
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    return image

def find_usb_folder(folder_name="test_images"):
    """
    search for a USB drive and look for a specific folder on it.
    in order this : mac (/Volumes/), raspberry pi (/media/), windows (D:, E:, F:, G:) 
    """
    system = platform.system()
    search_paths = []
    
    if system == "Darwin":  # macs
        search_paths = ["/Volumes"]
    elif system == "Linux":  # raspberry pis
        search_paths = ["/media/raspberrypi/", "/media"] 
    elif system == "Windows":
        # checking windows usb letters
        search_paths = [f"{letter}:" for letter in "DEFGHI" if os.path.exists(f"{letter}:")]
    
    print(f"Searching for USB in {search_paths}...")
    
    # mac and linux searches in directories
    if system in ["Darwin", "Linux"]:
        for volumes_path in search_paths:
            if not os.path.exists(volumes_path):
                continue
            
            for volume in os.listdir(volumes_path):
                volume_path = os.path.join(volumes_path, volume)
                
                if not os.path.isdir(volume_path):
                    continue
                
                target_path = os.path.join(volume_path, folder_name)
                if os.path.isdir(target_path):
                    print(f"Found '{folder_name}' at: {target_path}")
                    return target_path
    
    # checking windows drives
    elif system == "Windows":
        for drive in search_paths:
            target_path = os.path.join(drive, folder_name)
            if os.path.isdir(target_path):
                print(f"Found '{folder_name}' at: {target_path}")
                return target_path
    
    print(f"✗ Could not find USB with '{folder_name}' folder")
    return None

def main(): 
    # now only look for Raspberry Pi folder
    input_folder = "/media/raspberrypi/BOOTS"
    output_folder = OUTPUT_FOLDER
    
    print(f"Looking for images in: {input_folder}")
    
    if not os.path.exists(input_folder):
        print(f"ERROR: Raspberry Pi folder not found at {input_folder}")
        return
    
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(image_files)} images\n")
    
    detected_count = 0
    
    for filename in image_files:
        image_path = os.path.join(input_folder, filename)
        
        try:
            image = load_image(image_path)
            circle = detect_red_circle(image_path)
            
            if circle is not None:
                x, y, r = circle
                cropped_image = crop_circle(image, x, y, r)
                output_path = os.path.join(output_folder, filename)
                cv2.imwrite(output_path, cropped_image)
                detected_count += 1
                print(f"{filename}")
            else:
                print(f"{filename}")
        except Exception as e:
            print(f"{filename} - Error: {e}")
    
    print(f"\nDetection complete. Found {detected_count}/{len(image_files)} images with red circles.")
    
    # zips the detected images folder
    zip_path = os.path.join(os.path.dirname(output_folder), f"{output_folder}.zip")
    shutil.make_archive(os.path.splitext(zip_path)[0], 'zip', output_folder)
    print(f"Created zip file: {zip_path}")

if __name__ == "__main__":
    OUTPUT_FOLDER = "detected_images"
    main()