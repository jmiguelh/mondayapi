import streamlit as st

from paginas.login import login, logout
from paginas.util import barra_lateral, nome_pagina
from paginas.painel import monday
from paginas.projetos import projetos


def main(st):
    nome_pagina(
        st, "Lunelli - Portfólio TI", layout="wide", initial_sidebar_state="auto"
    )
    barra_lateral(st)
    pages = [
        st.Page(monday, title="Painel"),
        st.Page(projetos, title="Meus projetos"),
        st.Page(logout, title="Logout", icon=":material/logout:"),
    ]

    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    if "access_token" not in st.session_state:
        usuario = login()
        if usuario is not None:
            st.session_state["access_token"] = usuario
            st.rerun()
    else:
        # st.write(f"olá, **{st.session_state['access_token']}**! :wave:")
        main(st)
