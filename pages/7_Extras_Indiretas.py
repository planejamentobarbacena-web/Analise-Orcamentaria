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
# CONFIGURAÇÃO
# ==================================================
st.set_page_config(
    page_title="Repasse – Indireta",
    page_icon="🏛️",
    layout="wide"
)

st.header("🏛️ Repasse – Indireta")
st.caption("Repasses à Administração Indireta")

# ==================================================
# DADOS
# ==================================================
df = carregar_extras()

if df.empty:
    st.info("Nenhum repasse cadastrado.")
    st.stop()

# ==================================================
# FILTROS
# ==================================================
st.subheader("🎯 Filtros")

c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

ex_sel = c1.multiselect(
    "Exercício",
    sorted(df["Exercício"].unique()),
    default=sorted(df["Exercício"].unique())
)

credor_sel = c2.multiselect(
    "Credor",
    sorted(df["Credor"].unique()),
    default=sorted(df["Credor"].unique())
)

comp_sel = c3.multiselect(
    "Competência",
    ["Todos"] + MESES,
    default=["Todos"]
)

fonte_sel = c4.multiselect(
    "Fonte",
    ["Todos"] + sorted(df["Fonte"].unique()),
    default=["Todos"]
)

competencias = [c for c in comp_sel if c != "Todos"]

df_f = filtrar_extras(
    df,
    exercicios=ex_sel,
    credores=credor_sel,
    competencias=competencias
)

if "Todos" not in fonte_sel:
    df_f = df_f[df_f["Fonte"].isin(fonte_sel)]

# ==================================================
# PREPARAÇÃO DO GRÁFICO (CORREÇÃO DEFINITIVA)
# ==================================================
df_graf = (
    df_f
    .groupby(["Credor", "Exercício", "Competência"], as_index=False)
    .agg({"Repasse": "sum"})
)

# força categorias de meses
df_graf["Competência"] = pd.Categorical(
    df_graf["Competência"],
    categories=MESES,
    ordered=True
)

# 🔑 GARANTE TODOS OS MESES (ZERO PARA AUSENTES)
df_graf = (
    df_graf
    .set_index(["Credor", "Exercício", "Competência"])
    .unstack(fill_value=0)
    .stack()
    .reset_index()
)

# ==================================================
# GRÁFICO
# ==================================================
st.markdown("---")
st.subheader("📈 Evolução Mensal dos Repasses")

fig = px.bar(
    df_graf,
    x="Competência",
    y="Repasse",
    color="Exercício",
    facet_col="Credor",
    barmode="group",
    category_orders={"Competência": MESES},
    labels={
        "Competência": "Mês",
        "Repasse": "Valor (R$)",
        "Exercício": "Ano"
    }
)

fig.update_layout(
    height=520,
    yaxis_tickprefix="R$ ",
    yaxis_tickformat=",.0f",
    legend=dict(
        orientation="h",
        y=-0.30,
        x=0.5,
        xanchor="center"
    )
)

fig.for_each_annotation(
    lambda a: a.update(text=a.text.split("=")[-1])
)

st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TABELA
# ==================================================
st.markdown("---")
st.subheader("📋 Detalhamento dos Repasses")

df_tab = df_f.copy()

df_tab["Competência"] = pd.Categorical(
    df_tab["Competência"],
    categories=MESES,
    ordered=True
)

df_tab = df_tab.sort_values(
    ["Exercício", "Competência", "Credor"]
)

df_tab["Repasse"] = df_tab["Repasse"].apply(float_para_moeda)

st.dataframe(df_tab, use_container_width=True, hide_index=True)

# ==================================================
# DOWNLOAD
# ==================================================
st.markdown("---")

csv = df_tab.to_csv(index=False, sep=";", encoding="utf-8")
st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="repasse_indireta.csv",
    mime="text/csv"
)

st.caption("Repasse – Administração Indireta • Visualização confiável")
