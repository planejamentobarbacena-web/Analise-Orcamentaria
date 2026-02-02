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
st.caption("Repasses à Administração Indireta (Saída por Despesa Extra)")

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

col1, col2 = st.columns(2)

exercicios = sorted(df["Exercício"].unique())
ex_sel = col1.multiselect("Exercício", exercicios, default=exercicios)

credores = sorted(df["Credor"].unique())
credor_sel = col2.multiselect("Credor", credores, default=credores)

col3, col4 = st.columns(2)

comp_opcoes = ["Todos"] + MESES
comp_sel = col3.multiselect("Competência", comp_opcoes, default=["Todos"])

fonte_opcoes = ["Todos"] + sorted(df["Fonte"].unique())
fonte_sel = col4.multiselect("Fonte", fonte_opcoes, default=["Todos"])

# ==================================================
# FILTRAGEM
# ==================================================
competencias_filtrar = [c for c in comp_sel if c != "Todos"]

df_f = filtrar_extras(
    df,
    exercicios=ex_sel,
    credores=credor_sel,
    competencias=competencias_filtrar
)

if "Todos" not in fonte_sel:
    df_f = df_f[df_f["Fonte"].isin(fonte_sel)]

# 🔑 GARANTIA DE TIPO NUMÉRICO (CRÍTICO PARA O GRÁFICO)
df_f["Repasse"] = pd.to_numeric(df_f["Repasse"], errors="coerce").fillna(0)

# ==================================================
# GRÁFICO
# ==================================================
st.markdown("---")
st.subheader("📈 Evolução Mensal dos Repasses por Credor")

df_graf = (
    df_f
    .groupby(["Credor", "Competência", "Exercício"], as_index=False)
    .agg({"Repasse": "sum"})
)

df_graf["Competência"] = pd.Categorical(
    df_graf["Competência"],
    categories=MESES,
    ordered=True
)

df_graf["Exercício"] = df_graf["Exercício"].astype(str)

fig = px.bar(
    df_graf,
    x="Competência",
    y="Repasse",
    color="Exercício",
    facet_col="Credor",
    barmode="group",
    category_orders={
        "Competência": MESES,
        "Exercício": sorted(df_graf["Exercício"].unique())
    },
    labels={
        "Competência": "Mês",
        "Repasse": "Valor (R$)",
        "Exercício": "Ano"
    }
)

fig.update_layout(
    height=520,
    bargap=0.30,
    bargroupgap=0.08,
    yaxis_tickprefix="R$ ",
    yaxis_tickformat=",.0f",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.28,
        xanchor="center",
        x=0.5
    ),
    legend_title_text="Exercício"
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

df_tabela = df_f.copy()
df_tabela["Exercício"] = df_tabela["Exercício"].astype(str)
df_tabela["Repasse"] = df_tabela["Repasse"].apply(float_para_moeda)

df_tabela["Competência"] = pd.Categorical(
    df_tabela["Competência"],
    categories=MESES,
    ordered=True
)

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
