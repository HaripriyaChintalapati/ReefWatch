import streamlit as st

PRODUCTS = [
    dict(id="station", emoji="📷", name="ReefCam Station (Pi 5 kit)", price=249,
         desc="Waterproof housing, Raspberry Pi 5, camera and 128 GB storage. Runs station.py out of the box."),
    dict(id="probe", emoji="🌡️", name="Marine Temp Probe", price=39,
         desc="DS18B20 marine-grade probe, 5 m cable. Feeds water temperature into the station log."),
    dict(id="solar", emoji="☀️", name="Solar Power Pack", price=119,
         desc="20 W panel + 20 Ah battery for off-grid buoys and shore mounts."),
    dict(id="plan", emoji="🛰️", name="Giovanni Insights Plan", price=9,
         desc="Monthly satellite refresh and reef action report for two locations (per month)."),
]
P = {p["id"]: p for p in PRODUCTS}


def cart():
    return st.session_state.setdefault("cart", {})


def add(pid, qty=1):
    c = cart()
    c[pid] = c.get(pid, 0) + qty


def total():
    return sum(P[i]["price"] * q for i, q in cart().items())
