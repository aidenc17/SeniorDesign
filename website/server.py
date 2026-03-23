#!/usr/bin/env python3
"""
Simple HTTP server for Death Star vulnerability website
Serves the website and received images locally
"""

import http.server
import socketserver
import os
import sys

PORT = 8000
WEBSITE_DIR = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve files from the website directory"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEBSITE_DIR, **kwargs)
    
    def end_headers(self):
        # add CORS headers to allow image loading
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # custom logging format
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


def main():
    # change to website directory
    os.chdir(WEBSITE_DIR)
    
    print("=" * 60)
    print("Death Star Vulnerability Detection - Local Server")
    print("=" * 60)
    print(f"\nServing from: {WEBSITE_DIR}")
    print(f"\nServer running at:")
    print(f"  → http://localhost:{PORT}")
    print(f"  → http://127.0.0.1:{PORT}")
    print(f"\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    # create server
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()