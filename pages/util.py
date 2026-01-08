import time

from models.db import ultima_atualzacao
from monday import carregar


def barra_lateral(st):
    with st.sidebar:
        st.image("img/lunelli_colorida.png", width=250)
        with st.expander(
            f":arrows_counterclockwise: Última atualização: {ultima_atualzacao()}"
        ):
            if st.button("Recarregar dados"):
                with st.spinner("Carregando..."):
                    carregar()
                st.success("Sucesso! Repocessando...")
                time.sleep(3)
                st.rerun()
        st.write("")
        st.write("")
        st.image("img/monday_logo.png", width=250)


def nome_pagina(st, nome, layout="wide", initial_sidebar_state="auto"):
    st.set_page_config(
        page_title=f"Lunelli - {nome}",
        page_icon="🧊",
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
    )
    ### Remover o botão Deploy
    st.markdown(
        """
            <style>
                .reportview-container {
                    margin-top: -2em;
                }
                #MainMenu {visibility: hidden;}
                .stDeployButton {display:none;}
                .stAppDeployButton {display:none;}
                footer {visibility: hidden;}
                #stDecoration {display:none;}
            </style>
        """,
        unsafe_allow_html=True,
    )


def menu(st):
    pages = [
        st.Page("pages/painel.py", title="Painel"),
        st.Page("pages/projetos.py", title="Meus projetos"),
    ]

    pg = st.navigation(pages)
    pg.run()
