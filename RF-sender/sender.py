import sys
import time
import board
import busio
import digitalio
import adafruit_rfm69
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import os

from rfm69_transfer.shared.checksum import md5_file
from rfm69_transfer.shared.chunking import (
    split_file_into_chunks, 
    write_chunks_to_file, 
    CHUNK_SIZE, 
    make_radio_packet, 
    parse_radio_packet, 
    make_control_packet, 
    parse_missing_packet,
    is_control_packet, 
    END_PAYLOAD,
    DONE_PAYLOAD,
    COMPLETE_PAYLOAD
)


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
  
    # these are guesses, am not very familiar with radio wiring 
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.CE1)      # may adjust if wiring uses different CS pin
    reset = digitalio.DigitalInOut(board.D17)   # may adjust if wiring uses different reset pin

    rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, 915.0)
    
    # making it go faster and more powerful
    rfm69.bitrate = 50000
    rfm69.rx_bw = 125000
    rfm69.tx_power = 18

    # both sender and receiver have this encryption key
    rfm69.encryption_key = b"teampr2ojectskey"

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
        rfm69.send_with_ack(packet)
        print("sent header packet", i, "size", len(packet))


# change mode to "rfm69" when doing actual radio testing
# other args should remain unchanged
def sender(filename=IMAGE_ZIP, chunk_file=CHUNK_FILE, mode="rfm69"):

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

    # for testing only; remove for demo
    #chunks = chunks[:300]

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

            header_bytes = header.encode("utf-8")
            if not rfm69.send_with_ack(header_bytes):
                print("failed to send start header")
                return

            print("sent start header:", header)

            success = send_chunks_rfm69(chunks, rfm69)

            if success:
                print("all chunks sent and confirmed")
            else:
                print("send failed")

        except Exception as e:
            print("radio init send failed: ", e)

    # may not need this else; here for extra safety/error handling
    else:
        print("error- unsupported mode: ", mode)

# resending the packets that didn't make it/get processed the first time by receiver
def send_selected_chunks(chunks, chunk_numbers, rfm69, max_retries=10):
    
    for seq_num in chunk_numbers:
        chunk = chunks[seq_num]
        packet = make_radio_packet(seq_num, chunk)
        
        success = False
        
        for attempt in range(max_retries):
            if seq_num % 50 == 0:
                print("sending chunk ", seq_num, "attempt ", attempt + 1)

            if rfm69.send_with_ack(packet):
                success = True
                # only printing out every 50, printing every packet being sent is way too much
                if seq_num % 50 == 0:
                    print("chunk ", seq_num, "ACK received")
                # needs to give receiver a little time to process the packet before trying to send the next one
                time.sleep(0.09)
                break
            
        if not success:
            print("error - chunk ", seq_num, "failed after retries")
            return False
    return True


def send_chunks_rfm69(chunks, rfm69, max_rounds=5):
    
    total_chunks = len(chunks)
    
    success = send_selected_chunks(chunks, range(total_chunks), rfm69)
    if not success:
        return False
        
    for round_num in range(max_rounds):
        print("sending end pack for resend round", round_num +1)
        end_packet = make_control_packet(END_PAYLOAD)
        rfm69.send(end_packet)
        rfm69.listen()
        time.sleep(0.2)
        
        missing = []
        got_done = False
        got_complete = False
        
        start_time = time.time()
        
        while time.time() - start_time < 10:
            packet = rfm69.receive(timeout=1.0)
            
            if packet is None:
                continue
                
            parsed = parse_radio_packet(packet)
            if parsed is None:
                continue
            
            seq_num, payload = parsed
            
            if seq_num is None or payload is None:
                continue
                
            if not is_control_packet(seq_num):
                continue
                
            if payload == COMPLETE_PAYLOAD:
                got_complete = True
                break 

            if payload == DONE_PAYLOAD:
                got_done = True
                continue
            
            missing_part = parse_missing_packet(payload)
            if missing_part is not None:
                missing = list(set(missing + missing_part))
                
        if got_complete:
            print("receiever says transfer is complete")
            return True
            
        if not got_done:
            print("did not receieve DONE/COMPLETE, trying END again")
            continue
            
        if len(missing) == 0:
            print("no missing chunks, sending END again to confirm")
            continue
            
        print("resending", len(missing), "missing chunks")
        print("missing chunk numbers: ", missing[:20])
        
        success = send_selected_chunks(chunks, missing, rfm69)
        if not success:
            return False
    print("max resend rounds reached without COMPLETE")
    return False



if __name__ == "__main__":
    sender()
