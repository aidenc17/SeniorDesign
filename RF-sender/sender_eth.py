import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import socket
import os
from rfm69_transfer.shared.checksum import md5_file


# making a header to send first
def make_start_header(file_size, md5_hash, filename):
    return f"START|{file_size}|{md5_hash}|{filename}\n"

# change the receiver_ip to whatever the ip address of the receiver pi is when directly connected to sender pi with ethernet cable
def sender_eth(filename="detected_images.zip", receiver_ip="127.0.0.1", port=5001):
    if not os.path.exists(filename):
        print("error - file does not exist:", filename)
        return

    file_size = os.path.getsize(filename)
    file_hash = md5_file(filename)

    #print("File:", filename)
   # print("Size:", file_size, "bytes")
    #print("MD5:", file_hash)

    header = make_start_header(file_size, file_hash, os.path.basename(filename))

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((receiver_ip, port))
        print("connected to receiver at", receiver_ip, "port", port)

        # sending header
        sock.sendall(header.encode("utf-8"))
        print("sent header:", header.strip())

        # sending file bytes
        with open(filename, "rb") as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                sock.sendall(data)

        print("fnished sending file.")
        sock.close()

    except Exception as e:
        print("error during send: - ", e)


if __name__ == "__main__":
    # changes IP later to the receiver Pi's IP
    sender_eth()