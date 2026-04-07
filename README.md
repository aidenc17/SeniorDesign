# Death Star Vulnerability Detection & Secure Transmission System

**Spring 2026 Senior Design Project - Group 12**

A covert wireless communication system that autonomously identifies Death Star vulnerabilities from image datasets, transmits encrypted data via RF communication, and serves results through a secure web interface with multi-factor authentication.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [System Components](#system-components)
- [Design Constraints](#design-constraints)
- [Team](#team)
- [Documentation](#documentation)

---

## Overview

This project demonstrates a complete secure data exfiltration and distribution pipeline:

1. **Image Analysis**: Computer vision identifies vulnerability markers (red circles) in 100 provided images
2. **Encryption**: Detected images are encrypted using AES-256 and packaged into a secure archive
3. **RF Transmission**: Encrypted data is transmitted wirelessly via RFM69 radio modules (433 MHz)
4. **Reception & Decryption**: Receiving station validates and decrypts transmitted data
5. **Web Interface**: Authenticated users access vulnerability data through a locally-hosted website

### Key Features

- Computer vision-based vulnerability detection using OpenCV
- AES-128 encryption for data security
- Covert RF communication (no WiFi/Bluetooth/Ethernet on transmitter)
- Two-tier authentication system (public + restricted access)
- Complete pipeline orchestration via Bash script

---

## System Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  USB Drive      │      │   Raspberry Pi   │      │  RF Transmitter │
│  (100 images)   │─────▶│  • Detection     │─────▶│  (RFM69 915MHz) │
└─────────────────┘      │  • Encryption    │      └────────┬────────┘
                         │                  │               │
                         └──────────────────┘               │ Wireless
                                                             │ (5+ meters)
┌─────────────────┐      ┌──────────────────┐      ┌───────▼─────────┐
│  Web Browser    │      │   Local Server   │      │  RF Receiver    │
│  • Public View  │◀─────│  • Web Server    │◀─────│  (RFM69 915MHz) │
│  • Auth Access  │HTTP  │                  │      └─────────────────┘
└─────────────────┘      └──────────────────┘
```

---

## Project Structure

```
SeniorDesign/
├── image-detection/          # Computer vision module
│   ├── detection_script.py   # Red circle detection and image sorting
│   └── test_images/          # Sample dataset for testing
├── RF-sender/                # Transmission module (Raspberry Pi)
│   ├── sender.py             # Main RF transmission script
│   └── sender_eth.py         # Ethernet-based testing variant
├── RF-receiver/              # Reception module (Server)
│   ├── receiver.py           # Main RF reception script
│   └── receiver_eth.py       # Ethernet-based testing variant
├── rfm69_transfer/           # Shared RF utilities
│   └── shared/
│       ├── chunking.py       # Data chunking for transmission
│       └── checksum.py       # Data integrity verification
├── received_images/          # Decrypted images (populated by receiver)
├── website/                  # Web interface
│   ├── index.html            # Main webpage
│   ├── styles.css            # Star Wars themed styling
│   ├── script.js             # Dynamic content loading
│   ├── server.py             # Local HTTP server
│   └── images.json           # Image manifest (auto-generated)
├── run_pipeline.sh           # Master orchestration script
├── requirements.txt          # Python dependencies
└── docs/                     # Additional documentation
```

---

## Prerequisites

### Hardware

- **Raspberry Pi 4 Model B** (4GB RAM)
- **RFM69HCW Radio Modules** (2x, 915 MHz)
- **MicroSD Card** (64GB, Class 10)
- **USB Thumb Drive** (for image delivery)
- **PC/Laptop** (for receiver and web server)
- **Jumper wires and breadboard** (for circuit assembly)

### Software

- **Operating System**: Raspberry Pi OS (Debian-based) or macOS/Linux
- **Python**: 3.12 or higher
- **Virtual Environment**: Recommended for dependency isolation

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/aidenc17/SeniorDesign.git
cd SeniorDesign
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Running the Complete Pipeline

The system operates autonomously via a single orchestration script:

```bash
./run_pipeline.sh
```

This executes the following sequence:

1. Activates Python virtual environment
2. Runs image detection on USB-provided dataset
3. Creates encrypted archive of detected images
4. Initiates RF transmission to receiver
5. Generates image manifest for web interface
6. Outputs results to `pipeline.log`

### Manual Component Testing

**Image Detection Only:**
```bash
cd image-detection
python3 detection_script.py
```

**RF Transmission (Raspberry Pi):**
```bash
cd RF-sender
python3 sender.py
```

**RF Reception (Server):**
```bash
cd RF-receiver
python3 receiver.py
```

**Web Interface:**
```bash
cd website
python3 server.py
# Open browser to http://localhost:8000
```

---

## System Components

### Image Detection Module

- **Technology**: OpenCV, NumPy
- **Function**: Identifies images containing red circles using Hough Circle Transform and HSV color filtering
- **Input**: 100 PNG images (1024x1024 pixels) from USB drive
- **Output**: 10 detected vulnerability images in `detected_images/` folder

**Key Parameters** (adjustable in script):
- Saturation threshold: 150
- Circularity threshold: 0.75
- Minimum area: 200 pixels

### RF Transmission Module

- **Radio**: RFM69HCW (915 MHz, ISM band)
- **Protocol**: Custom packet-based with checksums
- **Range**: 5+ meters through obstacles (glass enclosure)
- **Data Rate**: Optimized for 600-second transmission window
- **Security**: Operates on encrypted data only

### Web Interface

- **Framework**: Vanilla JavaScript, HTML5, CSS3
- **Server**: Python `http.server` (development only)
- **Features**:
  - Dynamic image gallery (auto-loads from `received_images/`)
  - Embedded video content (public + authenticated)
  - Star Wars terminal aesthetic
  - Responsive design for mobile compatibility

**Authentication**: Two-factor system (Password + Personal Access Token) for restricted content access.

---

## Design Constraints

The following constraints shaped system design decisions:

| Constraint | Specification | Impact |
|------------|--------------|---------|
| **Budget** | ≤ $300 total cost | Selected cost-effective RFM69 modules over alternatives |
| **Time** | 600 seconds max transmission | Optimized chunking and data rate |
| **Distance** | ≥ 5 meters RF range | Tested transmission through glass enclosure |
| **Autonomy** | Zero user input after USB insertion | Fully scripted pipeline with error handling |
| **Security** | No WiFi/Bluetooth/Ethernet on transmitter | Covert RF-only communication |
| **Storage** | 64GB max on Raspberry Pi | Lightweight codebase and efficient image storage |

---

## Team

**Group 12 - Wright State University**

- **Aiden Cox** (CS) - Pipeline Integration / Automation / Circle Detection / Project Lead
- **Kristin** (CS) - Hardware Design & RF Protocol (Sending, Receiving, Encryption)
- **Annal** (EE) - Hardware Design & RF Circuits
- **Tom Pua** (IT) - System Testing
---


## License

This project is developed for educational purposes as part of Wright State University's Senior Design course. All rights reserved.

---

## Acknowledgments

- **Faculty**: Huge shout out to Billy Kelley, the EE lab manager for helping us through the process!
- **Wright State University**: Department of Computer Science and Engineering

**Project Completion**: Spring 2026
