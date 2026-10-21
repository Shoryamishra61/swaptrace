"""Vercel Serverless Function entrypoint for SwapTrace Telemetry API.

Exposes both BaseHTTPRequestHandler (Vercel standard) and WSGI app callable.
Uses Python standard library with zero external runtime overhead.
"""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function HTTP Handler."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "s-maxage=60, stale-while-revalidate")
        self.end_headers()

        payload = {
            "service": "SwapTrace Telemetry Attribution Pipeline",
            "status": "OPERATIONAL",
            "version": "1.0.0",
            "owners": [
                "CHARGER_DOCK",
                "PACK",
                "CELL_CHEMISTRY",
                "ENVIRONMENT",
                "INSUFFICIENT_EVIDENCE",
            ],
            "benchmark_results": {
                "sessions_evaluated": 138,
                "faults_attributed": 91,
                "abstentions": 47,
                "precision": 0.953,
                "root_cause_accuracy": 0.967,
            },
            "console_endpoint": "/",
        }
        self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))


def app(environ, start_response):
    """WSGI callable fallback for Vercel Python runtime."""
    status = "200 OK"
    headers = [
        ("Content-type", "application/json"),
        ("Access-Control-Allow-Origin", "*"),
    ]
    start_response(status, headers)
    body = {
        "service": "SwapTrace Telemetry Attribution Pipeline",
        "status": "OPERATIONAL",
        "version": "1.0.0",
    }
    return [json.dumps(body).encode("utf-8")]
