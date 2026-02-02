import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

# ==================================================
# SEGURANÇA (mantida)
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
st.caption("Repasses à Administração Indireta (Despesa Extra)")

# ==================================================
# CONSTANTES
# ==================================================
MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "extras"

# ==================================================
# CARGA DOS DADOS (como antes)
# ==================================================
@st.cache_data
def carregar_extras():

    dfs = []

    for arq in DATA_DIR.glob("extras_*.csv"):
        df = pd.read_csv(arq, sep=";", encoding="utf-8", dtype=str)

        df["Exercício"] = df["Exercício"].astype(int)
        df["Competência"] = df["Competência"].str.upper().str.strip()

        # 🔧 CORREÇÃO MÍNIMA DO REPASSE (SEM QUEBRAR O RESTO)
        df["Repasse"] = (
            df["Repasse"]
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)

df = carregar_extras()

if df.empty:
    st.info("Nenhum repasse cadastrado.")
    st.stop()

# ==================================================
# FILTROS (MESMA ORDEM DE ANTES)
# ==================================================
st.subheader("🎯 Filtros")

col1, col2 = st.columns(2)

exercicios = sorted(df["Exercício"].unique())
ex_sel = col1.multiselect(
    "Exercício",
    exercicios,
    default=exercicios
)

credores = sorted(df["Credor"].unique())
credor_sel = col2.multiselect(
    "Credor",
    credores,
    default=credores
)

col3, col4 = st.columns(2)

comp_opcoes = ["Todos"] + MESES
comp_sel = col3.multiselect(
    "Competência",
    comp_opcoes,
    default=["Todos"]
)

fonte_opcoes = ["Todos"] + sorted(df["Fonte"].unique())
fonte_sel = col4.multiselect(
    "Fonte",
    fonte_opcoes,
    default=["Todos"]
)

# ==================================================
# FILTRAGEM (igual antes)
# ==================================================
df_f = df.copy()

df_f = df_f[df_f["Exercício"].isin(ex_sel)]
df_f = df_f[df_f["Credor"].isin(credor_sel)]

if "Todos" not in comp_sel:
    df_f = df_f[df_f["Competência"].isin(comp_sel)]

if "Todos" not in fonte_sel:
    df_f = df_f[df_f["Fonte"].isin(fonte_sel)]

# ==================================================
# GRÁFICO (MESMO PADRÃO ORIGINAL)
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
    legend_title_text="Exercício"
)

fig.for_each_annotation(
    lambda a: a.update(text=a.text.split("=")[-1])
)

st.plotly_chart(fig, use_container_width=True)

# ==================================================
# TABELA (COM ORDEM CORRETA)
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

df_tab["Repasse"] = df_tab["Repasse"].map(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

st.dataframe(df_tab, use_container_width=True, hide_index=True)

st.caption("Repasse – Administração Indireta • Visão de Consulta")
