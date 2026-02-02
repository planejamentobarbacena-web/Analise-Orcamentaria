import streamlit as st
import pandas as pd
import plotly.express as px

from utils.extras_loader import (
    carregar_extras,
    filtrar_extras,
    MESES
)

# ==================================================
# CONFIGURAÇÃO (PRIMEIRA CHAMADA STREAMLIT)
# ==================================================
st.set_page_config(
    page_title="Repasse – Indireta",
    page_icon="🏛️",
    layout="wide"
)

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
def float_para_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
# TÍTULO
# ==================================================
st.title("🏛️ Repasse – Indireta")
st.caption("Repasses à Administração Indireta (Despesa Extra)")

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

competencias_sel = col3.multiselect(
    "Competência",
    options=["Todos"] + MESES,
    default=["Todos"]
)

fontes_sel = col4.multiselect(
    "Fonte",
    options=["Todos"] + sorted(df["Fonte"].unique()),
    default=["Todos"]
)

# ==================================================
# APLICA FILTROS
# ==================================================
competencias = None if "Todos" in competencias_sel else competencias_sel
fontes = None if "Todos" in fontes_sel else fontes_sel

df_f = filtrar_extras(
    df,
    exercicios=ex_sel,
    credores=credor_sel,
    competencias=competencias,
    fontes=fontes
)

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
    st.stop()

# ==================================================
# GRÁFICO
# ==================================================
st.markdown("---")
st.subheader("📊 Evolução Mensal dos Repasses (R$ milhões)")

df_graf = (
    df_f
    .groupby(["Exercício", "Competência", "Credor"], as_index=False)
    ["Repasse"]
    .sum()
)

df_graf["Competência"] = df_graf["Competência"].str.upper().str.strip()
df_graf = df_graf[df_graf["Competência"].isin(MESES)]

df_graf["Competência"] = pd.Categorical(
    df_graf["Competência"],
    categories=MESES,
    ordered=True
)

df_graf["Exercício"] = df_graf["Exercício"].astype(str)
df_graf["Repasse_mi"] = df_graf["Repasse"] / 1_000_000

fig = px.bar(
    df_graf,
    x="Competência",
    y="Repasse_mi",
    color="Exercício",
    facet_col="Credor",
    barmode="group",
    labels={
        "Competência": "Mês",
        "Repasse_mi": "Repasse (R$ milhões)",
        "Exercício": "Exercício"
    },
    category_orders={"Competência": MESES},
    height=520
)

fig.for_each_annotation(
    lambda a: a.update(text=a.text.split("=")[-1])
)

st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TABELA DETALHADA
# ==================================================
st.markdown("---")
st.subheader("📋 Detalhamento dos Repasses")

df_tabela = df_f.copy()
df_tabela["Exercício"] = df_tabela["Exercício"].astype(str)
df_tabela["Repasse"] = df_tabela["Repasse"].apply(float_para_moeda)

df_tabela["Competência"] = pd.Categorical(
    df_tabela["Competência"].str.upper().str.strip(),
    categories=MESES,
    ordered=True
)

df_tabela = df_tabela.sort_values(
    ["Exercício", "Competência", "Credor"]
)

st.dataframe(df_tabela, use_container_width=True, hide_index=True)

