import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import os
import zipfile

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "rfm69_transfer" / "output"
HEADER_FILE = OUTPUT_DIR / "start_header.txt"
CHUNK_FILE = OUTPUT_DIR / "sent_chunks.bin"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from rfm69_transfer.shared.checksum import md5_file


RADIO_PACKET_SIZE = 60

# parsing out the header sent at beginning of transmission
# with info about how many chunks, how big each one is,
# and the md5 checksum to verify data integrity at the end
def parse_start_header(header_string):
    parts = header_string.strip().split("|")

    if parts[0] != "START":
        print("invalid header :(")
        return None

    return {
        "total_chunks": int(parts[1]),
        "chunk_size": int(parts[2]),
        "md5": parts[3]
    }


def init_rfm69():

    """
    real hardware setup for Raspberry Pi + Adafruit RFM69.
    will only work on the Pi when the hardware is connected.
    """
    import board
    import busio
    import digitalio
    import adafruit_rfm69

    # may need to adjust these values once actual radio is done
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.CE1)      # adjust if wiring differs, i dunno wiring
    reset = digitalio.DigitalInOut(board.D17)   # this too

    rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)
    return rfm69


def receive_start_header_sim():
    with open(HEADER_FILE, "r") as f:
        header_string = f.read()

    print("START header from file")
    return header_string


def receive_chunks_sim(chunk_file):
    if not os.path.exists(chunk_file):
        print("error - chunk file not found:", chunk_file)
        return None

    with open(chunk_file, "rb") as f:
        data = f.read()

    print("chunk data from file:", chunk_file)
    return data

# timeout currently set at 10 seconds, can adjust up or down after testing
def receive_start_header_rfm69(rfm69, timeout=10.0):
    """
    Placeholder 
    for now, assuming START header fits in one packet
    if it gets longer later, extend this
    """
    print("waiting for START header over radio.")

    packet = rfm69.receive(timeout=timeout)

    # nothing will happen if no header received first
    if packet is None:
        print("No START header received.")
        return None

    try:
        header_string = packet.decode("utf-8")
        print("received START header over radio:", header_string)
        return header_string
    except Exception as e:
        print("could not decode START header - ", e)
        return None

# timeout currently set at 5 seconds for image transmission, can be adjusted as necessary
# would not go above 8 seconds currently
def receive_chunks_rfm69(rfm69, total_chunks, chunk_size, timeout=5.0):

    # informing how many packets total should be sent
    print("waiting for", total_chunks, "chunks over radio")

    received_data = bytearray()
    chunks_received = 0

    while chunks_received < total_chunks:
        packet = rfm69.receive(timeout=timeout)

        # lets us know if any particular packet didn't get sent within 5 seconds
        if packet is None:
            print("timed out waiting for chunk", chunks_received)
            break

        received_data.extend(packet)
        chunks_received += 1
        print("received chunk", chunks_received, "size", len(packet))

    # letting us know how many chunks total were received
    print("Finished radio receive. Got", chunks_received, "chunks.")
    return bytes(received_data)


def rebuild_zip_from_bytes(data, received_zip):
    with open(received_zip, "wb") as f_out:
        f_out.write(data)



def verify_and_extract(received_zip, expected_md5, out_folder):
    received_md5 = md5_file(received_zip)

    print("Received MD5:", received_md5)
    print("Expected MD5:", expected_md5)

    # informing if md5 indicates lost data
    if received_md5 == expected_md5:
        print("MD5 MATCH")
    else:
        print("MD5 MISMATCH (file corrupted or incomplete)")
        return

    os.makedirs(out_folder, exist_ok=True)

    with zipfile.ZipFile(received_zip, "r") as zf:
        zf.extractall(out_folder)

    print("unzipped to:", out_folder)

    print("\nPIL check (PNG files):")
    for root, dirs, files in os.walk(out_folder):
        for file in files:
            if file.lower().endswith(".png"):
                path = os.path.join(root, file)
                im = Image.open(path)
                print(file, "-", im.format, im.size)

# TO DO: make bidirectional if time allows (send md5 checksum to sender pi) 

# change mode to "rfm69" when doing actual radio testing; sim is for non-radio simulation
# filenames, etc. can be changed to match other code if necessary
# destination of photos can be changed as well, especially if they need to be uploaded to repo in real time during demo
def receiver(chunk_file=CHUNK_FILE, received_zip="detected_images.zip",
             out_folder="received_images", mode="sim"):

    if mode == "sim":
        header_string = receive_start_header_sim()
        if header_string is None:
            return

        header_info = parse_start_header(header_string)
        if header_info is None:
            return

        print("received START header:", header_info)

        data = receive_chunks_sim(chunk_file)
        if data is None:
            return

    elif mode == "rfm69":
        try:
            rfm69 = init_rfm69()
            #verifying the init worked
            print("RFM69 init")

            header_string = receive_start_header_rfm69(rfm69)
            if header_string is None:
                return

            header_info = parse_start_header(header_string)
            if header_info is None:
                return

            print("received START header:", header_info)

            data = receive_chunks_rfm69(rfm69, header_info["total_chunks"], header_info["chunk_size"])

            if data is None:
                return

        except Exception as e:
            print("radio receive failed:", e)
            return

    else:
        print("Error - unsupported mode:", mode)
        return

    rebuild_zip_from_bytes(data, received_zip)
    verify_and_extract(received_zip, header_info["md5"], out_folder)


if __name__ == "__main__":
    receiver()