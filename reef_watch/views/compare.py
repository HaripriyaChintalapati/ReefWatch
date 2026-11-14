import pandas as pd
import streamlit as st
import giovanni as gv
from catalog import PRODUCTS, P, add


def render():
    st.title("🌍 Compare Reef Locations")
    st.caption("Pick two locations and the products you'd deploy. Indicators come from NASA Giovanni.")
    names = list(gv.LOCATIONS)
    c1, c2 = st.columns(2)
    a = c1.selectbox("Location A", names, index=0)
    b = c2.selectbox("Location B", names, index=1)
    chosen = st.multiselect("Products", [p["id"] for p in PRODUCTS], default=["station"],
                            format_func=lambda i: P[i]["name"])
    if a == b:
        st.warning("Choose two different locations.")
        st.stop()

    S = {l: gv.summary(l) for l in (a, b)}
    sc = {l: gv.pressures(S[l]) for l in (a, b)}
    if any(S[l][v]["source"] == "Placeholder" for l in (a, b) for v in gv.VARS):
        st.info("Showing placeholder series. Export Giovanni time series CSVs to "
                "`giovanni_data/<location-slug>__<var>.csv` (vars: sst, chl, aod, no2, co2, precip) for real data.")

    st.subheader("Climatic conditions (last 12 months vs 12 months in 2017)")
    for col, loc in zip(st.columns(2), (a, b)):
        with col, st.container(border=True):
            st.markdown(f"**{loc}**")
            m = st.columns(3)
            for i, (v, (label, unit, _)) in enumerate(gv.VARS.items()):
                m[i % 3].metric(label.split(" (")[0], f"{S[loc][v]['now']:.2f} {unit}",
                                f"{S[loc][v]['delta']:+.2f}", delta_color="inverse")

    var = st.selectbox("Trend", list(gv.VARS), format_func=lambda v: f"{gv.VARS[v][0]} ({gv.VARS[v][1]})")
    ts = pd.concat([gv.get_series(l, var)[0].set_index("date").value.rename(l) for l in (a, b)], axis=1)
    st.line_chart(ts)

    st.subheader("Factors driving reef pressure (carbon-footprint proxies)")
    st.bar_chart(pd.DataFrame(sc))
    st.caption("0–100 pressure scores scaled from Giovanni indicators: SST (heat), NO₂ (industry, shipping, power), "
               "aerosols (pollution), chlorophyll (runoff), CO₂. They are indicators, not an emissions inventory.")

    st.subheader("Suggestions to revert conditions")
    for col, loc in zip(st.columns(2), (a, b)):
        with col, st.container(border=True):
            st.markdown(f"**{loc}**")
            for s in gv.suggest(sc[loc]):
                st.markdown(f"**{s['title']}** · {s['factor']} ({s['score']}/100)")
                st.markdown("\n".join(f"- {x}" for x in s["actions"]))
                have = [P[i]["name"] for i in s["products"] if i in chosen]
                need = [P[i]["name"] for i in s["products"] if i not in chosen]
                if have:
                    st.success("Covered by: " + ", ".join(have))
                if need:
                    st.caption("Consider adding: " + ", ".join(need))

    cost = sum(P[i]["price"] for i in chosen) * 2
    st.markdown(f"**Kit for both sites: ${cost}**")
    if chosen and st.button("Add one set per site to cart"):
        for i in chosen:
            add(i, 2)
        st.success("Added. Open the Shop page to check out.")
