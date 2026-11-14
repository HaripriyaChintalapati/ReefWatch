"""Reef data layer: synthetic satellite-style data, trend tests, similarity search.

Swap `load_reefs()` for a real loader (e.g. NOAA Coral Reef Watch DHW/SST
exports) that returns the same two DataFrames and nothing else changes.
"""
import numpy as np
import pandas as pd
from scipy import stats

FEATURES = ["sst_mean", "sst_var", "dhw_mean", "chlorophyll", "turbidity", "depth_m"]
ALPHA = 0.05


def load_reefs(n=40, months=60, seed=42):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2021-11-01", periods=months, freq="MS")
    t = np.arange(months)
    season = np.sin(2 * np.pi * t / 12)
    reefs, series = [], []
    for i in range(n):
        rid = f"R{i + 1:03d}"
        lat = rng.uniform(-23, -10)
        lon = rng.uniform(142, 153)
        depth = rng.uniform(3, 25)
        base_sst = rng.uniform(26, 29)
        chl = rng.uniform(0.2, 1.2)
        turb = rng.uniform(0.05, 0.6)
        slope = rng.choice([0.0, 0.0, 0.03, 0.06], p=[.35, .3, .2, .15])  # DHW/month
        sst = base_sst + 1.5 * season + 0.0025 * slope * 100 * t / months + rng.normal(0, .3, months)
        dhw = np.clip(1.2 + slope * t + 1.0 * season + rng.normal(0, 1.0, months), 0, None)
        chl_s = np.clip(chl + rng.normal(0, .08, months), 0.01, None)
        res = stats.linregress(t, dhw)
        reefs.append(dict(
            reef_id=rid, name=f"Reef {rid}", lat=lat, lon=lon, depth_m=depth,
            sst_mean=sst.mean(), sst_var=sst.var(), dhw_mean=dhw.mean(),
            chlorophyll=chl_s.mean(), turbidity=turb,
            trend_slope=res.slope, p_value=res.pvalue,
        ))
        series.append(pd.DataFrame(dict(reef_id=rid, date=dates, sst=sst, dhw=dhw, chlorophyll=chl_s)))
    reefs = pd.DataFrame(reefs)
    reefs["status"] = np.where(
        (reefs.trend_slope > 0) & (reefs.p_value < ALPHA), "worsening", "non-significant")
    return reefs, pd.concat(series, ignore_index=True)


def find_similar(reefs, target_id, k=3):
    """k nearest non-significant reefs to target, by z-scored environmental features."""
    z = (reefs[FEATURES] - reefs[FEATURES].mean()) / reefs[FEATURES].std(ddof=0)
    z.index = reefs.reef_id
    pool = reefs[reefs.status == "non-significant"].reef_id
    pool = pool[pool != target_id]
    dist = np.sqrt(((z.loc[pool] - z.loc[target_id]) ** 2).sum(axis=1)).nsmallest(k)
    out = reefs.set_index("reef_id").loc[dist.index].copy()
    out["distance"] = dist
    out["similarity_%"] = (100 / (1 + dist)).round(1)
    return out.reset_index()
