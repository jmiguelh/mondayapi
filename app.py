import streamlit as st
from streamlit_card import card

# import pandas as pd
import plotly.express as px
import time
import random
from monday import carregar
from models.db import ultima_atualzacao
import models.painel as painel

COLOR_CARD1 = "#3FDDE8"
COLOR_CARD2 = "#3FE881"
COLOR_DISCRETE_MAP = {
    "Segurança": "#44EB74",
    "Infra": "#EBC744",
    "Sistemas": "#4452EB",
    "PETI LUNELLI": "#EB4444",
}
COLOR_STATUS = {
    "Parado": "#EB1F13",
    "Execução": "#1613EB",
    "Não iniciado": "#EBC513",
    "Concluído": "#13EB68",
}


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

    st.title("Portfólio TI - 2025")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Resumo", "COE", "Infra", "Segurança", "Sistemas", "PETI Lunelli"]
    )

    ### Resumo ###
    with tab1:
        aba_resumo(df)

    ### COE ###
    with tab2:
        aba_coe()

    ### Infra ###
    with tab3:
        setor = "Infra"
        aba_setor(setor, df)

    ### Segurança ###
    with tab4:
        setor = "Segurança"
        aba_setor(setor, df)

    ### Sistema ###
    with tab5:
        setor = "Sistemas"
        aba_setor(setor, df)
    ### PETI Lunelli ###
    with tab6:
        setor = "PETI LUNELLI"
        aba_setor(setor, df)


def aba_resumo(df):
    linha = st.container()
    a, b = linha.columns(2)
    a1, a2 = a.columns(2)
    with a1:
        card(
            title=len(df),
            text="Total de projetos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": COLOR_CARD1,
                }
            },
            key=random.randint(1, 5000),
        )
    with a2:
        card(
            title=str(len(df.loc[df.Status == "Feito"])),
            text="Projetos Concluídos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": COLOR_CARD2,
                }
            },
            key=random.randint(1, 5000),
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
        df.groupby(["Status Agrupado"]).count().reset_index(),
        values="Projeto",
        names="Status Agrupado",
        color="Status Agrupado",
        color_discrete_map=COLOR_STATUS,
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


def aba_setor(setor, df):
    df_setor = df.loc[df.Setor == setor]
    linha = st.container()
    a, b = linha.columns(2)
    a1, a2 = a.columns(2)
    with a1:
        card(
            title=len(df_setor),
            text="Total de projetos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": COLOR_CARD1,
                }
            },
            key=random.randint(1, 5000),
        )
    with a2:
        card(
            title=len(df_setor.loc[df_setor.Status == "Feito"]),
            text="Projetos Concluídos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": COLOR_CARD2,
                }
            },
            key=random.randint(1, 5000),
        )

    b.write("Projetos por Status")
    fig = px.bar(
        df_setor.groupby(["Status Agrupado"]).count().reset_index(),
        x="Projeto",
        y="Status Agrupado",
        color="Status Agrupado",
        text_auto=True,
        color_discrete_map=COLOR_STATUS,
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
        df_setor[["Projeto", "Resposaveis", "% Evolução", "Status", "Comentários"]],
        use_container_width=True,
        hide_index=True,
        column_config={"Comentários": st.column_config.LinkColumn(display_text="➡️")},
    )


def aba_coe():
    df_total = painel.carregar_robos()
    df = df_total.loc[df_total.Ano == 2025]
    linha = st.container()
    a, b = linha.columns(2)
    a1, a2 = a.columns(2)
    with a1:
        card(
            title=len(df),
            text="Total de robôs",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": "LightGreen",
                }
            },
            key=random.randint(1, 5000),
        )
    with a2:
        card(
            title=str(
                round(
                    (df_total.loc[df_total.Status == "Feito"]["FTE/Horas Mês"].sum()), 2
                )
            ),
            text="Robôs Concluídos em FTE/Horas Mês",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": "LightSalmon",
                }
            },
            key=random.randint(1, 5000),
        )

    b.write("Robôs por Etapa")
    fig = px.bar(
        df.groupby(["Status"])
        .count()
        .reset_index()
        .sort_values(by="Robô", ascending=False),
        x="Robô",
        y="Status",
        color="Status",
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
    a.write("Status dos Robôs")
    fig = px.pie(
        df.groupby(["Status Agrupado"]).count().reset_index(),
        values="Robô",
        names="Status Agrupado",
        color="Status Agrupado",
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


if __name__ == "__main__":
    monday()
