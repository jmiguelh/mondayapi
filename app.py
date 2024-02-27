import streamlit as st
from streamlit_card import card
import pandas as pd
import plotly.express as px
import time
from monday import ultima_atualzacao, carregar
import models.painel as painel

COLOR_DISCRETE_MAP = {"Segurança": "olive", "Infra": "orange", "Sistemas": "royalblue"}


def barra_lateral():
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
        page_title="Lunelli - Portfólio TI ",
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

    barra_lateral()
    ### Filtros ###
    df = painel.carregar_projetos()

    st.title("Portfólio – TI - 2024")

    tab1, tab2, tab3, tab4 = st.tabs(["Resumo", "Segurança", "Infra", "Sistemas"])

    ### Resumo ###
    with tab1:
        linha = st.container()
        a, b = linha.columns(2)
        a1, a2 = a.columns(2)
        with a1:
            hasClicked = card(
                title=len(df),
                text="Total de projetos",
                styles={
                    "card": {
                        "width": "200px",
                        "height": "200px",
                        "background-color": "LightGreen",
                    }
                },
            )
        with a2:
            hasClicked = card(
                title=len(df.loc[df.Status == "Feito"]),
                text="Projetos Concluídos",
                styles={
                    "card": {
                        "width": "200px",
                        "height": "200px",
                        "background-color": "LightSalmon",
                    }
                },
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

        b.write("Projetos PCR")
        b.dataframe(
            df.loc[df.PCR == "Sim"][["Projeto", "Setor", "% Evolução"]],
            use_container_width=True,
            hide_index=True,
        )

    ### Segurança ###
    with tab2:
        setor = "Segurança"
        aba_setor(setor, df)

    ### Infra ###
    with tab3:
        setor = "Infra"
        aba_setor(setor, df)
    ### Sistema ###
    with tab4:
        setor = "Sistemas"
        aba_setor(setor, df)


def aba_setor(setor, df):
    df_setor = df.loc[df.Setor == setor]
    linha = st.container()
    a, b = linha.columns(2)
    a1, a2 = a.columns(2)
    with a1:
        hasClicked = card(
            title=len(df_setor),
            text="Total de projetos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": "LightGreen",
                }
            },
        )
    with a2:
        hasClicked = card(
            title=len(df_setor.loc[df_setor.Status == "Feito"]),
            text="Projetos Concluídos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": "LightSalmon",
                }
            },
        )

    b.write("Projetos por Status")
    fig = px.bar(
        df_setor.groupby(["Status"]).count().reset_index(),
        x="Projeto",
        y="Status",
        color="Status",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Set2,
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

    st.write("Projetos")
    df_setor = df_setor.sort_values(
        by=["% Evolução"],
        ascending=[False],
    )
    st.dataframe(
        df_setor[["Projeto", "% Evolução", "Status"]],
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    monday()
