"""NASA Giovanni indicator layer.

Giovanni (giovanni.gsfc.nasa.gov) needs an Earthdata login, so this app reads CSVs you export:
  Time Series, Area-Averaged -> Download Data (CSV) -> giovanni_data/<slug>__<var>.csv
  e.g. giovanni_data/great-barrier-reef-au__sst.csv   (vars: sst chl aod no2 co2 precip)
Missing files fall back to clearly labelled placeholder series so the UI always works.
"""
import re, zlib
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path("giovanni_data")

# name: (lat, lon, sst, chl, aod, no2, precip_mm_day)
LOCATIONS = {
    "Great Barrier Reef, AU": (-18.3, 147.7, 27.2, 0.25, 0.08, 0.7, 4.5),
    "Coral Triangle, ID": (-2.5, 121.0, 29.0, 0.35, 0.25, 1.8, 7.0),
    "Red Sea, EG": (27.5, 34.0, 27.0, 0.20, 0.30, 2.5, 0.3),
    "Mesoamerican Reef, BZ": (17.3, -87.8, 27.8, 0.30, 0.15, 1.2, 3.5),
    "Maldives": (3.2, 73.2, 29.0, 0.22, 0.22, 1.0, 5.0),
    "Florida Keys, US": (24.6, -81.0, 27.3, 0.28, 0.14, 2.8, 3.8),
    "Hawaii, US": (20.8, -156.9, 25.9, 0.12, 0.10, 0.9, 2.5),
    "Fiji": (-17.7, 178.0, 27.6, 0.20, 0.07, 0.5, 6.0),
}
VARS = {
    "sst": ("Sea surface temperature", "°C", "MODIS-Aqua"),
    "chl": ("Chlorophyll-a (runoff proxy)", "mg/m³", "MODIS-Aqua"),
    "aod": ("Aerosol optical depth", "", "MODIS"),
    "no2": ("Tropospheric NO₂ (combustion)", "10¹⁵ mol/cm²", "OMI"),
    "co2": ("Mid-tropospheric CO₂", "ppm", "AIRS"),
    "precip": ("Precipitation", "mm/day", "GPM IMERG"),
}
BAD_WHEN_HIGH = True  # for every variable here, higher/rising = more pressure on reefs


def slug(loc):
    return re.sub(r"[^a-z0-9]+", "-", loc.lower()).strip("-")


def _synthetic(loc, var):
    lat, _, sst, chl, aod, no2, pr = LOCATIONS[loc]
    base = dict(sst=sst, chl=chl, aod=aod, no2=no2, precip=pr, co2=418.0)[var]
    rng = np.random.default_rng(zlib.crc32(f"{loc}{var}".encode()))
    d = pd.date_range("2017-01-01", periods=120, freq="MS")
    t = np.arange(120)
    ph = 2 * np.pi * t / 12
    if var == "sst":
        v = base + 1.4 * np.sin(ph - 1.6) * (1 if lat >= 0 else -1) + 0.035 * t / 12 + rng.normal(0, .25, 120)
    elif var == "co2":
        v = 405 + 0.19 * t + 2 * np.sin(ph) + rng.normal(0, .3, 120)
    else:
        trend = rng.uniform(-.004, .008)
        v = base * (1 + trend * t / 12 + .15 * np.sin(ph) + rng.normal(0, .06, 120))
    return pd.DataFrame({"date": d, "value": v})


def get_series(loc, var):
    f = DATA / f"{slug(loc)}__{var}.csv"
    if f.exists():
        df = pd.read_csv(f, comment="#").iloc[:, :2]
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"])
        return df.dropna(), "NASA Giovanni export"
    return _synthetic(loc, var), "Placeholder"


def summary(loc):
    out = {}
    for v in VARS:
        df, src = get_series(loc, v)
        now, then = df.value.tail(12).mean(), df.value.head(12).mean()
        out[v] = dict(now=now, delta=now - then, source=src)
    return out


def pressures(s):
    cl = lambda x: int(max(0, min(100, x)))
    return {
        "Ocean heat (SST)": cl((s["sst"]["now"] - 26) / 4 * 100),
        "Industry & combustion (NO₂)": cl(s["no2"]["now"] / 4 * 100),
        "Air pollution (aerosols)": cl(s["aod"]["now"] / 0.4 * 100),
        "Nutrient & land runoff (chl-a)": cl(s["chl"]["now"] / 0.8 * 100),
        "Atmospheric CO₂ / acidification": cl((s["co2"]["now"] - 400) / 40 * 100),
    }


RULES = {
    "Ocean heat (SST)": ("Reduce thermal stress",
        ["Set DHW bleaching alerts and monitor continuously", "Prioritise heat-tolerant coral nurseries and shading trials",
         "Back local renewable energy to cut long-run warming"], ["station", "probe"]),
    "Industry & combustion (NO₂)": ("Cut industrial & shipping emissions",
        ["Shore power and low-sulfur fuel at nearby ports", "Emission caps and scrubbers for coastal industry",
         "Track NO₂ trend to verify policy impact"], ["plan"]),
    "Air pollution (aerosols)": ("Clean up the air above the reef",
        ["End open burning of waste and crop residue", "Dust control on coastal construction and roads"], ["plan"]),
    "Nutrient & land runoff (chl-a)": ("Stop nutrients reaching the water",
        ["Riparian buffers and fertiliser management upstream", "Upgrade coastal wastewater treatment",
         "Use station camera turbidity trends to spot runoff events"], ["station", "solar"]),
    "Atmospheric CO₂ / acidification": ("Tackle CO₂ and ocean acidification",
        ["Restore mangroves and seagrass (blue carbon)", "Decarbonise local tourism and transport"], ["plan"]),
}


def suggest(scores, top=3):
    out = []
    for k, v in sorted(scores.items(), key=lambda kv: -kv[1])[:top]:
        title, acts, prods = RULES[k]
        out.append(dict(factor=k, score=v, title=title, actions=acts, products=prods))
    return out
