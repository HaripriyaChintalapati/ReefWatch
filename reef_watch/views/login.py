import streamlit as st
import auth


def render():
    S = st.session_state
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown('<div class="hero"><h1>🪸 ReefWatch</h1>'
                    '<p>Watch the reefs. Reverse the heat.<br>Satellite insight + in-water stations.</p></div>',
                    unsafe_allow_html=True)
        with st.container(border=True):
            t1, t2 = st.tabs(["Sign in", "Create account"])
            with t1, st.form("in"):
                e, p = st.text_input("Email"), st.text_input("Password", type="password")
                if st.form_submit_button("Dive in"):
                    if auth.verify(e, p):
                        S.user = e.strip().lower()
                        st.rerun()
                    st.error("Wrong email or password.")
            with t2, st.form("up"):
                e, p = st.text_input("Email", key="e2"), st.text_input("Password (8+ chars)", type="password", key="p2")
                if st.form_submit_button("Create account"):
                    err = auth.register(e, p)
                    if err:
                        st.error(err)
                    else:
                        S.user = e.strip().lower()
                        st.rerun()
            if st.button("Continue as guest"):
                S.user = "guest"
                st.rerun()
