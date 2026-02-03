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
st.caption("Repasses à Administração Indireta (Despesa Extra)")

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

# 🔁 LINHA 1: Credor | Exercício
col1, col2 = st.columns(2)

credores = sorted(df["Credor"].unique())
credor_sel = col1.multiselect(
    "Credor",
    credores,
    default=credores
)

exercicios = sorted(df["Exercício"].dropna().astype(int).unique())
ex_sel = col2.multiselect(
    "Exercício",
    exercicios,
    default=exercicios
)

# 🔁 LINHA 2: Competência | Fonte
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

# 🔒 BLINDAGEM FINAL DO REPASSE
df_f["Repasse"] = pd.to_numeric(df_f["Repasse"], errors="coerce").fillna(0)

# ==================================================
# TABELA DETALHADA
# ==================================================
st.markdown("---")
st.subheader("📋 Detalhamento")

df_tabela = df_f.copy()
df_tabela["Exercício"] = df_tabela["Exercício"].astype(str)
df_tabela["Repasse"] = df_tabela["Repasse"].apply(float_para_moeda)

# Ordenar corretamente pela competência
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
# DOWNLOAD CSV
# ==================================================
st.markdown("---")

csv = df_tabela.to_csv(index=False, sep=";", encoding="utf-8")
st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="repasse_indireta.csv",
    mime="text/csv"
)

# ==================================================
# GRÁFICO – Evolução Mensal (Barras)
# ==================================================
st.markdown("---")
st.subheader("📈 Evolução Mensal dos Repasses")

df_graf = df_f.copy()
df_graf["Exercício"] = df_graf["Exercício"].astype(str)

# Ordenar competências corretamente
df_graf["Competência"] = pd.Categorical(
    df_graf["Competência"],
    categories=MESES,
    ordered=True
)

# Garantir que Repasse é número
df_graf["Repasse"] = pd.to_numeric(df_graf["Repasse"], errors="coerce").fillna(0)

# Gráfico de barras agrupadas
fig = px.bar(
    df_graf,
    x="Competência",
    y="Repasse",
    color="Exercício",
    barmode="group",
    facet_col="Credor",
    labels={
        "Competência": "Mês",
        "Repasse": "Valor (R$)",
        "Exercício": "Ano",
        "Credor": "Credor"
    }
)

# Formatar eixo y como moeda
fig.update_layout(
    height=520,
    yaxis_tickprefix="R$ ",
    yaxis_tickformat=",.0f",  # mantém separador de milhares
    legend=dict(
        orientation="h",
        y=-0.25,
        x=0.5,
        xanchor="center"
    )
)

# Limpar texto das facetas
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

st.plotly_chart(fig, use_container_width=True)

st.caption("Repasse – Administração Indireta • Consulta")









