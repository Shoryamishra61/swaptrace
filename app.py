"""
SwapTrace — Vercel entrypoint.

Zero external dependencies (stdlib only) so Vercel never installs any
Python packages and the Lambda bundle stays under 10 MB.
The web/ directory contains the full static operations console; all HTML/CSS/JS
requests are rewritten to it via vercel.json.
"""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    """Minimal status handler for Vercel health checks."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "service": "SwapTrace Telemetry Attribution Pipeline",
                    "status": "OPERATIONAL",
                    "version": "1.0.0",
                },
                indent=2,
            ).encode("utf-8")
        )

    def log_message(self, *args):  # silence access logs
        pass
