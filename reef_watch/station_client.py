"""Reads Pi station output (captures/*.jpg + log.jsonl) over HTTP or from a local folder."""
import json
from pathlib import Path
import requests


def fetch(source: str, limit_images=6, limit_logs=50):
    """source = 'http://pi.local:8000' or a local directory path. Returns (images, logs)."""
    try:
        if source.startswith("http"):
            raw = requests.get(f"{source}/log.jsonl", timeout=5).text
            logs = [json.loads(l) for l in raw.splitlines() if l.strip()]
            imgs = [f"{source}/captures/{l['image']}" for l in logs if l.get("image")]
        else:
            root = Path(source)
            raw = (root / "log.jsonl").read_text()
            logs = [json.loads(l) for l in raw.splitlines() if l.strip()]
            imgs = [str(root / "captures" / l["image"]) for l in logs if l.get("image")]
    except Exception as e:  # station offline / no data yet
        return [], [], str(e)
    return imgs[-limit_images:][::-1], logs[-limit_logs:][::-1], None
