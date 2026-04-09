#!/usr/bin/env python3
"""
Death Star Vulnerability Server - Flask Edition (Raspberry Pi)
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import json
import re
import secrets
import time
from pathlib import Path
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────────
PORT        = int(os.environ.get("PORT", 8000))
BASE_DIR    = Path(__file__).parent.resolve()
IMAGES_DIR  = Path(os.environ.get("IMAGES_DIR", str((BASE_DIR / "../RF-receiver/received_images").resolve())))

TOKEN_EXPIRY = 300  # 5 minutes

USERS = {
    "obiwan":  "obi1",
    "aiden":   "password",
    "anna":    "12345",
    "kristin": "blueberry",
    "tom":     "banana",
}

ACTIVE_TOKENS: dict = {}

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


# ── Helpers ───────────────────────────────────────────────────────────────────
def build_image_list() -> dict:
    images = []

    if not IMAGES_DIR.exists():
        print(f"[WARN] Images directory not found: {IMAGES_DIR}")
        return {"generated": datetime.now().isoformat(), "total_images": 0, "images": []}

    for file in sorted(IMAGES_DIR.iterdir()):
        if file.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue

        clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.name)
        if file.name != clean_name:
            file = file.rename(file.with_name(clean_name))

        stat = file.stat()
        images.append({
            "filename": file.name,
            "path":     f"/received_images/{file.name}",
            "size":     stat.st_size,
            "size_kb":  round(stat.st_size / 1024, 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })

    return {
        "generated":    datetime.now().isoformat(),
        "total_images": len(images),
        "images":       images,
    }


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_file(BASE_DIR / "index.html")

@app.route("/images.json")
def images_json():
    data = build_image_list()
    response = jsonify(data)
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/received_images/<path:filename>")
def serve_image(filename):
    return send_from_directory(str(IMAGES_DIR), filename)


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    data     = request.get_json(force=True)
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if USERS.get(username) == password:
        token = secrets.token_hex(16)
        ACTIVE_TOKENS[username] = {
            "token":   token,
            "expires": time.time() + TOKEN_EXPIRY,
        }
        return jsonify({"success": True, "token": token}), 200

    return jsonify({"success": False, "error": "Invalid credentials"}), 401


@app.route("/verify", methods=["POST"])
def verify():
    data     = request.get_json(force=True)
    username = data.get("username", "").strip()
    token    = data.get("token", "").strip()

    record = ACTIVE_TOKENS.get(username)
    if record and record["token"] == token and time.time() < record["expires"]:
        return jsonify({"success": True}), 200

    return jsonify({"success": False, "error": "Invalid or expired token"}), 401


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import socket

    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    local_ip = get_local_ip()

    print("=" * 60)
    print("  Death Star Secure Server  (Flask / Raspberry Pi)")
    print("=" * 60)
    print(f"\n  Local:   http://localhost:{PORT}")
    print(f"  Network: http://{local_ip}:{PORT}")
    print(f"  Images:  {IMAGES_DIR}")
    print(f"  Token expiry: {TOKEN_EXPIRY}s")
    print("\n  Tip: for production use, run with gunicorn:")
    print(f"       gunicorn -w 2 -b 0.0.0.0:{PORT} server:app")
    print("\nPress Ctrl+C to stop.")
    print("=" * 60)

    # Use threaded=True so the Pi handles concurrent requests without hanging
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)