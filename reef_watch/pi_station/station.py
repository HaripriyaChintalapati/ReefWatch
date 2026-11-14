"""Raspberry Pi reef station: periodic capture + JSONL log + HTTP server.

  python station.py --reef-id R012 --interval 300 --port 8000 [--mock]

Writes ./station_data/captures/*.jpg and ./station_data/log.jsonl, and serves
station_data/ so the Streamlit app can read it at http://<pi>:8000.
Optional: wire a DS18B20 water probe (w1thermsensor) in read_water_temp().
"""
import argparse, json, random, threading, time
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

OUT = Path("station_data")


def make_camera(mock):
    if not mock:
        from picamera2 import Picamera2  # present on Raspberry Pi OS
        cam = Picamera2()
        cam.configure(cam.create_still_configuration())
        cam.start()
        time.sleep(2)
        return lambda path: cam.capture_file(str(path))

    def fake(path):  # placeholder frame for desktop testing
        img = Image.new("RGB", (640, 480), (0, random.randint(80, 160), random.randint(120, 200)))
        ImageDraw.Draw(img).text((10, 10), f"MOCK {datetime.now():%H:%M:%S}", fill="white")
        img.save(path)
    return fake


def cpu_temp():
    try:
        return round(int(Path("/sys/class/thermal/thermal_zone0/temp").read_text()) / 1000, 1)
    except Exception:
        return None


def read_water_temp(mock):
    if mock:
        return round(random.uniform(26, 31), 2)
    try:
        from w1thermsensor import W1ThermSensor
        return round(W1ThermSensor().get_temperature(), 2)
    except Exception:
        return None


def serve(port):
    handler = partial(SimpleHTTPRequestHandler, directory=str(OUT))
    ThreadingHTTPServer(("0.0.0.0", port), handler).serve_forever()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reef-id", required=True)
    ap.add_argument("--interval", type=int, default=300, help="seconds between captures")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()

    (OUT / "captures").mkdir(parents=True, exist_ok=True)
    (OUT / "log.jsonl").touch()
    threading.Thread(target=serve, args=(a.port,), daemon=True).start()
    capture = make_camera(a.mock)
    print(f"Station for {a.reef_id} serving on :{a.port}")

    while True:
        ts = datetime.now(timezone.utc)
        name = f"{a.reef_id}_{ts:%Y%m%dT%H%M%S}.jpg"
        entry = {"ts": ts.isoformat(timespec="seconds"), "reef_id": a.reef_id, "image": None,
                 "water_temp_c": read_water_temp(a.mock), "cpu_temp_c": cpu_temp(),
                 "brightness": None, "status": "ok"}
        try:
            capture(OUT / "captures" / name)
            entry["image"] = name
            entry["brightness"] = round(ImageStat.Stat(
                Image.open(OUT / "captures" / name).convert("L")).mean[0], 1)
        except Exception as e:
            entry["status"] = f"capture_error: {e}"
        with open(OUT / "log.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(entry)
        time.sleep(a.interval)


if __name__ == "__main__":
    main()
