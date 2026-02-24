# RFM69 File Transfer


## Environment 

- Ubuntu 24.04.3 LTS (WSL)
- Python: 3.10+ (tested w/ 3.12.3) (venv)

### Current Files

- `checksum.py`
    computes md5 checksum for a file to verify integrity.

- `sender.py`
    takes in folder to be checksummed and prepares it for transmission via chunked bytes.

- `receiver.py`
    takes transmitted folder, rebuilds it, checks against md5 checksum to verify all data matches.

- `chunking.py`
    splits folder into 60-byte chunks for transmission and writes to new folder.