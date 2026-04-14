#!/usr/bin/env python3
"""
Death Star Vulnerability Server - Flask Edition (Raspberry Pi)
Now with Email OTP 2FA
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
import os
import json
import re
import secrets
import time
import smtplib
import random
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
PORT        = int(os.environ.get("PORT", 8000))
BASE_DIR    = Path(__file__).parent.resolve()
IMAGES_DIR  = Path(os.environ.get("IMAGES_DIR", str((BASE_DIR / "../RF-receiver/received_images").resolve())))

TOKEN_EXPIRY = 300   # 5 minutes (session token)
OTP_EXPIRY   = 300   # 5 minutes (OTP code)

# ── Gmail SMTP Config ─────────────────────────────────────────────────────────
# Set these as environment variables on your Pi — don't hardcode them
# export GMAIL_USER="youremail@gmail.com"
# export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"   <-- Gmail App Password (not your real password)
GMAIL_USER     = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASSWORD", "")

# ── Users: email → password ───────────────────────────────────────────────────
# Email is the username. Each user's email is also where their OTP gets sent.
USERS = {
    "obiwan@wright.edu":  "obi1",
    "cox.17@wright.edu":  "password",
    "anna@wright.edu":    "12345",
    "kristin@wright.edu": "blueberry",
    "tom@wright.edu":     "banana",
}

ACTIVE_TOKENS: dict = {}   # username → {token, expires}
PENDING_OTPS:  dict = {}   # username → {otp, expires}

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


def send_otp_email(to_email: str, otp_code: str) -> bool:
    """Send a 6-digit OTP to the given email via Gmail SMTP. Returns True on success."""
    if not GMAIL_USER or not GMAIL_APP_PASS:
        print("[ERROR] GMAIL_USER or GMAIL_APP_PASSWORD env vars not set.")
        return False

    subject = "Death Star Access Code"
    body    = (
        f"Your one-time access code is:\n\n"
        f"    {otp_code}\n\n"
        f"This code expires in 5 minutes.\n"
        f"Do not share it with anyone.\n\n"
        f"— Death Star Security System"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"[OTP] Sent to {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send OTP email: {e}")
        return False


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


# ── Auth: Step 1 — username + password ───────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    """
    Step 1 of 2FA.
    Accepts email + password. If valid, generates an OTP and emails it.
    Does NOT return a session token yet — that only happens after OTP is verified.
    """
    data     = request.get_json(force=True)
    username = data.get("username", "").strip().lower()  # email address
    password = data.get("password", "")

    if USERS.get(username) != password:
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    # Generate 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    PENDING_OTPS[username] = {
        "otp":     otp_code,
        "expires": time.time() + OTP_EXPIRY,
    }

    # Send OTP to user's email (which IS their username)
    sent = send_otp_email(username, otp_code)
    if not sent:
        return jsonify({"success": False, "error": "Failed to send OTP email. Check server config."}), 500

    return jsonify({"success": True, "message": f"OTP sent to {username}"}), 200


# ── Auth: Step 2 — OTP verification ──────────────────────────────────────────
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    """
    Step 2 of 2FA.
    Accepts email + the OTP code. If valid, returns a session token.
    """
    data     = request.get_json(force=True)
    username = data.get("username", "").strip().lower()
    otp      = data.get("otp", "").strip()

    record = PENDING_OTPS.get(username)

    if not record:
        return jsonify({"success": False, "error": "No pending OTP for this user"}), 401

    if time.time() > record["expires"]:
        del PENDING_OTPS[username]
        return jsonify({"success": False, "error": "OTP expired. Please log in again."}), 401

    if record["otp"] != otp:
        return jsonify({"success": False, "error": "Invalid OTP"}), 401

    # OTP is valid — clean up and issue session token
    del PENDING_OTPS[username]

    token = secrets.token_hex(16)
    ACTIVE_TOKENS[username] = {
        "token":   token,
        "expires": time.time() + TOKEN_EXPIRY,
    }

    return jsonify({"success": True, "token": token}), 200


# ── Auth: Session token verification ─────────────────────────────────────────
@app.route("/verify", methods=["POST"])
def verify():
    """Verifies an active session token (used to protect image routes on the frontend)."""
    data     = request.get_json(force=True)
    username = data.get("username", "").strip().lower()
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

    if not GMAIL_USER or not GMAIL_APP_PASS:
        print("\n  [!] WARNING: GMAIL_USER or GMAIL_APP_PASSWORD not set.")
        print("      OTP emails will not send until these are configured.\n")

    print("=" * 60)
    print("  Death Star Secure Server  (Flask / Raspberry Pi)")
    print("=" * 60)
    print(f"\n  Local:   http://localhost:{PORT}")
    print(f"  Network: http://{local_ip}:{PORT}")
    print(f"  Images:  {IMAGES_DIR}")
    print(f"  Token expiry: {TOKEN_EXPIRY}s")
    print(f"  OTP expiry:   {OTP_EXPIRY}s")
    print(f"  OTP sender:   {GMAIL_USER or '(not configured)'}")
    print("\n  Tip: set env vars before running:")
    print("       export GMAIL_USER='you@gmail.com'")
    print("       export GMAIL_APP_PASSWORD='xxxx xxxx xxxx xxxx'")
    print("\nPress Ctrl+C to stop.")
    print("=" * 60)

    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)