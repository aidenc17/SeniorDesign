from checksum import md5_file
from chunking import split_file_into_chunks, write_chunks_to_file, CHUNK_SIZE
from PIL import Image
import zipfile
import os


def sender_sim(folder_name="detected_images.zip", chunk_dump="sent_chunks.bin"):
    if not os.path.exists(folder_name):
        print("Error: folder does not exist:", folder_name)
        return


    # compute MD5 + size
    file_size = os.path.getsize(folder_name)
    file_hash = md5_file(folder_name)

    print("Zip size:", file_size, "bytes")
    print("MD5:", file_hash)
    print("Chunk size:", CHUNK_SIZE, "bytes")

    # chunk the zip
    chunks = split_file_into_chunks(folder_name)
    print("Total chunks:", len(chunks))

    # simulate sending
    write_chunks_to_file(chunks, chunk_dump)
    print("Wrote chunks to:", chunk_dump)

    # write the expected MD5 to a file so receiver can compare 
    with open("expected_md5.txt", "w") as f:
        f.write(file_hash)

    print("Wrote expected MD5 to: expected_md5.txt")

if __name__ == "__main__":
    sender_sim()
