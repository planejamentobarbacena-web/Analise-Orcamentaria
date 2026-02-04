import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

from utils_metas import (
    exercicios_metas,
    carregar_metas_multiplos_exercicios
)

# =====================================================
# SEGURANÇA
# =====================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado.")
    st.stop()

if st.session_state.get("perfil") not in ["administrador", "consulta"]:
    st.error("🚫 Perfil sem permissão.")
    st.stop()

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Metas de Receita",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Metas de Receita")

# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================
def fmt_moeda(valor):
    if pd.isna(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def normalizar_texto(txt):
    if pd.isna(txt):
        return ""
    return (
        unicodedata
        .normalize("NFKD", str(txt))
        .encode("ASCII", "ignore")
        .decode("utf-8")
        .lower()
        .strip()
    )

# =====================================================
# CARGA INICIAL (TODOS OS DADOS)
# =====================================================
exercicios = exercicios_metas()
df_full = carregar_metas_multiplos_exercicios(exercicios)

# coluna auxiliar para busca sem acento
df_full["Especificacao_norm"] = df_full["Especificação"].apply(normalizar_texto)

# =====================================================
# FILTROS
# =====================================================
st.subheader("🎯 Filtros")

col1, col2, col3 = st.columns(3)

# ---- Receita (PRIMEIRO)
receitas_norm = (
    df_full[["Especificação", "Especificacao_norm"]]
    .drop_duplicates()
    .sort_values("Especificação")
)

mapa_receitas = dict(
    zip(receitas_norm["Especificação"], receitas_norm["Especificacao_norm"])
)

receita_sel = col1.selectbox(
    "Receita",
    ["Todas"] + list(mapa_receitas.keys())
)

# ---- Aplica filtro de Receita
df = df_full.copy()

if receita_sel != "Todas":
    chave = mapa_receitas[receita_sel]
    df = df[df["Especificacao_norm"] == chave]

# ---- Exercício (DEPOIS da Receita)
anos_disponiveis = sorted(df["Exercício"].unique())

sel_exercicios = col2.multiselect(
    "Exercício",
    ["Todos"] + anos_disponiveis,
    default=["Todos"]
)

if "Todos" not in sel_exercicios:
    df = df[df["Exercício"].isin(sel_exercicios)]

# ---- Competência
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

competencias = ["Todas"] + ordem_meses
comp_sel = col3.multiselect(
    "Competência",
    competencias,
    default=["Todas"]
)

if "Todas" not in comp_sel:
    df = df[df["Competência"].isin(comp_sel)]

# =====================================================
# CONSOLIDAÇÃO FINAL
# =====================================================
df_base = (
    df
    .groupby(
        ["Exercício", "Especificação", "Competência"],
        as_index=False
    )[["Previsto", "Realizado"]]
    .sum()
)

subtotal = df_f["Previsto", "Realizado"].sum()

# ==================================================
# SUBTOTAL
# ==================================================
st.markdown("---")
st.subheader("💰 Subtotal dos Repasses (filtros aplicados)")

col1, col2 = st.columns(2)

col1.metric(
    "Previsto",
    float_para_moeda(subtotal)
)

col2.metric(
    "Realizado",
    f"{len(df_f):,}".replace(",", ".")
)

# =====================================================
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Metas de Receita – Visão Tabular")

tabela = (
    df
    .pivot_table(
        index=["Exercício", "Especificação"],
        columns="Competência",
        values=["Previsto", "Realizado"],
        aggfunc="sum"
    )
)

tabela.columns = [f"{t} {m}" for t, m in tabela.columns]
tabela = tabela.reset_index()

colunas_ordenadas = ["Exercício", "Especificação"]
for mes in ordem_meses:
    for tipo in ["Previsto", "Realizado"]:
        col = f"{tipo} {mes}"
        if col in tabela.columns:
            colunas_ordenadas.append(col)

tabela = tabela[colunas_ordenadas]

for col in tabela.columns:
    if col not in ["Exercício", "Especificação"]:
        tabela[col] = tabela[col].apply(fmt_moeda)

st.dataframe(tabela, use_container_width=True)

# =====================================================
# DOWNLOAD
# =====================================================
st.markdown("---")

csv = tabela.to_csv(index=False, sep=";", encoding="utf-8")
st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="metas_receita_competencia.csv",
    mime="text/csv"
)

st.caption("Metas de Receita • Filtro inteligente por receita e exercício")

