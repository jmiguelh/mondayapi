from datetime import datetime
import pandas as pd
import streamlit as st

from paginas.login import login
from models.db import nome_usuario, mail_usuario
from models.projetos import carregar_projetos, carregar_comentarios, carregar_analistas
from monday import alterar_projeto, criar_comentario, carregar


opcoes_status = {
    "Em progresso": 0,
    "Parado": 1,
    "Feito": 2,
    "Em planejamento": 3,
    "Em validação": 4,
    "Não iniciado": 5,
    "Em análise": 6,
    "Atualizar projeto": 7,
    "Aguardando Aprovação": 8,
    "Cancelado": 9,
}


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

    if len(event.selection.rows) > 0:
        with st.container(border=True):
            linha = event.selection.rows
            st.write(f"Projeto: **{df.iloc[linha[0]]["Projeto"]}**")
            validacao_projeto(df.iloc[linha[0]])

            with st.form(f"form_{df.index[linha[0]]}", border=True):
                a, b, c = st.columns(3)
                evolucao = a.number_input(
                    "% Evolução:",
                    value=int(df.iloc[linha[0]]["% Evolução"]),
                    min_value=0,
                    max_value=100,
                    step=1,
                    format="%d",
                )
                status = b.selectbox(
                    "Status:",
                    opcoes_status,
                    index=opcoes_status[df.iloc[linha[0]]["Status"]],
                )
                data_fim = c.date_input(
                    "Data Final:",
                    value=(
                        df.iloc[linha[0]]["Data Final"]
                        if df.iloc[linha[0]]["Data Final"] is not None
                        else datetime.today()
                    ),
                )
                if "texto" not in st.session_state:
                    st.session_state.texto = ""
                texto = st.text_area(
                    "Comentário:",
                    value=st.session_state.texto,
                )
                submitted = st.form_submit_button("Enviar")

                if submitted:
                    if texto == "":
                        st.warning("O comentário deve ser preenchido!")
                    else:
                        nome = nome_usuario(
                            f"{st.session_state['access_token']}@lunelli.com.br"
                        )
                        texto = f"Autor: {nome}\nEvolução: {evolucao}%\nStatus: {status}\nData Final: {data_fim.strftime("%d/%m/%Y")}\nComentário: {texto}"
                        resultado = criar_comentario(df.index[linha[0]], texto)
                        if "errors" in resultado:
                            st.error(resultado)
                        else:
                            resultado = alterar_projeto(
                                df.index[linha[0]],
                                str(evolucao),
                                str(status),
                                data_fim.strftime("%Y-%m-%d"),
                            )
                            if "errors" in resultado:
                                st.error(resultado)
                            else:
                                carregar(True, False)
                                st.info("Salvo com sucesso!")
                                st.session_state.texto = ""

            # Comentários
            df_comentario = carregar_comentarios(df.index[linha[0]])
            for _, row in df_comentario.iterrows():
                comentario = st.chat_message("user")  # avatar=":material/3p:"
                comentario.write(f"**{row["Autor"]} - {row["Data"]}**")
                comentario.markdown(
                    row["Comentário"].replace("\n", "<br>"), unsafe_allow_html=True
                )


def validacao_projeto(df):
    if df["Status Agrupado"] not in ("Parado", "Concluído"):
        if df["Data Final"] is not None:
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
