import os
import zipfile
from PIL import Image

from checksum import md5_file

def parse_start_header(header_string):
    parts = header_string.strip().split("|")

    if parts[0] != "START":
        print("Invalid header.")
        return None

    return {
        "total_chunks": int(parts[1]),
        "chunk_size": int(parts[2]),
        "md5": parts[3]
    }

def receiver(chunk_file="sent_chunks.bin", received_zip="detected_images.zip", out_folder="received_images"):

    with open("start_header.txt", "r") as f:
        header_string = f.read()

    header_info = parse_start_header(header_string)

    if header_info is None:
        return

    print("Received START header:", header_info)

    if not os.path.exists(chunk_file):
        print("Error: chunk file not found:", chunk_file)
        return

    # rebuilding zip 
    with open(chunk_file, "rb") as f_in, open(received_zip, "wb") as f_out:
        f_out.write(f_in.read())

    print("Rebuilt zip:", received_zip)

    # verifying MD5
    received_md5 = md5_file(received_zip)
    expected_md5 = header_info["md5"]

    print("Received MD5:", received_md5)
    print("Expected MD5:", expected_md5)

    if received_md5 == expected_md5:
        print("MD5 MATCH")
    else:
        print("MD5 MISMATCH (file corrupted or incomplete)")
        return


    # unzip
    os.makedirs(out_folder, exist_ok=True)
    with zipfile.ZipFile(received_zip, "r") as zf:
        zf.extractall(out_folder)

    print("Unzipped to:", out_folder)

    # verify pngs that were zipped and sent
    print("\nPIL check (PNG files):")
    for root, dirs, files in os.walk(out_folder):
        for file in files:
            if file.lower().endswith(".png"):
                path = os.path.join(root, file)
                im = Image.open(path)
                print(file, "-", im.format, im.size)

if __name__ == "__main__":
    receiver()
