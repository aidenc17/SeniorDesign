# RF-Sender


## Environment 

- Ubuntu 24.04.3 LTS (WSL)
- Python: 3.10+ (tested w/ 3.12.3) (venv)

### Current Files

- `sender.py`
    takes in folder to be checksummed and prepares it for transmission via chunked bytes. also creates a start header to send md5 checksum value ahead of file. sends bytes via adafruit's circuitpython send() function.

- `sender_eth.py`
    ethernet version of sender script in case the radio version fails too close to demo time. has not been tested yet beyond sim.
