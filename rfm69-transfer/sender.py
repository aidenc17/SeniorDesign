from checksum import md5_file
from chunking import split_file_into_chunks, write_chunks_to_file, CHUNK_SIZE
from PIL import Image
import zipfile
import os

# makes a header to send the md5 checksum expected as the first chunk sent
def make_start_header(total_packets, chunk_size, md5_hash):

    return f"START|{total_packets}|{chunk_size}|{md5_hash}"

def sender_sim(filename="detected_images.zip", chunk_file="sent_chunks.bin"):
    
    # path where zipped folder of images are stored on sender pi
    # will add in once pi is up and running and can be tested properly
    # /home/raspberrypi/SeniorDesign/image-detection/detected_images.zip
    if not os.path.exists(filename):
        print("Error: folder does not exist:", filename)
        return

    # compute MD5 + size
    file_size = os.path.getsize(filename)
    file_hash = md5_file(filename)

    print("Zip size:", file_size, "bytes")
    print("MD5:", file_hash)
    print("Chunk size:", CHUNK_SIZE, "bytes")

    # chunk the zip
    chunks = split_file_into_chunks(filename)
    total_chunks = len(chunks)

    print("Total chunks:", total_chunks)

    # creating start header
    header = make_start_header(total_chunks, CHUNK_SIZE, file_hash)

    # simulates sending start header
    with open("start_header.txt", "w") as f:
        f.write(header)

    print("Wrote START header:", header)

    # simulating sending chunk data
    write_chunks_to_file(chunks, chunk_file)
    print("Wrote chunks to:", chunk_file)

if __name__ == "__main__":
    sender_sim()
