import cv2
import numpy as np
import os
import shutil
from pathlib import Path

def detect_red_circle(image_path):
    image = cv2.imread(image_path)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # define red color range 
    # CAN TWEAK LATER IF NEEDED
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # create masks for red color
    # masks do a bitwise OR to combine both ranges
    mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    masked_image = cv2.bitwise_and(image, image, mask=red_mask)
    gray_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (9, 9), 2)
    
    circles = cv2.HoughCircles(blurred_image, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                            param1=100, param2=30, minRadius=0, maxRadius=0)
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        x, y, r = circles[0]
        return (x, y, r)
    else:
        return None

def crop_circle(image, x, y, r):
    top_left_x = max(0, x - r)
    top_left_y = max(0, y - r)
    bottom_right_x = min(image.shape[1], x + r)
    bottom_right_y = min(image.shape[0], y + r)
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

def main(): 
    input_folder = INPUT_FOLDER
    output_folder = OUTPUT_FOLDER
    
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    print(f"Looking for images in: {os.path.abspath(input_folder)}")
    
    if not os.path.exists(input_folder):
        print(f"ERROR: Input folder does not exist: {input_folder}")
        return
    
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(image_files)} images")
    
    for filename in image_files:
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = load_image(image_path)
            circle = detect_red_circle(image_path)
            
            if circle is not None:
                x, y, r = circle
                cropped_image = crop_circle(image, x, y, r)
                output_path = os.path.join(output_folder, filename)
                cv2.imwrite(output_path, cropped_image)
                print(f"Detected red circle in {filename}, saved cropped image.")
            else:
                print(f"No red circle detected in {filename}.")

if __name__ == "__main__":
    INPUT_FOLDER = "test_images"      # folder that contains images from usb script
    OUTPUT_FOLDER = "detected_images" # folder to save images with detected red circles
    main()