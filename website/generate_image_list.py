#!/usr/bin/env python3
"""
Generate images.json file listing all images in received_images folder
This allows the website to load images without knowing their names in advance
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

def generate_image_list(images_dir="../received_images", output_file="images.json"):
    """
    Scan received_images folder and create JSON file with image metadata
    """
    # Get absolute path
    images_path = Path(images_dir).resolve()
    
    if not images_path.exists():
        print(f"ERROR: Directory not found: {images_path}")
        return
    
    images = []
    
    for file in sorted(images_path.iterdir()):
        # ✅ ONLY grab PNG files
        if file.suffix.lower() == ".png":

            # 🔥 sanitize filename (remove spaces & weird chars)
            clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.name)
            new_path = file.with_name(clean_name)

            # rename file if needed
            if file.name != clean_name:
                file.rename(new_path)
                file = new_path  # update reference

            # Get file info
            stat = file.stat()
            
            image_info = {
                "filename": file.name,
                "path": f"../received_images/{file.name}",  # keep your original format
                "size": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            images.append(image_info)
    
    # Create metadata object
    metadata = {
        "generated": datetime.now().isoformat(),
        "total_images": len(images),
        "images": images
    }
    
    # Write to JSON file
    output_path = Path(output_file)
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Generated image list: {output_path.absolute()}")
    print(f"  Found {len(images)} PNG images")
    for img in images:
        print(f"  - {img['filename']} ({img['size_kb']} KB)")


if __name__ == "__main__":
    generate_image_list()