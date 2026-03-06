import hashlib
import yara
import os

rules = yara.compile(filepath="rules/malware_rules.yar")

def calculate_sha256(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

def scan_with_yara(path):
    matches = rules.match(path)
    if matches:
        return ", ".join([m.rule for m in matches])
    return "Clean"