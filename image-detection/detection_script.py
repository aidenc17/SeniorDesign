import cv2
import numpy as np
import os
import shutil
from pathlib import Path

def dectect_red_circles(path_to_image): 

    """
    script used for detection of red circles in images.
    """

    
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




if __name__ == "__main__":
    INPUT_FOLDER = "image-detection/test_images"      # folder that contains images from usb script
    OUTPUT_FOLDER = "image-detection/detected_images" # folder to save images with detected red circles