import streamlit as st
import plotly.express as px
from utils1 import carregar_dados

st.set_page_config(
    page_title="Consulta de Repasses",
    layout="wide"
)

st.title("📊 Consulta de Repasses")

try:
    dados = carregar_dados("dados")

    st.subheader("🔎 Filtros")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        exercicio = st.multiselect(
            "Exercício",
            sorted(dados["Exercício"].unique()),
            default=sorted(dados["Exercício"].unique())
        )

    with col2:
        competencia = st.multiselect(
            "Competência",
            sorted(dados["Competência"].unique()),
            default=sorted(dados["Competência"].unique())
        )

    with col3:
        credor = st.multiselect(
            "Credor",
            sorted(dados["Credor"].unique()),
            default=sorted(dados["Credor"].unique())
        )

    with col4:
        fonte = st.multiselect(
            "Fonte",
            sorted(dados["Fonte"].unique()),
            default=sorted(dados["Fonte"].unique())
        )

    filtrado = dados[
        (dados["Exercício"].isin(exercicio)) &
        (dados["Competência"].isin(competencia)) &
        (dados["Credor"].isin(credor)) &
        (dados["Fonte"].isin(fonte))
    ]

    st.subheader("📋 Tabela")
    st.dataframe(filtrado, use_container_width=True)

    st.subheader("📈 Total de Repasse por Competência")

    agrupado = (
        filtrado
        .groupby("Competência", as_index=False)["Repasse"]
        .sum()
    )

    fig = px.bar(
        agrupado,
        x="Competência",
        y="Repasse",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

    total = filtrado["Repasse"].sum()

    st.metric(
        "💰 Total Geral",
        f"R$ {total:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

except Exception as e:
    st.error("❌ Erro ao carregar os dados")
    st.exception(e)

