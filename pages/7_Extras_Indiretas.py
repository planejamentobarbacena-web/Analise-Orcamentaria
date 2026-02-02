import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Repasses Extras", layout="wide")

st.title("💰 Repasses Extras")

# -------------------------
# CONSTANTES
# -------------------------
MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

# -------------------------
# LEITURA DO CSV
# -------------------------
@st.cache_data
def carregar_dados():
    df = pd.read_csv(
        "extras_2023.csv",  # ajuste se necessário
        sep=";",
        encoding="utf-8"
    )

    # padronização
    df.columns = df.columns.str.strip()

    # conversões
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


df = carregar_dados()

# -------------------------
# FILTROS
# -------------------------
st.sidebar.header("🔎 Filtros")

exercicio_sel = st.sidebar.selectbox(
    "Exercício",
    sorted(df["Exercício"].unique())
)

df_f = df[df["Exercício"] == exercicio_sel]

credor_sel = st.sidebar.multiselect(
    "Credor",
    sorted(df_f["Credor"].unique()),
    default=sorted(df_f["Credor"].unique())
)

df_f = df_f[df_f["Credor"].isin(credor_sel)]

fonte_sel = st.sidebar.multiselect(
    "Fonte",
    sorted(df_f["Fonte"].unique()),
    default=sorted(df_f["Fonte"].unique())
)

df_f = df_f[df_f["Fonte"].isin(fonte_sel)]

# -------------------------
# INDICADORES
# -------------------------
st.subheader("📊 Resumo")

col1, col2 = st.columns(2)

col1.metric(
    "Total de Registros",
    f"{len(df_f)}"
)

col2.metric(
    "Total Repassado",
    f"R$ {df_f['Repasse'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
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
    yaxis_tickformat=",.0f",
    legend_title_text="Credor"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# TABELA
# -------------------------
st.subheader("📄 Detalhamento")

df_tabela = df_f.sort_values(["Credor", "Competência"])

df_tabela["Repasse"] = df_tabela["Repasse"].map(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

st.dataframe(
    df_tabela,
    use_container_width=True,
    hide_index=True
)
