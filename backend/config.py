import os

DB_PATH    = os.environ.get("DB_PATH", "malware.db")

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
ALGORITHM  = "sha256"