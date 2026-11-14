# Reef Watch

Dual-system app: a **Streamlit dashboard** (`app.py`) and a **Raspberry Pi station** (`pi_station/station.py`).

## Workflow
1. Pick a reef with a worsening trend (positive DHW slope, p < 0.05).
2. App finds the 3 most similar *non-significant* reefs (z-scored SST, DHW, chlorophyll, turbidity, depth).
3. Choose the deployment site; the app prints the Pi command.
4. Side-by-side: satellite time series/stats vs Pi images, sensor chart and log table.

## Run
```bash
# dashboard (laptop/server)
pip install -r requirements.txt
streamlit run app.py

# Pi station (on the Pi: sudo apt install python3-picamera2; pip install pillow w1thermsensor)
cd pi_station && python station.py --reef-id R012 --interval 300
# desktop test without a camera
python station.py --reef-id R012 --interval 10 --mock
```
In the app sidebar set the station URL (`http://<pi-ip>:8000`) or a local `station_data` folder.

## Notes
- `data.py` uses synthetic data; replace `load_reefs()` with NOAA Coral Reef Watch exports
  (same two DataFrames returned: reef summary + monthly series).
- The Pi serves its folder over plain HTTP: keep it on a trusted network or put it behind a VPN/reverse proxy.

## v2: ReefWatch site
`streamlit run app.py` → login (vivid reef scene) → **Compare Reefs** (two locations + products, NASA Giovanni
indicators, pressure factors, suggestions) · **Reef Monitor** (worsening reef → candidates → Pi) · **Shop**.
- Giovanni: export area-averaged monthly CSVs to `giovanni_data/<slug>__<var>.csv` (see `giovanni.py`); placeholders are labelled.
- Auth is demo-grade (`users.json`); checkout writes `orders.json` and has no payment processor yet.
