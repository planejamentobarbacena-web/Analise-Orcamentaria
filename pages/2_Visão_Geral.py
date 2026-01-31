import streamlit as st
import pandas as pd
import altair as alt

from utils import (
    exercicios_disponiveis,
    carregar_despesas,
    carregar_despesas_multiplos_exercicios
)

# =====================================================
# SEGURANÇA
# =====================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado.")
    st.stop()

if st.session_state.get("perfil") not in ["administrador", "consulta"]:
    st.error("🚫 Perfil sem permissão.")
    st.stop()

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Visão Geral da Execução Orçamentária",
    page_icon="📊",
    layout="wide"
)

st.header("📊 Visão Geral da Execução Orçamentária")

# =====================================================
# FUNÇÃO MOEDA
# =====================================================
def fmt_moeda_br(valor):
    if pd.isna(valor):
        return "0,00"
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================
# FILTROS
# =====================================================
st.subheader("🎯 Filtros")

# LINHA 1
col1, col2 = st.columns(2)

exercicios = exercicios_disponiveis()
sel_ex = col1.multiselect(
    "Exercício",
    ["Todos"] + exercicios,
    default=["Todos"]
)

anos = exercicios if "Todos" in sel_ex else sel_ex

df_base = carregar_despesas_multiplos_exercicios(
    anos,
    carregar_despesas
)

df = df_base.copy()

organogramas = ["Todos"] + sorted(df_base["Organograma"].dropna().unique())
org_sel = col2.selectbox("Descrição do organograma", organogramas)

if org_sel != "Todos":
    df = df[df["Organograma"] == org_sel]

# LINHA 2
col3, col4 = st.columns(2)

subfs = ["Todos"] + sorted(df_base["Subfunção"].dropna().unique())
subf_sel = col3.selectbox("Descrição da subfunção", subfs)

if subf_sel != "Todos":
    df = df[df["Subfunção"] == subf_sel]

recursos = ["Todos"] + sorted(df_base["Recurso"].dropna().unique())
rec_sel = col4.selectbox("Recurso", recursos)

if rec_sel != "Todos":
    df = df[df["Recurso"] == rec_sel]

# =====================================================
# AGREGAÇÃO
# =====================================================
df_ag = (
    df.groupby("Exercício", as_index=False)[
        ["valor_orcado", "valor_atualizado", "valor_empenhado"]
    ].sum()
)

# =====================================================
# GRÁFICO
# =====================================================
st.markdown("---")
st.subheader("📊 Comparativo Orçamentário por Exercício")

df_long = df_ag.melt(
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

ordem = ["Orçada", "Atualizada", "Empenhada"]
df_long["Tipo"] = pd.Categorical(df_long["Tipo"], categories=ordem, ordered=True)
df_long["Valor_fmt"] = df_long["Valor"].apply(fmt_moeda_br)

grafico = (
    alt.Chart(df_long)
    .mark_bar(size=30)
    .encode(
        x=alt.X("Exercício:N", title="Exercício"),
        xOffset=alt.XOffset("Tipo:N", sort=ordem),
        y=alt.Y("Valor:Q", title="Valor (R$)"),
        color=alt.Color("Tipo:N", title="Despesa", sort=ordem),
        tooltip=[
            "Exercício:N",
            "Tipo:N",
            alt.Tooltip("Valor_fmt:N", title="Valor (R$)")
        ]
    )
    .properties(height=420)
)

st.altair_chart(grafico, use_container_width=True)
st.caption("Visão Geral • Execução Orçamentária Consolidada")