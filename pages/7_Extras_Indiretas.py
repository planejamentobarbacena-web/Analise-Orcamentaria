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
# =====================================================
# GRÁFICO – VISÃO GERAL POR EXERCÍCIO
# =====================================================
st.markdown("---")
st.subheader("📊 Comparativo Orçamentário por Exercício")

df_grafico = (
    df_ag
    .groupby("Exercício", as_index=False)[
        ["valor_orcado", "valor_atualizado", "valor_empenhado"]
    ]
    .sum()
)

df_long = df_grafico.melt(
    id_vars="Exercício",
    value_vars=["valor_orcado", "valor_atualizado", "valor_empenhado"],
    var_name="Tipo",
    value_name="Valor"
)

df_long["Tipo"] = df_long["Tipo"].map({
    "valor_orcado": "Orçada",
    "valor_atualizado": "Atualizada",
    "valor_empenhado": "Empenhada"
})

ordem_tipo = ["Orçada", "Atualizada", "Empenhada"]
df_long["Tipo"] = pd.Categorical(
    df_long["Tipo"],
    categories=ordem_tipo,
    ordered=True
)

df_long["Valor_fmt"] = df_long["Valor"].apply(fmt_moeda_br)

grafico = (
    alt.Chart(df_long)
    .mark_bar(size=30)  # <<< CONTROLE DE LARGURA
    .encode(
        x=alt.X(
            "Exercício:N",
            title="Exercício",
            axis=alt.Axis(labelAngle=0)
        ),
        xOffset=alt.XOffset("Tipo:N", sort=ordem_tipo),
        y=alt.Y("Valor:Q", title="Valor (R$)"),
        color=alt.Color("Tipo:N", title="Despesa", sort=ordem_tipo),
        tooltip=[
            "Exercício:N",
            "Tipo:N",
            alt.Tooltip("Valor_fmt:N", title="Valor (R$)")
        ]
    )
    .properties(height=420)
)

st.altair_chart(grafico, use_container_width=True)

st.caption("Repasse – Administração Indireta • Consulta")
