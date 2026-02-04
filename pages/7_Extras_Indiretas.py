import streamlit as st
import pandas as pd

from utils_extras import (
    carregar_extras,
    filtrar_extras,
    float_para_moeda,
    agregar_repasse_por_exercicio,
    MESES
)

from utils_graficos import grafico_barra_exercicio

# ==================================================
# CONFIGURAÇÃO DA PÁGINA (TEM QUE SER PRIMEIRO)
# ==================================================
st.set_page_config(
    page_title="Repasse – Indireta",
    page_icon="🏛️",
    layout="wide"
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
# TÍTULO
# ==================================================
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

col1, col2 = st.columns(2)

credor_sel = col1.multiselect(
    "Credor",
    sorted(df["Credor"].unique()),
    default=sorted(df["Credor"].unique())
)

ex_sel = col2.multiselect(
    "Exercício",
    sorted(df["Exercício"].unique()),
    default=sorted(df["Exercício"].unique())
)

col3, col4 = st.columns(2)

comp_sel = col3.multiselect(
    "Competência",
    ["Todos"] + MESES,
    default=["Todos"]
)

fonte_sel = col4.multiselect(
    "Fonte",
    ["Todos"] + sorted(df["Fonte"].unique()),
    default=["Todos"]
)

# ==================================================
# APLICA FILTROS
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

df_f["Repasse"] = pd.to_numeric(df_f["Repasse"], errors="coerce").fillna(0)

# ==================================================
# TABELA
# ==================================================
st.markdown("---")
st.subheader("📋 Detalhamento")

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

# ==================================================
# GRÁFICO (USANDO UTILS_GRAFICOS)
# ==================================================
st.markdown("---")
st.subheader("📊 Repasse por Exercício")

df_grafico = agregar_repasse_por_exercicio(df_f)

df_grafico["Repasse_fmt"] = df_grafico["Repasse"].apply(float_para_moeda)

fig = grafico_barra_exercicio(
    df_grafico,
    coluna_exercicio="Exercício",
    coluna_valor="Repasse",
    coluna_texto="Repasse_fmt",
    titulo="Repasse por Exercício",
    label_valor="Valor (R$)"
)

if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhum dado para exibir no gráfico com os filtros atuais.")

st.caption("Repasse – Administração Indireta • Consulta")
