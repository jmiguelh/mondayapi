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


def primeira_linha():
    corpo = st.container()
    a, b, c = corpo.columns(3)

    total_cards = painel.total_cards()
    cards_aberto_ultimo_dia = painel.cards_aberto_ultimo_dia()
    cards_aberto_no_mes = painel.cards_aberto_no_mes()
    total_cards_concluidos = painel.total_cards_concluidos()
    cards_conluidos_ultimo_dia = painel.cards_conluidos_ultimo_dia()
    cards_concludos_no_mes = painel.cards_concludos_no_mes()
    dftipo = painel.total_cards_tipo()
    dftipo7 = painel.total_cards_tipo(30)

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(label="Total de cards abertos", value=total_cards)
    a2.metric(
        label="Total de cards concluídos",
        value=total_cards_concluidos,
        delta=total_cards - total_cards_concluidos,
    )

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Cards aberto ontem",
        value=cards_aberto_ultimo_dia,
    )
    a2.metric(
        label="Cards concluídos ontem",
        value=cards_conluidos_ultimo_dia,
        delta=cards_aberto_ultimo_dia - cards_conluidos_ultimo_dia,
    )

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(label="Cards abertos no mês", value=cards_aberto_no_mes)
    a2.metric(
        label="Cards concluídos no mês",
        value=cards_concludos_no_mes,
        delta=cards_aberto_no_mes - cards_concludos_no_mes,
    )

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Total de Cards Evolutivos",
        value=dftipo.loc["Evolutivo"],
        delta=int(dftipo.loc["Evolutivo"] - dftipo7.loc["Evolutivo"]),
    )
    a2.metric(
        label="Total de Cards Corretivos",
        value=dftipo.loc["Corretivo"],
        delta=int(dftipo.loc["Corretivo"] - dftipo7.loc["Corretivo"]),
    )

    b.write("Cards aberto por mês")
    fig = px.bar(
        painel.cards_por_mes(),
        x="Mês",
        y="Cards",
        color="Tipo",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Set1,
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

    fig = px.pie(
        painel.cards_por_setor(),
        values="Quantidade",
        names="Setor",
        color="Setor",
        color_discrete_map=COLOR_DISCRETE_MAP,
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
    c.write("Cards aberto por setor")
    c.plotly_chart(fig, use_container_width=True)


def segunda_linha():
    rodape = st.container()
    a, b, c = rodape.columns(3)

    a.write("% Apropriação por tipo")
    fig = px.bar(
        painel.apropriacao_por_tipo(),
        x=["Corretivo", "Evolutivo"],
        y="Mês",
        text_auto=True,
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Set1,
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

    b.write("Cards concluído por mês")

    fig = px.bar(
        painel.cards_concluido_por_mes(),
        x="Mês",
        y="Cards",
        color="Tipo",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Set1,
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

    c.write("Cards concluído no mês por setor")
    fig = px.pie(
        painel.cards_concluido_por_mes_setor(),
        values="Quantidade",
        names="Setor",
        color="Setor",
        color_discrete_map=COLOR_DISCRETE_MAP,
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
    c.plotly_chart(fig, use_container_width=True)


def terceira_linha():
    terceira = st.container()
    a, b = terceira.columns(2)

    a.write("Evolução dos cards")
    fig = px.area(
        painel.diario_por_status(),
        x="Data",
        y="Cards",
        color="Status",
        line_group="Status",
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

    b.write("% Apropriação por Setor")
    fig = px.bar(
        painel.apropriacao_por_pai(),
        x=["Comercial", "Têxtil", "CRL"],
        y="Mês",
        text_auto=True,
        orientation="h",
        color_discrete_map=COLOR_DISCRETE_MAP,
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


def quarta_linha():
    linha = st.container()
    a, b = linha.columns(2)

    df = painel.diario()
    df = df.groupby(["Status"]).sum()
    df7 = painel.diario(7)
    df7 = df7.groupby(["Status"]).sum()

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Total de cards no quadro",
        value=df.Quantidade.sum(),
        delta=(int(df.Quantidade.sum() - df7.Quantidade.sum())),
    )
    a.write("Total de cards por status")
    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Especificação",
        value=df.loc["1 - Especificação"].Quantidade.item(),
        delta=(
            df.loc["1 - Especificação"].Quantidade.item()
            - df7.loc["1 - Especificação"].Quantidade.item()
        ),
    )
    a2.metric(
        label="Desenvolvimento",
        value=df.loc["2 - Desenvolvimento"].Quantidade.item(),
        delta=(
            df.loc["2 - Desenvolvimento"].Quantidade.item()
            - df7.loc["2 - Desenvolvimento"].Quantidade.item()
        ),
    )

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Homologação",
        value=df.loc["3 - Homologação"].Quantidade.item(),
        delta=(
            df.loc["3 - Homologação"].Quantidade.item()
            - df7.loc["3 - Homologação"].Quantidade.item()
        ),
    )
    a2.metric(
        label="Produção",
        value=df.loc["4 - Produção"].Quantidade.item(),
        delta=(
            df.loc["4 - Produção"].Quantidade.item()
            - df7.loc["4 - Produção"].Quantidade.item()
        ),
    )

    df = painel.diario()
    b.write("Cards na esteira por tipo")
    fig = px.funnel(
        df.groupby(["Status", "Tipo"], as_index=False).sum(),
        x="Quantidade",
        y="Status",
        color="Tipo",
        color_discrete_sequence=px.colors.qualitative.Set1,
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
        df_cards_filtrados = df[df.pai == setor]
    else:
        df_cards_filtrados = df

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
        a.write("Status dos Projetos")
        a.plotly_chart(fig, use_container_width=True)

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
