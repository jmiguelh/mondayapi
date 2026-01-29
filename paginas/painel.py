import streamlit as st
from streamlit_card import card

# import pandas as pd
import plotly.express as px
import random
import models.painel as painel
from paginas.login import login


COLOR_CARD1 = "#3FDDE8"
COLOR_CARD2 = "#3FE881"
COLOR_DISCRETE_MAP = {
    "Segurança": "#73681F",
    "Infra": "#731F51",
    "Sistemas": "#1F6D73",
    "PETI LUNELLI": "#79C2C8",
}
COLOR_STATUS = {
    "Parado": "#EB4444",
    "Execução": "#4452EB",
    "Não iniciado": "#EBC744",
    "Concluído": "#44EB74",
}
COLOR_MONDAY = {
    "Em progresso": "#9cd326",
    "Feito": "#00c875",
    "Parado": "#df2f4a",
    "Aguardando Aprovação": "#ffcb00",
    "Cancelado": "#e484bd",
    "Atualizar projeto": "#c4c4c4",
    "Em planejamento": "#579bfc",
    "Não iniciado": "#a9bee8",
    "Em análise": "#5559df",
}


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
    ### Filtros ###
    df = painel.carregar_projetos()

    st.title("Portfólio TI - 2026")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        [
            "Resumo",
            "COE",
            "BI",
            "Infra",
            "Segurança",
            "Sistemas",
            "PETI Lunelli",
            "Produtos Digitais",
        ]
    )

    ### Resumo ###
    with tab1:
        aba_resumo(df)

    ### COE ###
    with tab2:
        aba_coe()

    ### BI ###
    with tab3:
        setor = "BI"
        aba_setor(setor, df)

    ### Infra ###
    with tab4:
        setor = "Infra"
        aba_setor(setor, df)

    ### Segurança ###
    with tab5:
        setor = "Segurança"
        aba_setor(setor, df)

    ### Sistema ###
    with tab6:
        setor = "Sistemas"
        aba_setor(setor, df)

    ### PETI Lunelli ###
    with tab7:
        setor = "PETI LUNELLI"
        aba_setor(setor, df)

    ### Produtos Digitais###
    with tab8:
        setor = "Produtos Digitais"
        aba_setor(setor, df)


def aba_resumo(df):
    linha = st.container()
    a, b = linha.columns(2)
    a1, a2 = a.columns(2)
    with a1:
        card(
            title=str(len(df)),
            text="Total de projetos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": COLOR_CARD1,
                }
            },
            key=str(random.randint(1, 5000)),
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
            key=str(random.randint(1, 5000)),
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
    fig.update_layout(showlegend=False)

    b.plotly_chart(fig, width="stretch")

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
    a.plotly_chart(fig, width="stretch")

    b.write("Projetos PCR")
    b.dataframe(
        df.loc[df.PCR == "Sim"][["Projeto", "Setor", "% Evolução"]],
        width="stretch",
        hide_index=True,
    )


def aba_setor(setor, df):
    df_setor = df.loc[df.Setor == setor]
    linha = st.container()
    a, b = linha.columns(2)
    a1, a2 = a.columns(2)
    with a1:
        card(
            title=str(len(df_setor)),
            text="Total de projetos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": COLOR_CARD1,
                }
            },
            key=str(random.randint(1, 5000)),
        )
    with a2:
        card(
            title=str(len(df_setor.loc[df_setor.Status == "Feito"])),
            text="Projetos Concluídos",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": COLOR_CARD2,
                }
            },
            key=str(random.randint(1, 5000)),
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
    fig.update_layout(showlegend=False)

    b.plotly_chart(fig, width="stretch")

    st.write("Projetos")
    df_setor = df_setor.sort_values(
        by=["% Evolução"],
        ascending=[False],
    )
    st.dataframe(
        df_setor[
            [
                "Projeto",
                "Responsável",
                "% Evolução",
                "Status",
                "Comentários",
                "Diretor Responsável",
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
    )


def aba_coe():
    df_total = painel.carregar_robos()
    df = df_total.loc[df_total.Ano == 2025]
    linha = st.container()
    a, b = linha.columns(2)
    a1, a2 = a.columns(2)
    with a1:
        card(
            title=str(len(df)),
            text="Total de robôs",
            styles={
                "card": {
                    "width": "200px",
                    "height": "200px",
                    "background-color": "LightGreen",
                }
            },
            key=str(random.randint(1, 5000)),
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
            key=str(random.randint(1, 5000)),
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
    fig.update_layout(showlegend=False)

    b.plotly_chart(fig, width="stretch")

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
    a.plotly_chart(fig, width="stretch")


if __name__ == "__main__":
    if "access_token" not in st.session_state:
        usuario = login()
        if usuario is not None:
            st.session_state["access_token"] = usuario
            st.rerun()
        else:
            monday(st)
