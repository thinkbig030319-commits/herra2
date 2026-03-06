import hashlib
import hmac
import base64
import json
import os
import time

from .config import SECRET_KEY
from .database import get_db

def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex() + ":" + key.hex()

def _verify_password(password: str, stored: str) -> bool:
    salt_hex, key_hex = stored.split(":", 1)
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(key.hex(), key_hex)

def create_token(data: dict, expires_in: int = 3600) -> str:
    payload = {**data, "exp": time.time() + expires_in}
    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).rstrip(b"=").decode()
    sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"

def verify_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 2:
        raise ValueError("Invalid token format")
    payload_b64, sig = parts
    expected = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Invalid token signature")
    padding = "=" * (-len(payload_b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
    if payload.get("exp", 0) < time.time():
        raise ValueError("Token expired")
    return payload

def register_user(username: str, password: str):
    hashed = _hash_password(password)
    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed),
        )

def login_user(username: str, password: str) -> str:
    with get_db() as conn:
        row = conn.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        ).fetchone()
    if not row or not _verify_password(password, row["password"]):
        raise ValueError("Invalid credentials")
    return create_token({"sub": username})