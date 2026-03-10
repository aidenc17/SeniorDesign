## PC to AWS Script (Python)

### Overview
This script monitors a specific subfolder (`RF_receiver`) and  automatically uploads any new image or video files to an AWS server via SFTP. No manual file transfers needed — just drop files into the folder and the script handles the rest.

---

### Files Included
```
- auto_sftp_forwarder.py    (Python script)
- README.md
```

---

### How It Works

1. On startup, the script watches the `RF_receiver`   folder.
2. When an image or video file is placed inside `RF_receiver/`, the script detects it.
3. It waits for the file to finish writing, then uploads it via SFTP to the AWS server.
4. After a successful upload and size verification, the local file is deleted from `RF_receiver/`.
5. If the upload fails, it retries up to 3 times before stopping.
6. All activity is logged to `transfer.log` in the same directory.

**Supported file types:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.tiff`, `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.m4v`

---

### Setup Instructions

1. Ensure your SSH key is available via your system SSH agent or in `~/.ssh/`.

2. Run the script:
   - **Python:** Run `python auto_sftp_forwarder.py`
3. A terminal window will open and the script will begin watching `RF_receiver/`.
4. Drop any image or video files into the `RF_receiver/` folder — they will be uploaded automatically.
5. Files are uploaded to `/srv/media/private` on the AWS server (served by nginx to authenticated users).

---

### Configuration (advanced)
Open `auto_sftp_forwarder.py` and edit the `CONFIG` section at the top:

| Setting | Description |
|---|---|
| `AWS_HOST` | IP address or hostname of your AWS instance |
| `SSH_USER` | SSH username (default: `ubuntu`) |
| `REMOTE_DIR` | Remote path on the server to upload files into |
| `WATCH_SUBDIR` | Local subfolder to monitor (default: `RF_receiver`) |
| `ALLOWED_EXTENSIONS` | File types that will be uploaded |
| `EXCLUDE_NAMES` | Files that will always be skipped |

To use a PEM key file directly, uncomment `PEM_PATH` in the config and set it to your `.pem` file path, then uncomment the related lines in the script.

---

> **Note:** Don't forget to start   AWS instance before running the script.
