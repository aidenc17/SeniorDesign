# RFM69 File Transfer

## Environment 

- Ubuntu 24.04.3 LTS (WSL)
- Python: 3.10+ (tested w/ 3.12.3) (venv)

### Current Files

- `receiver.py`
    verifies start header from sender script matches. takes transmitted folder, rebuilds it, checks against md5 checksum to verify all data matches. 

- `receiver_eth.py`
    ethernet version of receiver script in case the radio version fails too close to demo time. has not been tested yet beyond sim.