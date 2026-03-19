import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import socket
import os
import zipfile
from PIL import Image
from rfm69_transfer.shared.checksum import md5_file


def parse_start_header(header_text):
    parts = header_text.strip().split("|")

    if len(parts) != 4 or parts[0] != "START":
        raise ValueError("START header incorrect or bad format")

    file_size = int(parts[1])

    md5_hash = parts[2]

    filename = parts[3]

    return file_size, md5_hash, filename

# this might need a LOT of work; this is first attempt at networking stuff for me
# so half of it might not be right
def receiver_eth(save_folder="received_files", port=5001):
    
    os.makedirs(save_folder, exist_ok=True)

    # i know what this is doing in theory but this was sourced elsewhere
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("0.0.0.0", port))
    server_sock.listen(1)

    print("listening on port", port)

    conn, addr = server_sock.accept()
    print("connected by", addr)

    try:
        # reading header until newline
        header_bytes = b""
        while b"\n" not in header_bytes:
            piece = conn.recv(1)
            if not piece:
                raise ValueError("connection closed before header finished")
            header_bytes += piece

        header_text = header_bytes.decode("utf-8")
        print("received header:", header_text.strip())

        file_size, expected_md5, filename = parse_start_header(header_text)

        out_path = os.path.join(save_folder, filename)

        # more print statements for testing purposes
        # md5 checksum line is helpful to keep for demo tho
        print("Expected file size:", file_size)
        print("Expected MD5:", expected_md5)
        print("Saving to:", out_path)

        bytes_received = 0

        with open(out_path, "wb") as f:
            while bytes_received < file_size:
                remaining = file_size - bytes_received
                chunk = conn.recv(min(4096, remaining))

                if not chunk:
                    break

                f.write(chunk)
                bytes_received += len(chunk)

        print("finished receiving.")
        print("bytes received:", bytes_received)

        if bytes_received != file_size:
            print("error: file size mismatch")
            return
        else:
            print("file size matches")

        received_md5 = md5_file(out_path)
        print("received MD5:", received_md5)

        if received_md5 == expected_md5:
            print("MD5 MATCH")
        else:
            # TO DO:
            # if mismatch, have receiver tell sender to resend
            print("MD5 MISMATCH")
            return

        
        unzip_folder = os.path.join(save_folder, "unzipped_images")
        os.makedirs(unzip_folder, exist_ok=True)

        with zipfile.ZipFile(out_path, "r") as zf:
            zf.extractall(unzip_folder)

        # showing where it was all sent to; can/will change if necessary
        print("unzipped to:", unzip_folder)

        # verifing pngs
        # dunno if necessary for demo but its nice for testing purposes
        print("\nPNG files:")
        for root, dirs, files in os.walk(unzip_folder):
            for file in files:
                if file.lower().endswith(".png"):
                    path = os.path.join(root, file)
                    im = Image.open(path)
                    print(file, "-", im.format, im.size)

    except Exception as e:
        print("error during receive -", e)

    conn.close()
    server_sock.close()


if __name__ == "__main__":
    receiver_eth()