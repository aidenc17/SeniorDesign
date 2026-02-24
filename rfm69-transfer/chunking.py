import os
import numpy as np
import cv2
import PIL
from cv2 import *
from PIL import Image

CHUNK_SIZE = 60  # bytes (small on purpose; want to try v small first)



def split_file_into_chunks(filename):
    chunks = []

    with open(filename, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            chunks.append(data)

    return chunks

def write_chunks_to_file(chunks, out_filename):
    with open(out_filename, "wb") as f:
        for chunk in chunks:
            f.write(chunk)



if __name__ == "__main__":
    test_file = "example.txt"

    if not os.path.exists(test_file):
        print("test file not found:", test_file)
    else:
        pieces = split_file_into_chunks(test_file)
        
        print("File:", test_file)
        print("chunk size:", CHUNK_SIZE)

        print("total chunks:", len(pieces))

        # printing the first few chunks for testing/seeing what it's doing
        for i in range(min(3, len(pieces))):
            print(f"Chunk {i} length:", len(pieces[i]))
