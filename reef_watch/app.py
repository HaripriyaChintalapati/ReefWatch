"""ReefWatch: eco-ocean Streamlit site.  Run: streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="ReefWatch", page_icon="🪸", layout="wide")
import theme
from catalog import cart
from views import compare, login, monitor, shop

S = st.session_state
theme.inject(login=not S.get("user"))
if not S.get("user"):
    login.render()
    st.stop()

pages = [
    st.Page(compare.render, title="Compare Reefs", icon="🌍", url_path="compare", default=True),
    st.Page(monitor.render, title="Reef Monitor", icon="🪸", url_path="monitor"),
    st.Page(shop.render, title="Shop", icon="🛒", url_path="shop"),
]
nav = st.navigation(pages)
with st.sidebar:
    st.caption(f"Signed in: {S.user}")
    st.caption(f"🛒 {sum(cart().values())} item(s) in cart")
    if st.button("Sign out"):
        S.clear()
        st.rerun()
nav.run()
