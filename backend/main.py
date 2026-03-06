from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json
import os

from .database import init_db, get_db
from .auth import register_user, login_user
from .scan_engine import calculate_sha256, scan_with_yara
from .ai_engine import predict_malware
from .monitor import get_system_stats

HOST       = os.environ.get("HOST", "0.0.0.0")
PORT       = int(os.environ.get("PORT", 8000))
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _parse_multipart(headers, rfile) -> dict:
    content_type = headers.get("Content-Type", "")
    boundary = None
    for part in content_type.split(";"):
        part = part.strip()
        if part.startswith("boundary="):
            boundary = part[9:].strip('"')
    if not boundary:
        return {}

    length = int(headers.get("Content-Length", 0))
    body   = rfile.read(length)
    sep    = ("--" + boundary).encode()
    result = {}

    for chunk in body.split(sep)[1:-1]:
        if b"\r\n\r\n" not in chunk:
            continue
        header_raw, content = chunk.split(b"\r\n\r\n", 1)
        content = content.rstrip(b"\r\n")

        field_name = filename = None
        for line in header_raw.decode(errors="replace").splitlines():
            if "Content-Disposition" in line:
                for item in line.split(";"):
                    item = item.strip()
                    if item.startswith("name="):
                        field_name = item[5:].strip('"')
                    elif item.startswith("filename="):
                        filename = item[9:].strip('"')
        if field_name:
            result[field_name] = {"filename": filename, "content": content}

    return result

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def send_json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length))
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        if self.path == "/stats":
            # Replaces the socketio broadcast — clients poll this endpoint.
            self.send_json(200, get_system_stats())
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        routes = {
            "/register": self._register,
            "/login":    self._login,
            "/scan":     self._scan,
        }
        handler = routes.get(self.path)
        if not handler:
            self.send_json(404, {"error": "Not found"})
            return
        try:
            handler()
        except ValueError as exc:
            self.send_json(400, {"error": str(exc)})
        except Exception:
            self.send_json(500, {"error": "Internal server error"})

    def _register(self):
        data = self.read_json()
        register_user(data["username"], data["password"])
        self.send_json(200, {"message": "User registered"})

    def _login(self):
        data = self.read_json()
        token = login_user(data["username"], data["password"])
        self.send_json(200, {"access_token": token})

    def _scan(self):
        fields = _parse_multipart(self.headers, self.rfile)
        if "file" not in fields:
            raise ValueError("No file field in request")

        file_info = fields["file"]
        filename   = file_info["filename"] or "upload"
        content    = file_info["content"]

        upload_path = os.path.join(UPLOAD_DIR, filename)
        with open(upload_path, "wb") as f:
            f.write(content)

        sha256        = calculate_sha256(upload_path)
        yara_result   = scan_with_yara(upload_path)
        file_size     = os.path.getsize(upload_path)
        ai_prediction, confidence = predict_malware(file_size)
        threat        = "HIGH" if yara_result != "Clean" or ai_prediction == "Malicious" else "LOW"

        with get_db() as conn:
            conn.execute(
                """INSERT INTO scan_history
                   (filename, sha256, yara_result, ai_prediction, confidence, threat_level)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (filename, sha256, yara_result, ai_prediction, confidence, threat),
            )

        self.send_json(200, {
            "filename":      filename,
            "sha256":        sha256,
            "yara_result":   yara_result,
            "ai_prediction": ai_prediction,
            "confidence":    confidence,
            "threat_level":  threat,
        })

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    init_db()
    server = ThreadedHTTPServer((HOST, PORT), Handler)
    print(f"Listening on {HOST}:{PORT}")
    server.serve_forever()