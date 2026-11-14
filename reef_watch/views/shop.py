import json, uuid
from pathlib import Path
import streamlit as st
from catalog import PRODUCTS, P, cart, add, total


def render():
    st.title("🛒 ReefWatch Shop")
    st.caption("Hardware and data plans to put a station on your reef.")
    cols = st.columns(2)
    for i, p in enumerate(PRODUCTS):
        with cols[i % 2], st.container(border=True):
            st.markdown(f'<div class="tile">{p["emoji"]}</div>', unsafe_allow_html=True)
            st.subheader(p["name"])
            st.write(p["desc"])
            st.markdown(f'<span class="price">${p["price"]}</span>', unsafe_allow_html=True)
            if st.button("Add to cart", key=f"add_{p['id']}"):
                add(p["id"])
                st.rerun()

    st.divider()
    st.subheader("Your cart")
    c = cart()
    if not c:
        st.info("Cart is empty.")
        return
    for pid, q in list(c.items()):
        a, b, d = st.columns([4, 1, 1])
        a.write(f"{P[pid]['emoji']} {P[pid]['name']}")
        b.write(f"×{q} · ${P[pid]['price'] * q}")
        if d.button("Remove", key=f"rm_{pid}"):
            del c[pid]
            st.rerun()
    st.markdown(f"**Total: ${total()}**")
    with st.form("checkout"):
        name, email, addr = st.text_input("Name"), st.text_input("Email"), st.text_area("Shipping address")
        if st.form_submit_button("Place order"):
            if not (name and email and addr):
                st.error("Please fill in all fields.")
            else:
                oid = uuid.uuid4().hex[:8].upper()
                f = Path("orders.json")
                orders = json.loads(f.read_text()) if f.exists() else []
                orders.append(dict(id=oid, name=name, email=email, address=addr, items=c, total=total()))
                f.write_text(json.dumps(orders))
                st.session_state.cart = {}
                st.success(f"Order {oid} placed. Payment is not wired up yet: connect Stripe Checkout here.")
