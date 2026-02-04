import streamlit as st
import pandas as pd
import plotly.express as px

from utils_extras import (
    carregar_extras,
    filtrar_extras,
    float_para_moeda,
    MESES
)

# ==================================================
# SEGURANÇA
# ==================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado.")
    st.stop()

if st.session_state.get("perfil") not in ["administrador", "consulta"]:
    st.error("🚫 Perfil sem permissão.")
    st.stop()

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(
    page_title="Repasse – Indireta",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Repasse – Indireta")
st.caption("Repasses à Administração Indireta (Empenhos)")

# ==================================================
# CARGA DOS DADOS
# ==================================================
df = carregar_extras()

if df.empty:
    st.info("Nenhum repasse cadastrado.")
    st.stop()

# ==================================================
# FILTROS
# ==================================================
st.subheader("🎯 Filtros")

col1, col2, col3, col4 = st.columns(4)

# Exercício
exercicios = sorted(df["Exercício"].unique())
ex_sel = col1.multiselect(
    "Exercício",
    exercicios,
    default=exercicios
)

# Credor
credores = sorted(df["Credor"].unique())
credor_sel = col2.multiselect(
    "Credor",
    credores,
    default=credores
)

# Competência
comp_sel = col3.multiselect(
    "Competência",
    MESES,
    default=MESES
)

# Fonte
fontes = sorted(df["Fonte"].unique())
fonte_sel = col4.multiselect(
    "Fonte",
    fontes,
    default=fontes
)

df_f = filtrar_extras(
    df,
    exercicios=ex_sel,
    credores=credor_sel,
    competencias=comp_sel
)

if fonte_sel:
    df_f = df_f[df_f["Fonte"].isin(fonte_sel)]

# ==================================================
# INDICADORES
# ==================================================
st.markdown("---")
st.subheader("📌 Resumo")

colA, colB, colC = st.columns(3)

total_repasse = df_f["Repasse"].sum()
colA.metric("💰 Total de Repasses", float_para_moeda(total_repasse))
colB.metric("🏛️ Credores", df_f["Credor"].nunique())
colC.metric("📅 Registros", len(df_f))

# ==================================================
# GRÁFICO
# ==================================================
st.markdown("---")
st.subheader("📈 Evolução Mensal dos Repasses")

df_graf = (
    df_f
    .groupby(["Exercício", "Competência"], as_index=False)
    .agg({"Repasse": "sum"})
)

df_graf["Serie"] = df_graf["Exercício"].astype(str)

fig = px.bar(
    df_graf,
    x="Competência",
    y="Repasse",
    color="Serie",
    barmode="group",
    category_orders={"Competência": MESES},
    labels={
        "Repasse": "Valor (R$)",
        "Competência": "Mês",
        "Serie": "Exercício"
    },
    title="Repasses Mensais Consolidados"
)

fig.update_layout(
    height=450,
    yaxis_tickprefix="R$ ",
    yaxis_tickformat=",.0f",
    legend_title_text=""
)

st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TABELA DETALHADA
# ==================================================
st.markdown("---")
st.subheader("📋 Detalhamento dos Repasses")

df_tabela = df_f.copy()
df_tabela["Repasse"] = df_tabela["Repasse"].apply(float_para_moeda)

df_tabela = df_tabela.sort_values(
    ["Exercício", "Competência", "Credor"]
)

st.dataframe(
    df_tabela,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# DOWNLOAD
# ==================================================
st.markdown("---")

csv = df_tabela.to_csv(index=False, sep=";", encoding="utf-8")
st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="repasse_indireta.csv",
    mime="text/csv"
)

st.caption("Repasse – Administração Indireta • Visão de Consulta")
