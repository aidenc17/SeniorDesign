#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
import json

PORT = 8000
WEBSITE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔐 USERS DATABASE (expandable)
USERS = {
    "obiwan": {
        "password": "helloThere",
        "token": "kenobi123"
    },
    "anakin": {
        "password": "ilovePadme",
        "token": "vader999"
    },
    "yoda": {
        "password": "doOrDoNot",
        "token": "forceMaster"
    }
}

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
        if self.path == "/auth":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            data = json.loads(body)
            username = data.get("username")
            password = data.get("password")
            token = data.get("token")

            user = USERS.get(username)

            if user and user["password"] == password and user["token"] == token:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            else:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False}).encode())

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


def main():
    os.chdir(WEBSITE_DIR)
    
    print("=" * 60)
    print("Death Star Vulnerability Detection - Local Server")
    print("=" * 60)
    print(f"\nServer running at:")
    print(f"  → http://localhost:{PORT}")
    print("=" * 60)
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()