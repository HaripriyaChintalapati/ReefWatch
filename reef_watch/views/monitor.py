"""Reef Monitor page: worsening reef -> 3 similar candidates -> deploy -> satellite vs Pi."""
import pandas as pd
import streamlit as st
from data import load_reefs, find_similar
from station_client import fetch


@st.cache_data
def get_data():
    return load_reefs()


def render():
    reefs, series = get_data()
    S = st.session_state

    st.title("🪸 Reef Watch: satellite + in-situ station")

    with st.sidebar:
        st.header("Station connection")
        source = st.text_input("Pi URL or local folder", "http://raspberrypi.local:8000",
                               help="e.g. http://192.168.1.50:8000 or ./station_data")
        if st.button("Reset workflow"):
            S.clear()
            st.rerun()
        st.caption("Worsening = positive DHW slope with p < 0.05. "
                   "Candidates = most similar reefs with no significant trend.")

    # ---- Step 1: worsening reef -------------------------------------------------
    st.subheader("1. Select a reef with a worsening trend")
    worse = reefs[reefs.status == "worsening"].sort_values("p_value")
    target = st.selectbox(
        "Worsening reef", worse.reef_id,
        format_func=lambda r: f"{r}  (slope {worse.set_index('reef_id').loc[r, 'trend_slope']:+.3f} DHW/mo, "
                              f"p={worse.set_index('reef_id').loc[r, 'p_value']:.3f})",
        index=None, placeholder="Choose a reef...")
    if target is None:
        st.map(worse.rename(columns={"lat": "latitude", "lon": "longitude"}), size=2000)
        st.stop()
    if S.get("target") != target:
        S.target, S.site = target, None

    # ---- Step 2: similar non-significant candidates -----------------------------
    st.subheader("2. Three similar non-significant candidates")
    cands = find_similar(reefs, target, 3)
    show = cands[["reef_id", "name", "similarity_%", "sst_mean", "dhw_mean", "chlorophyll",
                  "turbidity", "depth_m", "p_value"]].round(3)
    c1, c2 = st.columns([3, 2])
    c1.dataframe(show, hide_index=True, use_container_width=True)
    pts = pd.concat([reefs[reefs.reef_id == target].assign(role="target"),
                     cands.assign(role="candidate")])
    c2.map(pts.rename(columns={"lat": "latitude", "lon": "longitude"}), size=3000)

    # ---- Step 3: deployment site ------------------------------------------------
    st.subheader("3. Choose a deployment site")
    site = st.radio("Deploy the Pi station at:", cands.reef_id, horizontal=True, index=None,
                    format_func=lambda r: f"{r} ({cands.set_index('reef_id').loc[r, 'similarity_%']}% similar)")
    if site is None:
        st.stop()
    S.site = site
    st.code(f"python station.py --reef-id {site} --interval 300 --port 8000", language="bash")
    st.caption("Run on the Pi (add --mock to test without a camera).")

    # ---- Step 4: side-by-side ---------------------------------------------------
    st.subheader(f"4. Satellite stats vs station data: {target} (worsening) vs {site} (deployed)")
    left, right = st.columns(2)

    with left:
        st.markdown("#### 🛰️ Satellite")
        metric = st.selectbox("Metric", ["dhw", "sst", "chlorophyll"])
        pivot = (series[series.reef_id.isin([target, site])]
                 .pivot(index="date", columns="reef_id", values=metric))
        st.line_chart(pivot)
        row = reefs.set_index("reef_id")
        cmp = row.loc[[target, site], ["sst_mean", "dhw_mean", "chlorophyll", "turbidity",
                                       "trend_slope", "p_value", "status"]].T
        st.dataframe(cmp, use_container_width=True)

    with right:
        st.markdown("#### 📷 Raspberry Pi station")
        if st.button("Refresh station"):
            st.cache_data.clear()
        imgs, logs, err = fetch(source)
        if err:
            st.warning(f"Station not reachable or no data yet: {err}")
        else:
            if imgs:
                cols = st.columns(3)
                for i, im in enumerate(imgs):
                    cols[i % 3].image(im, caption=im.split("/")[-1], use_container_width=True)
            if logs:
                ldf = pd.DataFrame(logs)
                if logs[0].get("reef_id") != site:
                    st.info(f"Station is logging reef {logs[0].get('reef_id')}, not {site}.")
                st.line_chart(ldf.set_index("ts")[["water_temp_c", "brightness"]].dropna(how="all"))
                st.dataframe(ldf, hide_index=True, use_container_width=True)
