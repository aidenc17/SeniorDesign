import cv2
import numpy as np
import os
import shutil
from pathlib import Path

def dectect_red_circles(path_to_image): 

    """
    script used for detection of red circles in images.
    """


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