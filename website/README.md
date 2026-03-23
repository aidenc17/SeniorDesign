# Death Star Vulnerability Website

This project hosts a local website to view images in the `received_images` folder. It includes:

1. A script to generate an `images.json` file listing all PNG images.
2. A Python HTTP server to serve the website and images locally.

---

## Prerequisites

- Python 3.x installed
- `received_images` folder located in the parent directory of the website/server scripts
- Browser (Chrome, Firefox, etc.)

---

## Files Overview

- **`generate_images.py`**  
  Scans `../received_images` and generates `images.json` with metadata for all PNG images. Filenames are sanitized automatically.

- **`server.py`**  
  Runs a local HTTP server:  
  - Serves website files and `received_images`  
  - Maps `/received_images/*` URLs to the correct folder  
  - Adds CORS headers for smooth image loading  
  - Prevents caching

---

## Quick Start

### 1. Generate the image list

Run this command to create `images.json`:

```bash
python3 generate_images.py
```

### 2. Start the server (locally of course)

```bash
python3 server.py
```

- Click the browser link in your terminal 
- Always run generate images first, then the server. 