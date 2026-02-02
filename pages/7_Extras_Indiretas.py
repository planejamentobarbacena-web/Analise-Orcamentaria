import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import re

st.set_page_config(page_title="Repasses Extras", layout="wide")
st.title("💰 Repasses Extras – Indiretas")

# -------------------------
# CONSTANTES
# -------------------------
MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "extras"

# -------------------------
# EXERCÍCIOS DISPONÍVEIS
# -------------------------
arquivos = list(DATA_DIR.glob("extras_*.csv"))

if not arquivos:
    st.error("Nenhum arquivo extras_ano.csv encontrado em data/extras/")
    st.stop()

anos_disponiveis = sorted(
    int(re.search(r"extras_(\d{4})", arq.name).group(1))
    for arq in arquivos
)

# -------------------------
# LEITURA DO CSV
# -------------------------
@st.cache_data
def carregar_dados(exercicio: int):

    caminho = DATA_DIR / f"extras_{exercicio}.csv"

    if not caminho.exists():
        st.error(f"Arquivo não encontrado: {caminho}")
        st.stop()

    df = pd.read_csv(caminho, sep=";", encoding="utf-8")
    df.columns = df.columns.str.strip()

    df["Exercício"] = df["Exercício"].astype(int)

    df["Repasse"] = (
        df["Repasse"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    df["Competência"] = pd.Categorical(
        df["Competência"],
        categories=MESES,
        ordered=True
    )

    return df

# -------------------------
# FILTROS
# -------------------------
st.sidebar.header("🔎 Filtros")

exercicio = st.sidebar.selectbox(
    "Exercício",
    anos_disponiveis,
    index=len(anos_disponiveis) - 1
)

df = carregar_dados(exercicio)

credor_sel = st.sidebar.multiselect(
    "Credor",
    sorted(df["Credor"].unique()),
    default=sorted(df["Credor"].unique())
)

fonte_sel = st.sidebar.multiselect(
    "Fonte",
    sorted(df["Fonte"].unique()),
    default=sorted(df["Fonte"].unique())
)

df_f = df[
    (df["Credor"].isin(credor_sel)) &
    (df["Fonte"].isin(fonte_sel))
]

# -------------------------
# INDICADORES
# -------------------------
st.subheader("📊 Resumo")

c1, c2 = st.columns(2)

c1.metric("Registros", len(df_f))

total = df_f["Repasse"].sum()
c2.metric(
    "Total Repassado",
    f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# -------------------------
# GRÁFICO
# -------------------------
st.subheader("📈 Repasses por Competência")

df_graf = (
    df_f
    .groupby(["Competência", "Credor"], as_index=False)["Repasse"]
    .sum()
    .sort_values("Competência")
)

fig = px.bar(
    df_graf,
    x="Competência",
    y="Repasse",
    color="Credor",
    barmode="group",
    category_orders={"Competência": MESES},
    labels={
        "Competência": "Competência",
        "Repasse": "Valor (R$)",
        "Credor": "Credor"
    }
)

fig.update_layout(
    height=520,
    yaxis_tickprefix="R$ ",
    yaxis_tickformat=",.0f"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TABELA
# -------------------------
st.subheader("📄 Detalhamento")

df_tab = df_f.sort_values(["Credor", "Competência"]).copy()

df_tab["Repasse"] = df_tab["Repasse"].map(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

st.dataframe(df_tab, use_container_width=True, hide_index=True)
