import cv2
import numpy as np
import os
import shutil
from pathlib import Path

# Use absolute path based on script location, not cwd
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, "detected_images")

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

def find_all_images(root_path):
    """
    Recursively search for all image files (.png, .jpg, .jpeg) in a directory tree.
    Returns a list of full file paths.
    """
    image_extensions = ('.png', '.jpg', '.jpeg')
    image_files = []
    
    print(f"Searching for images in: {root_path}")
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            # Skip macOS metadata files
            if filename.startswith("._"):
                continue
            if filename.lower().endswith(image_extensions):
                full_path = os.path.join(dirpath, filename)
                image_files.append(full_path)
                print(f"  Found: {filename}")
    
    return image_files

def main(): 
    # Search for Raspberry Pi USB
    usb_root = "/media/raspberrypi" # CHAGNED TO RUN ON KALLI PI
    output_folder = OUTPUT_FOLDER
    
    print(f"Looking for USB at: {usb_root}\n")
    
    if not os.path.exists(usb_root):
        print(f"ERROR: USB not found at {usb_root}")
        return
    
    # Find all images recursively
    image_files = find_all_images(usb_root)
    
    if not image_files:
        print("ERROR: No images found on USB")
        return
    
    print(f"\nFound {len(image_files)} total images\n")
    
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    detected_count = 0
    
    for image_path in image_files:
        filename = os.path.basename(image_path)
        
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
    main()