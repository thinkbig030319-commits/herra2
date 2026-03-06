import sqlite3
import os
from contextlib import contextmanager

from .config import DB_PATH

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                filename      TEXT,
                sha256        TEXT,
                yara_result   TEXT,
                ai_prediction TEXT,
                confidence    REAL,
                threat_level  TEXT
            )
        """)

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()