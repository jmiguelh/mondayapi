from datetime import datetime
import pandas as pd
import streamlit as st

from paginas.login import login
from models.db import nome_usuario, mail_usuario
from models.projetos import carregar_projetos, carregar_comentarios, carregar_analistas


def projetos():
    if st.session_state["access_token"] != "jose.h":
        mail = f"{st.session_state['access_token']}@lunelli.com.br"
        nome = nome_usuario(mail)
        st.header(f"Projetos de **{nome}**!")
    else:
        with st.expander(":mag: Filtros"):
            df_analista = carregar_analistas()
            todos = st.checkbox("Todos projetos", key="disabled", value=True)
            nome = st.selectbox(
                "Nome:", df_analista["Nome"], disabled=st.session_state.disabled
            )
            if not todos:
                mail = mail_usuario(nome if not todos else None)
                st.header(f"Projetos de **{nome}**!")
            else:
                mail = None

    with st.container():
        df = carregar_projetos(mail)
        df = df.sort_values(
            by=["% Evolução"],
            ascending=[False],
        )
        event = st.dataframe(
            df[
                [
                    "Projeto",
                    "Responsável",
                    "% Evolução",
                    "Status",
                    "Data Final",
                    "Data LB",
                    "Equipe",
                    "Comentários",
                ]
            ],
            width="stretch",
            hide_index=True,
            column_config={
                "Data Final": st.column_config.DateColumn(
                    format="DD/MM/YYYY",
                ),
                "Data LB": st.column_config.DateColumn(
                    format="DD/MM/YYYY",
                ),
                "Comentários": st.column_config.LinkColumn(display_text="➡️"),
                "% Evolução": st.column_config.ProgressColumn(
                    "% Evolução",
                    help="% Evolução",
                    format="%f",
                    min_value=0,
                    max_value=100,
                ),
            },
            on_select="rerun",
            selection_mode="single-row",
        )
    # Comentários
    if len(event.selection.rows) > 0:
        with st.container(border=True):
            linha = event.selection.rows
            st.write(f"Projeto: **{df.iloc[linha[0]]["Projeto"]}**")
            validacao_projeto(df.iloc[linha[0]])
            df_comentario = carregar_comentarios(df.index[linha[0]])
            for _, row in df_comentario.iterrows():
                comentario = st.chat_message(
                    "user",  # avatar=":material/3p:"
                )
                comentario.write(f"**{row["Autor"]} - {row["Data"]}**")
                comentario.write(row["Comentário"])


def validacao_projeto(df):
    if df["Status Agrupado"] not in ("Parado", "Concluído"):
        if df["Data Final"] < datetime.now():
            st.error("Projeto em atraso! Favor replanejar.", icon="⛔")

        elif pd.isnull(df["Data Final"]) and df["Status"] == "Em progresso":
            st.error("Projeto sem data final!", icon="⛔")

        if df["Data LB"] is None:
            st.warning("Projeto sem linha base!", icon="⚠️")

        if df["Equipe"] == "":
            st.warning("Projeto sem equipe definida!", icon="⚠️")

        dias = df["dias_sem_comentario"] if df["dias_sem_comentario"] is not None else 0
        if dias > 30:
            st.warning(
                f"Projeto com {int(df['dias_sem_comentario'])} dias sem cometário!",
                icon="⚠️",
            )


if __name__ == "__main__":
    if "access_token" not in st.session_state:
        usuario = login()
        if usuario is not None:
            st.session_state["access_token"] = usuario
            st.rerun()
    else:
        projetos()
