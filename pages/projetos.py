import streamlit as st

from pages.login import login


def projetos(st):
    st.stop()
    pass


if __name__ == "__main__":
    if "access_token" not in st.session_state:
        usuario = login()
        if usuario is not None:
            st.session_state["access_token"] = usuario
            st.rerun()
    else:
        st.write(f"olá, **{st.session_state['access_token']}**! :wave:")
        projetos(st)
