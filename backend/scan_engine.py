import hashlib
import re

RULES: list[dict] = [
    {
        "name": "Suspicious_PowerShell",
        "any": [
            b"powershell -enc",
            b"powershell -encodedcommand",
            b"IEX(New-Object",
            b"Invoke-Expression",
            b"DownloadString(",
        ],
    },
    {
        "name": "PE_Executable",
        "strings": [b"MZ"],          # DOS header magic bytes
        "any": [b"PE\x00\x00"],      # PE signature
    },
    {
        "name": "Ransomware_Strings",
        "any": [
            b"YOUR FILES HAVE BEEN ENCRYPTED",
            b"send bitcoin",
            b"your personal id",
            b"decrypt your files",
            b".onion",
        ],
    },
    {
        "name": "Shellcode_Patterns",
        "any": [
            b"\x60\x89\xe5",         # pusha / mov ebp,esp prologue
            b"\xfc\xe8\x82\x00",     # common Metasploit stub
            b"VirtualAlloc",
            b"WriteProcessMemory",
            b"CreateRemoteThread",
        ],
    },
    {
        "name": "Suspicious_Script",
        "any": [
            b"eval(base64_decode",
            b"exec(base64.b64decode",
            b"<script>document.write(unescape(",
            b"fromCharCode(",
        ],
    },
    {
        "name": "Credential_Harvesting",
        "any": [
            b"password",
            b"passwd",
            b"credential",
            b"mimikatz",
            b"sekurlsa",
        ],
        "regex": [
            rb"(?i)(logon|login)\s*password",
        ],
    },
]

def _match_rule(data: bytes, rule: dict) -> bool:
    for pattern in rule.get("strings", []):
        if pattern not in data:
            return False

    any_patterns = rule.get("any", [])
    if any_patterns and not any(p in data for p in any_patterns):
        return False

    for pattern in rule.get("regex", []):
        if not re.search(pattern, data):
            return False

    return True


def scan_with_yara(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()

    matched = [rule["name"] for rule in RULES if _match_rule(data, rule)]
    return ", ".join(matched) if matched else "Clean"

def calculate_sha256(path: str) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()