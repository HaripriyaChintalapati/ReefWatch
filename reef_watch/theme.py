"""Eco-ocean look & feel: Earth + coral backdrop (subtle in-app, vivid on login)."""
import random, urllib.parse
import streamlit as st


def _url(svg):
    return 'url("data:image/svg+xml;utf8,' + urllib.parse.quote(svg) + '")'


def reef_svg(op, w=1600, h=420, seed=3):
    r = random.Random(seed)
    pal = ["#ff7a7a", "#ff9f6b", "#f7c8d8", "#2ee6c5", "#7be0ff", "#b69cff"]
    g = []
    for _ in range(34):
        x, c, hgt = r.uniform(0, w), r.choice(pal), r.uniform(60, 230)
        for _ in range(r.randint(3, 6)):
            x2, y2 = x + hgt * r.uniform(-.7, .7), h - hgt * r.uniform(.6, 1)
            xm = x + (x2 - x) * .4 + r.uniform(-20, 20)
            g.append(f'<path d="M{x:.0f} {h} Q{xm:.0f} {(h + y2) / 2:.0f} {x2:.0f} {y2:.0f}" '
                     f'stroke="{c}" stroke-width="{r.uniform(5, 12):.0f}" stroke-linecap="round" fill="none"/>')
            g.append(f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="{r.uniform(6, 12):.0f}" fill="{c}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
            f'<g opacity="{op}">{"".join(g)}</g></svg>')


def earth_svg(op):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><defs>'
            '<radialGradient id="o" cx=".35" cy=".3"><stop offset="0" stop-color="#4fd1ff"/>'
            '<stop offset="1" stop-color="#05406b"/></radialGradient></defs>'
            f'<g opacity="{op}"><circle cx="200" cy="200" r="190" fill="url(#o)"/>'
            '<g fill="#3ddc97"><path d="M90 120q40-40 90-20t30 60-60 30-60 50-40-40z"/>'
            '<path d="M230 220q50-20 80 20t-10 70-60 20-30-50z"/>'
            '<path d="M250 90q30-20 60 0t-10 40-50-10z"/></g></g></svg>')


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background:
  __REEF__ center bottom / 100% auto no-repeat fixed,
  __EARTH__ right -110px top 70px / 460px no-repeat fixed,
  linear-gradient(180deg, #041a2b 0%, #06324a 55%, #0a5a66 100%); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: rgba(4, 26, 43, .72); backdrop-filter: blur(10px); }
[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255,255,255,.06);
  backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,.14); border-radius: 18px; }
h1, h2, h3 { background: linear-gradient(90deg, #7be0ff, #2ee6c5); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; font-weight: 700; }
.stButton > button, .stFormSubmitButton > button { background: linear-gradient(90deg, #2ee6c5, #3ddc97);
  color: #032033; font-weight: 600; border: 0; border-radius: 999px; padding: .5rem 1.4rem; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(46,230,197,.35); }
.tile { font-size: 3rem; text-align: center; padding: 1rem; border-radius: 14px;
  background: linear-gradient(135deg, rgba(46,230,197,.25), rgba(123,224,255,.15)); }
.price { font-size: 1.4rem; font-weight: 700; color: #2ee6c5; }
.hero { text-align: center; margin: 4vh 0 1rem; }
.hero p { color: #bfeee8; font-size: 1.1rem; }
.bubble { position: fixed; bottom: -60px; border-radius: 50%; z-index: 0; pointer-events: none;
  border: 1px solid rgba(255,255,255,.5); background: rgba(255,255,255,.10);
  animation: rise linear infinite; }
@keyframes rise { to { transform: translateY(-115vh); opacity: 0; } }
</style>
"""


def inject(login=False):
    css = CSS.replace("__REEF__", _url(reef_svg(0.9 if login else 0.10)))
    css = css.replace("__EARTH__", _url(earth_svg(0.55 if login else 0.14)))
    st.markdown(css, unsafe_allow_html=True)
    if login:
        r = random.Random(7)
        st.markdown("".join(
            f'<div class="bubble" style="left:{r.randint(2, 96)}%;width:{(s := r.randint(8, 34))}px;'
            f'height:{s}px;animation-duration:{r.randint(9, 22)}s;animation-delay:-{r.randint(0, 20)}s"></div>'
            for _ in range(16)), unsafe_allow_html=True)
