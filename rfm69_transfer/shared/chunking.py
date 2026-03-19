import os
import PIL
import struct
from PIL import Image

CHUNK_SIZE = 57  # bytes (small on purpose; need to be under 60 bytes as that's the radio limit)
CONTROL_SEQ = 65535


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

def make_radio_packet(seq_num, payload):
    return struct.pack(">HB", seq_num, len(payload)) + payload


def parse_radio_packet(packet):
    if packet is None or len(packet) < 3:
        return None, None

    seq_num, payload_len = struct.unpack(">HB", packet[:3])
    payload = packet[3:3 + payload_len]

    if len(payload) != payload_len:
        return None, None

    return seq_num, payload

    
END_PAYLOAD = b"END"
DONE_PAYLOAD = b"DONE"
COMPLETE_PAYLOAD = b"COMPLETE"

# b"M" = 1 byte, count = 1 byte, each seq = 2 bytes, and max payload is 57 bytes
# so, 1+1+2*n <=57 is n <= 27
MAX_MISSING_PER_PACKET = 27

def make_control_packet(payload: bytes):
    return make_radio_packet(CONTROL_SEQ, payload)
    
def is_control_packet(seq_num):
    return seq_num == CONTROL_SEQ
    
def make_missing_packet(missing_list):
    count = min(len(missing_list), MAX_MISSING_PER_PACKET)
    
    payload = b"M" + bytes([count])
    
    for seq_num in missing_list[:count]:
        payload += struct.pack(">H", seq_num)
        
    
    packet = make_control_packet(payload)
    remaining = missing_list[count:]
    
    return packet, remaining
    
def parse_missing_packet(payload):
    if payload is None or len(payload) < 2:
        return None
        
    if payload[0:1] != b"M":
        return None
        
    count = payload[1]
    
    expected_len = 2 + (count *2)
    
    if len(payload) < expected_len:
        return None
        
    missing = []
    idx = 2
    
    for _ in range(count):
        seq_num = struct.unpack(">H", payload[idx:idx+2])[0]
        missing.append(seq_num)
        idx += 2
    return missing


if __name__ == "__main__":
    test_file = "example.txt"

    if not os.path.exists(test_file):
        print("test file not found:", test_file)
    else:
        pieces = split_file_into_chunks(test_file)
        
        print("file:", test_file)
        print("chunk size:", CHUNK_SIZE)

        print("total chunks:", len(pieces))

        # printing the first few chunks for testing/seeing what it's doing
        for i in range(min(3, len(pieces))):
            print(f"chunk {i} length:", len(pieces[i]))
