import streamlit as st
import plotly.express as px
import sys
import os

# Ajuste de caminho para importar utils1
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils1 import carregar_dados

st.set_page_config(
    page_title="Consulta de Repasses",
    layout="wide"
)

st.title("📊 Consulta de Repasses")

try:
    # Carrega dados
    dados = carregar_dados("data/extras")

    # Filtros
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

    # Aplica filtros
    filtrado = dados[
        (dados["Exercício"].isin(exercicio)) &
        (dados["Competência"].isin(competencia)) &
        (dados["Credor"].isin(credor)) &
        (dados["Fonte"].isin(fonte))
    ]

    # Mostrar tabela
    st.subheader("📋 Tabela")
    st.dataframe(filtrado, use_container_width=True)

    # Checagem rápida: valores de Repasse
    st.write("🔍 Valores de Repasse (pré-visualização)")
    st.write(filtrado[["Competência", "Repasse"]])

    # -----------------------------
    # Gráfico total por Competência
    # -----------------------------
    st.subheader("📈 Total de Repasse por Competência")

    # Forçar Repasse como float
    filtrado["Repasse"] = filtrado["Repasse"].astype(float)

    # Agrupar e ordenar Competência
    agrupado = filtrado.groupby("Competência", as_index=False).agg({"Repasse": "sum"})
    # Ordenar corretamente, convertendo Competência para números
    try:
        agrupado["Competência_ordem"] = agrupado["Competência"].str.replace(r"[^\d]", "", regex=True).astype(int)
        agrupado = agrupado.sort_values("Competência_ordem")
    except:
        agrupado = agrupado.sort_values("Competência")

    fig = px.bar(
        agrupado,
        x="Competência",
        y="Repasse",
        text=agrupado["Repasse"],
        labels={"Repasse": "R$"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Total geral
    total = filtrado["Repasse"].sum()
    st.metric(
        "💰 Total Geral",
        f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

except Exception as e:
    st.error("❌ Erro ao carregar os dados")
    st.exception(e)
