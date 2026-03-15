import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


import os

from rfm69_transfer.shared.checksum import md5_file
from rfm69_transfer.shared.chunking import split_file_into_chunks, write_chunks_to_file, CHUNK_SIZE


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "rfm69_transfer" / "output"
HEADER_FILE = OUTPUT_DIR / "start_header.txt"
CHUNK_FILE = OUTPUT_DIR / "sent_chunks.bin"
IMAGE_ZIP = PROJECT_ROOT / "image-detection" / "detected_images.zip"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# radio packet size for circuitpython RFM69 path
RADIO_PACKET_SIZE = 60




# makes a header to send md5 checksum expected as first chunk sent
def make_start_header(total_packets, chunk_size, md5_hash):
    return f"START|{total_packets}|{chunk_size}|{md5_hash}"

# making individual chunks in correct size to send
def split_bytes_for_radio(data, packet_size=RADIO_PACKET_SIZE):

    radio_packets = []

    for i in range(0, len(data), packet_size):
        radio_packets.append(data[i:i + packet_size])

    return radio_packets


def init_rfm69():
    """
    hardware setup for pi + adafruit RFM69 (so, not the sim version)
    """
    import board
    import busio
    import digitalio
    import adafruit_rfm69

    # these are guesses, am not very familiar with radio wiring 
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.CE1)      # may adjust if wiring uses different CS pin
    reset = digitalio.DigitalInOut(board.D17)   # may adjust if wiring uses different reset pin

    rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)
    return rfm69

# making the header to send ahead of actual image data packets
def send_start_header_sim(header):
    with open(HEADER_FILE, "w") as f:
        f.write(header)

    print("wrote START header: ", header)

# writing the chunks made earlier to file for simulation purposes
def send_chunks_sim(chunks, chunk_file):

    write_chunks_to_file(chunks, chunk_file)
    print("wrote chunks to ", chunk_file)

# encoding start header to send at beginning of transmission and then sending header chunks one at a time via rfm69
def send_start_header_rfm69(header, rfm69):

    header_bytes = header.encode("utf-8")

    header_packets = split_bytes_for_radio(header_bytes)

    # sending each packet and keeping track of count and size via print statements
    for i, packet in enumerate(header_packets):
        rfm69.send(packet)
        print("sent header packet", i, "size", len(packet))

# sending the actual image chunks 
def send_chunks_rfm69(chunks, rfm69):
    packet_count = 0

    for chunk_index, chunk in enumerate(chunks):
        radio_packets = split_bytes_for_radio(chunk)

        for packet in radio_packets:
            rfm69.send(packet)
            packet_count += 1       # counting up by one each time a new packet is being sent 

        # keeping track of what's been sent so far
        print("sent chunk", chunk_index, "as", len(radio_packets), "radio packets")

    print("total radio packets sent: ", packet_count)

# change mode to "rfm69" when doing actual radio testing
# other args should remain unchanged
def sender(filename=IMAGE_ZIP, chunk_file=CHUNK_FILE, mode="sim"):

    if not os.path.exists(filename):
        print("error - file does not exist: ", filename)
        return

    file_size = os.path.getsize(filename)

    file_hash = md5_file(filename)

    # lots of print statements for testing; can be removed if theyre cluttering things up too much
    print("zip size: ", file_size, "bytes")
    print("MD5: ", file_hash)
    print("chunk size: ", CHUNK_SIZE, "bytes")

    chunks = split_file_into_chunks(filename)
    total_chunks = len(chunks)

    print("total chunks: ", total_chunks)

    header = make_start_header(total_chunks, CHUNK_SIZE, file_hash)

    # below section allows for both simulation mode and actual testing with the radio once it's up and running
    # change mode in sender args to "rfm69" for actual radio code to run and "sim" to allow for simulation testing 
    if mode == "sim":
        send_start_header_sim(header)
        send_chunks_sim(chunks, chunk_file)

    elif mode == "rfm69":
        
        try:
            rfm69 = init_rfm69()
            print("RFM69 init")
            send_start_header_rfm69(header, rfm69)
            send_chunks_rfm69(chunks, rfm69)
        except Exception as e:
            print("radio send failed: ", e)

    # may not need this else; here for extra safety/error handling
    else:
        print("error- unsupported mode: ", mode)


if __name__ == "__main__":
    sender()