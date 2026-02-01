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
# FILTROS EM DUAS LINHAS COM “Todos”
# ==================================================
st.subheader("🎯 Filtros")

# Linha 1: Exercício - Credor
col1, col2 = st.columns(2)

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

# Linha 2: Competência - Fonte
col3, col4 = st.columns(2)

# Competência com "Todos"
comp_opcoes = ["Todos"] + MESES
comp_sel = col3.multiselect(
    "Competência",
    comp_opcoes,
    default=["Todos"]
)

# Fonte com "Todos"
fonte_opcoes = ["Todos"] + sorted(df["Fonte"].unique())
fonte_sel = col4.multiselect(
    "Fonte",
    fonte_opcoes,
    default=["Todos"]
)

# ==================================================
# FILTRAGEM DOS DADOS
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


# ==================================================
# GRÁFICO - Cada Credor com barras lado a lado por mês/ano
# ==================================================
st.markdown("---")
st.subheader("📈 Evolução Mensal dos Repasses por Credor")


df_graf = (
    df_f
    .groupby(["Credor", "Competência", "Exercício"], as_index=False)
    .agg({"Repasse": "sum"})
)

# força tudo como string (crítico)
df_graf["Competência"] = df_graf["Competência"].astype(str)
df_graf["Exercício"] = df_graf["Exercício"].astype(str)


# Ordena os meses corretamente
df_graf["Competência"] = pd.Categorical(
    df_graf["Competência"],
    categories=MESES,
    ordered=True
)

# Cria coluna combinando Mes/Ano como string
df_graf["MesAno"] = df_graf["Competência"].astype(str) + "/" + df_graf["Exercício"].astype(str)
# Cria coluna combinando Credor + Mes/Ano para barras lado a lado
df_graf["CredorMesAno"] = df_graf["Credor"] + " - " + df_graf["MesAno"]

# Ordena pelo Credor, Competência e Exercício
df_graf = df_graf.sort_values(["Credor", "Competência", "Exercício"])

# Plot
fig = px.bar(
    df_graf,
    x="Competência",
    y="Repasse",
    color="Exercício",      # 🔑 separa 2024 / 2025 (lado a lado)
    facet_col="Credor",     # 🔑 um gráfico por credor
    barmode="group",        # 🔑 nunca empilha
    category_orders={
        "Competência": MESES,
        "Exercício": sorted(df_graf["Exercício"].astype(str).unique())
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
# TABELA DETALHADA
# ==================================================
st.markdown("---")
st.subheader("📋 Detalhamento dos Repasses")

df_tabela = df_f.copy()
df_tabela["Repasse"] = df_tabela["Repasse"].apply(float_para_moeda)

# Ordena Competência respeitando a ordem dos meses
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
