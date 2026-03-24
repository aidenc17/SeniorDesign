#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
import json
import secrets
import time

PORT = 8000
WEBSITE_DIR = os.path.dirname(os.path.abspath(__file__))

# USERS (no tokens stored here anymore)
USERS = {
    "obiwan": "obi1",
    "aiden": "password",
    "anna": "12345",
    "kristin": "blueberry",
    "tom": "banana",
   
}

# ACTIVE TOKENS (in-memory)
ACTIVE_TOKENS = {}
TOKEN_EXPIRY_SECONDS = 300  # 5 minutes


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEBSITE_DIR, **kwargs)

    def translate_path(self, path):
        if path.startswith("/received_images/"):
            rel_path = path.replace("/received_images/", "")
            return os.path.abspath(
                os.path.join(WEBSITE_DIR, "../received_images", rel_path)
            )
        return super().translate_path(path)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        # 🔐 STEP 1: LOGIN → GENERATE TOKEN
        if self.path == "/login":
            username = data.get("username")
            password = data.get("password")

            if USERS.get(username) == password:
                token = secrets.token_hex(16)

                ACTIVE_TOKENS[username] = {
                    "token": token,
                    "expires": time.time() + TOKEN_EXPIRY_SECONDS
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                self.wfile.write(json.dumps({
                    "success": True,
                    "token": token
                }).encode())
            else:
                self.send_response(401)
                self.end_headers()

        # 🔐 STEP 2: VERIFY TOKEN
        elif self.path == "/verify":
            username = data.get("username")
            token = data.get("token")

            record = ACTIVE_TOKENS.get(username)

            if record:
                if record["token"] == token and time.time() < record["expires"]:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode())
                    return

            self.send_response(401)
            self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


def main():
    os.chdir(WEBSITE_DIR)

    print("=" * 60)
    print("Death Star Secure Server")
    print("=" * 60)
    print(f"Server: http://localhost:{PORT}")
    print("Token expiry: 5 minutes")
    print("=" * 60)

    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()