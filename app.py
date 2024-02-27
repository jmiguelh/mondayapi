import streamlit as st
import pandas as pd
import plotly.express as px
import time
from monday import ultima_atualzacao, carregar
import models.painel as painel

SETOR = ["Todos", "Segurança", "Infra", "Sistemas"]

COLOR_DISCRETE_MAP = {"Segurança": "olive", "Infra": "orange", "Sistemas": "royalblue"}


def barra_lateral():
    with st.sidebar:
        st.image("img/lunelli_colorida.png", width=250)
        with st.expander(":pushpin: Filtos"):
            setor = st.selectbox("Setor:", SETOR)
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
        return setor


def colorir_linha(row):
    cor = [
        (
            "background-color: #f2f28d"
            if row["status_agrupado"] != "1- Baclog"
            and row["status_agrupado"] != "0 - Concluído"
            else (
                "background-color: lightgreen"
                if row["status_agrupado"] == "0 - Concluído"
                else ""
            )
        )
        for _ in row.index
    ]
    return cor


def monday():
    st.set_page_config(
        page_title="Lunelli - Portfólio – TI ",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="auto",
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
                footer {visibility: hidden;}
                #stDecoration {display:none;}
            </style>
        """,
        unsafe_allow_html=True,
    )

    setor = barra_lateral()
    ### Filtros ###
    df = painel.carregar_projetos()

    if setor != "Todos":
        df_filtrados = df[df.Setor == setor]
    else:
        df_filtrados = df
    df_filtrados = df_filtrados.sort_values(
        by=["Setor", "Evolução"],
        ascending=[True, False],
    )

    st.title("Portfólio – TI - 2024")

    tab1, tab2, tab3, tab4 = st.tabs(["Resumo", "Segurança", "Infra", "Sistemas"])

    ### Resumo ###
    with tab1:
        linha = st.container()
        a, b = linha.columns(2)
        a1, a2 = a.columns(2)
        a1.metric(label="Total de projetos", value=len(df))
        a2.metric(label="Projetos Concluídos", value=len(df.loc[df.Status == "Feito"]))

        a.write("Projetos PCR")
        a.dataframe(
            df.loc[df.PCR == "Sim"][["Projeto", "Setor", "Evolução"]],
            use_container_width=True,
            hide_index=True,
        )

        b.write("Projetos por Setor")
        fig = px.bar(
            df.groupby(["Setor"]).count().reset_index(),
            x="Projeto",
            y="Setor",
            color="Setor",
            text_auto=True,
            color_discrete_map=COLOR_DISCRETE_MAP,
            orientation="h",
        )
        fig.update_layout(
            legend=dict(
                orientation="h",
                entrywidth=70,
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            )
        )
        b.plotly_chart(fig, use_container_width=True)

        linha = st.container()
        a, b = linha.columns(2)
        a.write("Status dos Projetos")
        fig = px.pie(
            df.groupby(["Status"]).count().reset_index(),
            values="Projeto",
            names="Status",
            color="Status",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(
            legend=dict(
                orientation="h",
                entrywidth=70,
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            )
        )
        a.plotly_chart(fig, use_container_width=True)
        b.write("Projetos")
        b.dataframe(
            df_filtrados[["Projeto", "Setor", "Evolução", "Status"]],
            use_container_width=True,
            hide_index=True,
        )
    ### Prioridade ###
    with tab2:
        ...
    ### Dados ###
    with tab3:
        ...
    with tab4:
        ...


if __name__ == "__main__":
    monday()
