"""Minimal HTTP API server for VASP-TRACE AI module.

Pure Python standard library implementation using http.server.
Provides POST /ai/evaluate endpoint for frontend and service integration.
"""

import http.server
import json
import os
import sys
from typing import Any, Dict, Tuple

from .service import evaluate_risk


class AIRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler for VASP-TRACE AI endpoints."""

    server_version = "VASP-TRACE-AI/1.0"

    def _send_json_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Helper to send a JSON response with CORS headers."""
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:
        """Handle POST requests, specifically POST /ai/evaluate."""
        # Enforce route matching
        if self.path != "/ai/evaluate":
            self._send_json_response(404, {"error": "Route not found", "path": self.path})
            return

        # Read request body
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            self._send_json_response(400, {"error": "Invalid Content-Length header."})
            return

        if content_length <= 0:
            self._send_json_response(400, {"error": "Empty request body."})
            return

        body_bytes = self.rfile.read(content_length)

        # Parse JSON
        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json_response(400, {"error": f"Invalid JSON payload: {str(exc)}"})
            return

        if not isinstance(payload, dict):
            self._send_json_response(400, {"error": "Payload must be a JSON object."})
            return

        # Validate required fields
        if "graph_data" not in payload or "scoring_data" not in payload:
            self._send_json_response(
                400,
                {
                    "error": "Missing required fields. Both 'graph_data' and 'scoring_data' are required.",
                },
            )
            return

        graph_data = payload["graph_data"]
        scoring_data = payload["scoring_data"]

        if not isinstance(graph_data, dict) or not isinstance(scoring_data, dict):
            self._send_json_response(
                400,
                {
                    "error": "'graph_data' and 'scoring_data' must be JSON objects (dictionaries).",
                },
            )
            return

        # Execute evaluation
        try:
            result = evaluate_risk(graph_data=graph_data, scoring_data=scoring_data)
            self._send_json_response(200, result.to_dict())
        except Exception as exc:
            self._send_json_response(
                500,
                {"error": f"Internal server error during evaluation: {str(exc)}"},
            )

    def do_GET(self) -> None:
        """Handle GET requests (unsupported routes return 404)."""
        self._send_json_response(
            404,
            {
                "error": "Not Found",
                "message": f"Route GET {self.path} is not supported. Use POST /ai/evaluate.",
            },
        )

    def log_message(self, format: str, *args: Any) -> None:
        """Format server log messages cleanly."""
        sys.stderr.write(f"[AI-API] {self.address_string()} - {format % args}\n")


def create_server(host: str = "127.0.0.1", port: int = 8000) -> http.server.HTTPServer:
    """Instantiate the AI HTTP server."""
    return http.server.HTTPServer((host, port), AIRequestHandler)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the AI HTTP server until interrupted."""
    server = create_server(host=host, port=port)
    print(f"[AI-API] Server running at http://{host}:{port}/")
    print(f"[AI-API] Ready to accept POST requests at http://{host}:{port}/ai/evaluate")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[AI-API] Shutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "127.0.0.1")
    run_server(host=host, port=port)
