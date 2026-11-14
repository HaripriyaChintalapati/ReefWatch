"""Demo-grade local auth (salted PBKDF2 in users.json). Use a real IdP in production."""
import hashlib, hmac, json, os
from pathlib import Path

DB = Path("users.json")


def _h(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 120_000).hex()


def _load():
    return json.loads(DB.read_text()) if DB.exists() else {}


def register(email, pw):
    users = _load()
    email = email.strip().lower()
    if "@" not in email or len(pw) < 8:
        return "Enter a valid email and a password of 8+ characters."
    if email in users:
        return "Account already exists."
    salt = os.urandom(16)
    users[email] = {"salt": salt.hex(), "hash": _h(pw, salt)}
    DB.write_text(json.dumps(users))
    return None


def verify(email, pw):
    u = _load().get(email.strip().lower())
    return bool(u) and hmac.compare_digest(u["hash"], _h(pw, bytes.fromhex(u["salt"])))
