#!/usr/bin/env python3
"""Local charting web app. Stdlib only, Python 3.9 compatible.

Run:   python3 app/server.py        then open http://127.0.0.1:8765
Stops with Ctrl+C. Binds 127.0.0.1 ONLY — never change this to 0.0.0.0 (PHI stays local).

Endpoints:
  GET  /                    -> app/index.html
  GET  /api/templates       -> {"templates": ["admission", ...]}
  POST /api/generate        -> body {"type": "...", "bullets": "..."} -> {"chart": "..."}
  POST /api/transcribe      -> raw audio bytes (webm/ogg/wav) -> {"text": "..."}
                               (converted with ffmpeg, transcribed with whisper-cli)
"""
import json
import os
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import chart  # noqa: E402  (scripts/chart.py)
from vocab_fix import apply_corrections  # noqa: E402

WHISPER_MODEL = os.path.join(ROOT, "models", "ggml-small.en.bin")
HOST, PORT = "127.0.0.1", 8765


def transcribe(audio_bytes):
    """audio bytes (any ffmpeg-readable container) -> corrected transcript text."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "in.audio")
        wav = os.path.join(td, "in.wav")
        with open(src, "wb") as f:
            f.write(audio_bytes)
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", src,
             "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav],
            check=True,
        )
        out = subprocess.run(
            ["whisper-cli", "-m", WHISPER_MODEL, "-f", wav, "--no-timestamps"],
            check=True, capture_output=True, text=True,
        ).stdout
    return apply_corrections(out.strip())


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "app", "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/templates":
            self._send(200, {"templates": chart.list_templates()})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            if self.path == "/api/generate":
                req = json.loads(body.decode("utf-8"))
                if not req.get("bullets", "").strip():
                    self._send(400, {"error": "empty input"})
                    return
                text = chart.generate(req["type"], req["bullets"])
                self._send(200, {"chart": text})
            elif self.path == "/api/transcribe":
                if not os.path.exists(WHISPER_MODEL):
                    self._send(500, {"error": "whisper model missing — see docs/SETUP.md step 3"})
                    return
                self._send(200, {"text": transcribe(body)})
            else:
                self._send(404, {"error": "not found"})
        except SystemExit as e:  # chart.py uses sys.exit for user-facing errors
            self._send(502, {"error": str(e)})
        except subprocess.CalledProcessError as e:
            self._send(500, {"error": "audio processing failed: %s" % e})
        except Exception as e:  # keep server alive; report the error to the page
            self._send(500, {"error": "%s: %s" % (type(e).__name__, e)})

    def log_message(self, fmt, *args):  # quieter logs
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    print("Charting app: http://%s:%d  (Ctrl+C to stop)" % (HOST, PORT))
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
