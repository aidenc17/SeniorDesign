"""
Auto SFTP forwarder for images/videos placed in a specific subfolder.

Note to users:
Set WATCH_SUBDIR to the folder name you want to monitor.
Fill in the CONFIG values below, then run the script.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath
from threading import Event


def ensure_dependencies() -> None:
    """Ensure required packages are installed."""
    if getattr(sys, "frozen", False):
        return
    required = {
        "paramiko": "paramiko",
        "watchdog": "watchdog",
    }
    missing = [
        package
        for package, module in required.items()
        if importlib.util.find_spec(module) is None
    ]
    if not missing:
        return

    print("Missing dependencies: " + ", ".join(missing) + ". Installing now...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    except Exception as exc:
        print("Failed to install dependencies:", exc)
        sys.exit(1)


ensure_dependencies()

import importlib

paramiko = importlib.import_module("paramiko")


def load_watchdog_classes():
    events = importlib.import_module("watchdog.events")
    observers = importlib.import_module("watchdog.observers")
    return events.FileSystemEventHandler, observers.Observer


FileSystemEventHandler, Observer = load_watchdog_classes()

# ============================
# CONFIG (EDIT THESE VALUES)
# ============================
# AWS host or IP address
AWS_HOST = "18.224.219.3"

# SSH username for the AWS server
SSH_USER = "ubuntu"

# Path to PEM key. If blank, the script auto-detects a .pem in this folder.
# If relative, it's resolved from this script's folder.
PEM_PATH = ""

# Remote directory on the server where files should be uploaded
REMOTE_DIR = "/srv/media/private"

# Subfolder to watch for incoming images (relative to this script's directory)
WATCH_SUBDIR = "../RF-reciever"

# Allowed file extensions (images/videos only). Add/remove as needed.
ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".tiff",
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".webm",
    ".m4v",
}

# Files to always exclude from upload
EXCLUDE_NAMES = {
    "config.json",
    ".env",
    "transfer.log",
    ".json",
    ".txt",
    ".pem",
}

# Retry behavior when AWS is unreachable
RETRY_COUNT = 3
RETRY_DELAY_SECONDS = 5

# Debounce duplicate events (seconds)
DEBOUNCE_SECONDS = 1.0

# File stability checks (avoid uploading files still being written)
STABLE_CHECKS = 3
STABLE_DELAY_SECONDS = 1.0


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

SCRIPT_DIR = BASE_DIR
WATCH_DIR = BASE_DIR / WATCH_SUBDIR
LOG_FILE = BASE_DIR / "transfer.log"
EXIT_EVENT = Event()


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def resolve_pem_path() -> Path:
    if PEM_PATH.strip():
        pem = Path(PEM_PATH)
        if not pem.is_absolute():
            pem = BASE_DIR / pem
        if not pem.exists():
            raise FileNotFoundError(f"PEM key not found at: {pem}")
        return pem

    candidates = [
        path
        for path in BASE_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".pem"
    ]
    if not candidates:
        raise FileNotFoundError(
            "No .pem key found in script folder. Add your PEM file or set PEM_PATH."
        )
    if len(candidates) > 1:
        names = ", ".join(sorted(p.name for p in candidates))
        raise ValueError(
            "Multiple .pem files found. Set PEM_PATH to choose one: " + names
        )
    return candidates[0]


def validate_config() -> None:
    if not AWS_HOST.strip():
        raise ValueError("AWS_HOST is blank. Fill it in the config section.")
    if not REMOTE_DIR.strip():
        raise ValueError("REMOTE_DIR is blank. Fill it in the config section.")


def request_exit(reason: str, exc: Exception | None = None) -> None:
    if EXIT_EVENT.is_set():
        return
    if exc:
        logging.error("%s", reason, exc_info=True)
    else:
        logging.error("%s", reason)
    EXIT_EVENT.set()


def is_allowed_file(path: Path, exclude_names: set[str]) -> bool:
    if path.name in exclude_names:
        return False
    if path.name.startswith("."):
        return False
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def wait_for_stable_file(path: Path) -> bool:
    last_size = None
    for _ in range(STABLE_CHECKS):
        if not path.exists():
            return False
        try:
            size = path.stat().st_size
            with path.open("rb"):
                pass
        except OSError:
            size = None
        if size is not None and size == last_size:
            return True
        last_size = size
        time.sleep(STABLE_DELAY_SECONDS)
    return False


def cleanup_empty_dirs(base_dir: Path, target_dir: Path) -> None:
    if not target_dir.exists() or not target_dir.is_dir():
        return
    for root, dirs, _files in os.walk(target_dir, topdown=False):
        root_path = Path(root)
        if root_path == base_dir:
            continue
        try:
            if not any(root_path.iterdir()):
                root_path.rmdir()
        except OSError:
            pass


class SFTPUploader:
    def __init__(self, host: str, user: str, remote_dir: str, pem_path: Path):
        self.host = host
        self.user = user
        self.pem_path = pem_path
        self.remote_dir = remote_dir
        self.client = None
        self.sftp = None

    def connect(self) -> None:
        if self.client and self.sftp:
            return
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            self.host,
            username=self.user,
            key_filename=str(self.pem_path),
            allow_agent=True,
            look_for_keys=True,
            timeout=10,
        )
        self.client = client
        self.sftp = client.open_sftp()

    def close(self) -> None:
        try:
            if self.sftp:
                self.sftp.close()
        finally:
            if self.client:
                self.client.close()
        self.sftp = None
        self.client = None

    def ensure_remote_dir(self, remote_dir: PurePosixPath) -> None:
        if not self.sftp:
            raise RuntimeError("SFTP client not connected")
        parts = remote_dir.parts
        path = ""
        for part in parts:
            if part == "/":
                path = "/"
                continue
            if path in ("", "/"):
                path = f"/{part}" if path == "/" else part
            else:
                path = f"{path}/{part}"
            try:
                self.sftp.stat(path)
            except OSError:
                self.sftp.mkdir(path)

    def upload_and_verify(self, local_path: Path, relative_path: Path) -> None:
        if not self.sftp:
            raise RuntimeError("SFTP client not connected")

        remote_path = PurePosixPath(self.remote_dir) / relative_path.as_posix()
        self.ensure_remote_dir(remote_path.parent)
        self.sftp.put(str(local_path), str(remote_path))
        remote_stat = self.sftp.stat(str(remote_path))
        local_size = local_path.stat().st_size
        if remote_stat.st_size != local_size:
            raise IOError(
                f"Size mismatch after upload: local={local_size}, remote={remote_stat.st_size}"
            )


class IncomingHandler(FileSystemEventHandler):
    def __init__(self, uploader: SFTPUploader, pem_name: str = "") -> None:
        super().__init__()
        self.uploader = uploader
        self.last_seen: dict[str, float] = {}
        self.exclude_names = set(EXCLUDE_NAMES)
        self.exclude_names.add(Path(__file__).name)
        if pem_name:
            self.exclude_names.add(pem_name)

    def on_created(self, event) -> None:
        self._handle_event(event)

    def on_moved(self, event) -> None:
        if hasattr(event, "dest_path"):
            self._handle_path(Path(event.dest_path))
        else:
            self._handle_event(event)

    def on_modified(self, event) -> None:
        self._handle_event(event)

    def _handle_event(self, event) -> None:
        self._handle_path(Path(event.src_path))

    def _handle_path(self, path: Path) -> None:
        if EXIT_EVENT.is_set():
            return
        try:
            if path.is_dir():
                self._handle_directory(path)
            else:
                self._handle_file(path)
        except Exception as exc:
            request_exit("Fatal error during file handling", exc)

    def _handle_directory(self, directory: Path) -> None:
        if not directory.exists():
            return
        for file_path in directory.rglob("*"):
            if EXIT_EVENT.is_set():
                return
            if file_path.is_file():
                self._handle_file(file_path)
        cleanup_empty_dirs(WATCH_DIR, directory)

    def _handle_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            return
        key = str(file_path.resolve())
        now = time.time()
        last = self.last_seen.get(key, 0.0)
        if now - last < DEBOUNCE_SECONDS:
            return
        self.last_seen[key] = now

        if not is_allowed_file(file_path, self.exclude_names):
            return
        if not wait_for_stable_file(file_path):
            logging.info("File not stable yet, skipping: %s", file_path)
            return

        relative_path = file_path.relative_to(WATCH_DIR)
        self._upload_with_retries(file_path, relative_path)

    def _upload_with_retries(self, local_path: Path, relative_path: Path) -> None:
        for attempt in range(1, RETRY_COUNT + 1):
            if EXIT_EVENT.is_set():
                return
            try:
                self.uploader.connect()
                self.uploader.upload_and_verify(local_path, relative_path)
                # Delete the local file after successful upload
                local_path.unlink()
                logging.info("Uploaded and removed: %s", local_path)
                return
            except Exception as exc:
                self.uploader.close()
                if attempt < RETRY_COUNT:
                    logging.warning(
                        "Upload failed (attempt %s/%s): %s",
                        attempt,
                        RETRY_COUNT,
                        exc,
                    )
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    request_exit(
                        f"Upload failed after {RETRY_COUNT} attempts; exiting.",
                        exc,
                    )


def main() -> None:
    setup_logging()
    try:
        validate_config()
        pem_path = resolve_pem_path()
    except Exception as exc:
        request_exit("Configuration error", exc)
        return

    if not WATCH_DIR.exists():
        logging.info("Creating watch folder: %s", WATCH_DIR)
        WATCH_DIR.mkdir(parents=True, exist_ok=True)

    uploader = SFTPUploader(AWS_HOST, SSH_USER, REMOTE_DIR, pem_path)
    handler = IncomingHandler(uploader, pem_name=pem_path.name)

    observer = Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=False)
    observer.start()
    logging.info("Watching folder: %s", WATCH_DIR)

    try:
        while not EXIT_EVENT.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping due to keyboard interrupt")
    finally:
        observer.stop()
        observer.join()
        uploader.close()


if __name__ == "__main__":
    main()
