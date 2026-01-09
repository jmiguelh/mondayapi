import streamlit as st

from paginas.login import login
from models.db import nome_usuario, mail_usuario
from models.projetos import carregar_projetos, carregar_comentarios, carregar_analistas


def projetos():
    if st.session_state["access_token"] != "jose.h":
        mail = f"{st.session_state['access_token']}@lunelli.com.br"
        nome = nome_usuario(mail)
    else:
        with st.expander(":mag: Filtros"):
            df_analista = carregar_analistas()
            nome = st.selectbox("Nome:", df_analista["Nome"])
            mail = mail_usuario(nome)

    with st.container():
        st.header(f"Projetos de **{nome}**!")
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
                    "Comentários",
                ]
            ],
            width="stretch",
            hide_index=True,
            column_config={
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
            df_comentario = carregar_comentarios(df.index[linha[0]])
            for index, row in df_comentario.iterrows():
                comentario = st.chat_message(
                    "user",  # avatar=":material/3p:"
                )
                comentario.write(f"**{row["Autor"]} - {row["Data"]}**")
                comentario.write(row["Comentário"])


if __name__ == "__main__":
    if "access_token" not in st.session_state:
        usuario = login()
        if usuario is not None:
            st.session_state["access_token"] = usuario
            st.rerun()
    else:
        projetos()
