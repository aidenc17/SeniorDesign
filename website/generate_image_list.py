#!/usr/bin/env python3
"""
Generate images.json file listing all images in received_images folder
This allows the website to load images without knowing their names in advance
"""

import os
import json
from pathlib import Path
from datetime import datetime

def generate_image_list(images_dir="../received_images", output_file="images.json"):
    """
    Scan received_images folder and create JSON file with image metadata
    
    Args:
        images_dir: Path to received images folder
        output_file: Output JSON file path
    """
    # Get absolute path
    images_path = Path(images_dir).resolve()
    
    if not images_path.exists():
        print(f"ERROR: Directory not found: {images_path}")
        return
    
    # Find all image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    images = []
    
    for file in sorted(images_path.iterdir()):
        if file.suffix.lower() in image_extensions:
            # Get file info
            stat = file.stat()
            
            image_info = {
                "filename": file.name,
                "path": f"../received_images/{file.name}",
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
    print(f"  Found {len(images)} images")
    for img in images:
        print(f"  - {img['filename']} ({img['size_kb']} KB)")


if __name__ == "__main__":
    generate_image_list()