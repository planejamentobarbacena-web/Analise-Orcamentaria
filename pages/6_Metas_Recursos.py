import streamlit as st
import pandas as pd

from utils_metas import (
    exercicios_metas,
    carregar_metas_recurso_multiplos_exercicios
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
    page_title="Metas por Fonte / Recurso",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Metas por Fonte / Recurso")

# =====================================================
# FORMATAÇÃO
# =====================================================
def fmt_moeda(valor):
    if pd.isna(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================
# CARGA COMPLETA
# =====================================================
anos = exercicios_metas()
df_full = carregar_metas_recurso_multiplos_exercicios(anos)

if df_full.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

# =====================================================
# FILTROS
# =====================================================
st.subheader("🎯 Filtros")

# Linha 1
col1, col2 = st.columns(2)
# Linha 2
col3, col4 = st.columns(2)

# -----------------------------------------------------
# Fonte / Recurso (Código)
# -----------------------------------------------------
mapa = (
    df_full[["Codigo", "Especificacao"]]
    .drop_duplicates()
    .sort_values("Codigo")
)

opcoes_recurso = (
    mapa["Codigo"] + " - " + mapa["Especificacao"]
).tolist()

recurso_sel = col1.selectbox(
    "Fonte / Recurso",
    ["Todos"] + opcoes_recurso,
    key="filtro_recurso"
)

df = df_full.copy()

if recurso_sel != "Todos":
    codigo_sel = recurso_sel.split(" - ")[0]
    df = df[df["Codigo"] == codigo_sel]

# -----------------------------------------------------
# Exercício (com preservação de estado)
# -----------------------------------------------------
anos_disp = sorted(df["Exercício"].unique())

if "filtro_exercicio_recurso" in st.session_state:
    valores_atuais = st.session_state["filtro_exercicio_recurso"]
    valores_validos = [
        v for v in valores_atuais
        if v == "Todos" or v in anos_disp
    ]
    if valores_validos:
        st.session_state["filtro_exercicio_recurso"] = valores_validos

sel_anos = col2.multiselect(
    "Exercício",
    ["Todos"] + anos_disp,
    default=["Todos"],
    key="filtro_exercicio_recurso"
)

if "Todos" not in sel_anos:
    df = df[df["Exercício"].isin(sel_anos)]

# -----------------------------------------------------
# Competência
# -----------------------------------------------------
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

comp_sel = col3.multiselect(
    "Competência",
    ["Todas"] + ordem_meses,
    default=["Todas"],
    key="filtro_competencia_recurso"
)

if "Todas" not in comp_sel:
    df = df[df["Competência"].isin(comp_sel)]

# -----------------------------------------------------
# Tipo de Valor
# -----------------------------------------------------
tipo_valor = col4.selectbox(
    "Tipo de Valor",
    ["Ambos", "Previsto", "Realizado"],
    key="filtro_tipo_valor_recurso"
)

if tipo_valor == "Previsto":
    colunas_valor = ["Previsto"]
elif tipo_valor == "Realizado":
    colunas_valor = ["Realizado"]
else:
    colunas_valor = ["Previsto", "Realizado"]

# =====================================================
# CONSOLIDAÇÃO
# =====================================================
df_base = (
    df
    .groupby(
        ["Exercício", "Codigo", "Especificacao", "Competência"],
        as_index=False
    )[colunas_valor]
    .sum()
)

# =====================================================
# SUBTOTAL
# =====================================================
st.markdown("---")
st.subheader("💰 Subtotal das Metas (filtros aplicados)")

cols = st.columns(len(colunas_valor))

for i, col in enumerate(colunas_valor):
    cols[i].metric(col, fmt_moeda(df_base[col].sum()))

# =====================================================
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Metas por Fonte – Visão Tabular")

tabela = (
    df_base
    .pivot_table(
        index=["Exercício", "Codigo", "Especificacao"],
        columns="Competência",
        values=colunas_valor,
        aggfunc="sum"
    )
)

tabela.columns = [f"{t} {m}" for t, m in tabela.columns]
tabela = tabela.reset_index()

colunas = ["Exercício", "Codigo", "Especificacao"]
for mes in ordem_meses:
    for tipo in colunas_valor:
        col = f"{tipo} {mes}"
        if col in tabela.columns:
            colunas.append(col)

tabela = tabela[colunas]

for col in tabela.columns:
    if col not in ["Exercício", "Codigo", "Especificacao"]:
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
    file_name="metas_por_fonte_competencia.csv",
    mime="text/csv"
)

st.caption("Metas por Fonte / Recurso • Visualização dinâmica e consistente")
