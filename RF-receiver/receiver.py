import sys
import time
import board
import busio
import digitalio
import adafruit_rfm69
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
from rfm69_transfer.shared.chunking import (
    parse_radio_packet,
    make_control_packet,
    make_missing_packet,
    parse_missing_packet,
    is_control_packet,
    END_PAYLOAD,
    DONE_PAYLOAD,
    COMPLETE_PAYLOAD
)


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

    # may need to adjust these values once actual radio is done
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.CE1)      # adjust if wiring differs, i dunno wiring
    reset = digitalio.DigitalInOut(board.D17)   # this too

    rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)

    # making it go faster and more powerful
    rfm69.bitrate = 50000
    rfm69.rx_bw = 125000
    rfm69.tx_power = 18

    # encryption 
    # yes this is literally it, this hits the requirements for the project
    # both sender and receiver have this key
    rfm69.encryption_key = b"teampr2ojectskey"

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

# timeout currently set at 300 seconds just for testing, can adjust up or down after testing
def receive_start_header_rfm69(rfm69, timeout=300.0):

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
    received_chunks = {}
    duplicates = 0

    while True:
        packet = rfm69.receive(timeout=timeout)

        if packet is None:
            print("still waiting for packets...")
            continue

        parsed = parse_radio_packet(packet)
        if parsed is None:
            print("bad packet received")
            continue

        seq_num, payload = parsed
        if seq_num is None or payload is None:
            print("bad packet received")
            continue

        # control packet from sender
        if is_control_packet(seq_num):
            if payload == END_PAYLOAD:
                missing = [i for i in range(total_chunks) if i not in received_chunks]

                if len(missing) == 0:
                    print("no missing chunks, sending COMPLETE")
                    complete_packet = make_control_packet(COMPLETE_PAYLOAD)

                    # sending a few times for safety; stuff gets dropped a lot
                    for _ in range(3):
                        rfm69.send(complete_packet)
                        time.sleep(0.05)

                    return received_chunks

                print("missing chunks:", missing[:20])
                if len(missing) > 20:
                    print("...and", len(missing) - 20, "more")

                # send missing chunk numbers back in groups
                remaining = missing[:]
                while len(remaining) > 0:
                    missing_packet, remaining = make_missing_packet(remaining)

                    # safety sends
                    for _ in range(3):
                        rfm69.send(missing_packet)
                        time.sleep(0.05)


                done_packet = make_control_packet(DONE_PAYLOAD)

                for _ in range(3):
                    rfm69.send(done_packet)
                    time.sleep(0.05)

                print("sent missing list to sender")
                continue

            # ignoring other control packets here
            continue

        # normal data packets
        if seq_num in received_chunks:
            duplicates += 1
        else:
            received_chunks[seq_num] = payload

            if seq_num % 200 == 0:
                print("received up to chunk", seq_num, "total unique:", len(received_chunks))

        if duplicates % 50 == 0 and duplicates > 0:
            print("duplicates ignored:", duplicates)




def rebuild_zip_from_bytes(received_chunks, total_chunks, received_zip):
    
    missing = []

    for i in range(total_chunks):
        if i not in received_chunks:
            missing.append(i)

    if len(missing) > 0:
        print("missing chunks: ", missing[:20])
        if len(missing) > 20:
            print("...and", len(missing) - 20, "more")

        return False


    with open(received_zip, "wb") as f_out:
        for i in range(total_chunks):
            f_out.write(received_chunks[i])

    return True


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

# TO DO: send md5 checksum back to sender pi

# change mode to "rfm69" when doing actual radio testing; sim is for non-radio simulation
# filenames, etc. can be changed to match other code if necessary
# destination of photos can be changed as well, especially if they need to be uploaded to repo in real time during demo
def receiver(chunk_file=CHUNK_FILE, received_zip="detected_images.zip",
             out_folder="received_images", mode="rfm69"):

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

            received_chunks = receive_chunks_rfm69(rfm69, header_info["total_chunks"], header_info["chunk_size"])

            success = rebuild_zip_from_bytes(received_chunks, header_info["total_chunks"], received_zip)

            if not success:
                print("couldnt rebuilt zip correctly")
                return

        except Exception as e:
            print("radio init receive failed:", e)
            return

    else:
        print("Error - unsupported mode:", mode)
        return

    verify_and_extract(received_zip, header_info["md5"], out_folder)


if __name__ == "__main__":
    receiver()
