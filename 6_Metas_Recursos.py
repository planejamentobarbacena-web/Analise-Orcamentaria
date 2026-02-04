import streamlit as st
import pandas as pd
import plotly.express as px

from utils_metas import (
    exercicios_metas,
    carregar_metas_recurso_multiplos_exercicios
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
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Metas por Fonte / Recurso",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Metas por Fonte / Recurso")

# =====================================================
# FORMATAÇÃO
# =====================================================
def fmt_moeda(valor):
    if pd.isna(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================
# CARGA COMPLETA
# =====================================================
anos = exercicios_metas()
df_full = carregar_metas_recurso_multiplos_exercicios(anos)

if df_full.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

# =====================================================
# FILTROS
# =====================================================
st.subheader("🎯 Filtros")

col1, col2, col3 = st.columns(3)

# ---- Fonte / Recurso (CÓDIGO)
mapa = (
    df_full[["Codigo", "Especificacao"]]
    .drop_duplicates()
    .sort_values("Codigo")
)

opcoes_recurso = (
    mapa["Codigo"] + " - " + mapa["Especificacao"]
).tolist()

recurso_sel = col1.selectbox(
    "Fonte / Recurso",
    ["Todos"] + opcoes_recurso
)

df = df_full.copy()

if recurso_sel != "Todos":
    codigo_sel = recurso_sel.split(" - ")[0]
    df = df[df["Codigo"] == codigo_sel]

# ---- Exercício
anos_disp = sorted(df["Exercício"].unique())

sel_anos = col2.multiselect(
    "Exercício",
    ["Todos"] + anos_disp,
    default=["Todos"]
)

if "Todos" not in sel_anos:
    df = df[df["Exercício"].isin(sel_anos)]

# ---- Competência
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

comp_sel = col3.multiselect(
    "Competência",
    ["Todas"] + ordem_meses,
    default=["Todas"]
)

if "Todas" not in comp_sel:
    df = df[df["Competência"].isin(comp_sel)]

# =====================================================
# CONSOLIDAÇÃO
# =====================================================
df_base = (
    df
    .groupby(
        ["Exercício", "Codigo", "Especificacao", "Competência"],
        as_index=False
    )[["Previsto", "Realizado"]]
    .sum()
)

# =====================================================
# GRÁFICO
# =====================================================
st.markdown("---")
st.subheader("📈 Gráfico Comparativo")

tipo_valor = st.multiselect(
    "Tipo de Valor",
    ["Previsto", "Realizado"],
    default=["Previsto", "Realizado"]
)

if recurso_sel == "Todos":
    st.info("Selecione um recurso específico para visualizar o gráfico.")
elif not tipo_valor:
    st.warning("Selecione ao menos um tipo de valor.")
else:
    df_long = df_base.melt(
        id_vars=["Exercício", "Competência"],
        value_vars=["Previsto", "Realizado"],
        var_name="Tipo",
        value_name="Valor"
    )

    df_long = df_long[df_long["Tipo"].isin(tipo_valor)]

    df_long["Serie"] = df_long["Tipo"] + " " + df_long["Exercício"].astype(str)

    fig = px.bar(
        df_long,
        x="Competência",
        y="Valor",
        color="Serie",
        barmode="group",
        category_orders={"Competência": ordem_meses},
        title=f"Comparativo Mensal – {recurso_sel}",
        labels={
            "Valor": "Valor (R$)",
            "Competência": "Mês",
            "Serie": ""
        }
    )

    fig.update_traces(width=0.32)

    fig.update_layout(
        height=600,
        yaxis_tickprefix="R$ ",
        yaxis_tickformat=",.0f",
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0.5,
            xanchor="center"
        ),
        margin=dict(b=90)
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Metas por Fonte – Visão Tabular")

tabela = (
    df
    .pivot_table(
        index=["Exercício", "Codigo", "Especificacao"],
        columns="Competência",
        values=["Previsto", "Realizado"],
        aggfunc="sum"
    )
)

tabela.columns = [f"{t} {m}" for t, m in tabela.columns]
tabela = tabela.reset_index()

colunas = ["Exercício", "Codigo", "Especificacao"]
for mes in ordem_meses:
    for tipo in ["Previsto", "Realizado"]:
        col = f"{tipo} {mes}"
        if col in tabela.columns:
            colunas.append(col)

tabela = tabela[colunas]

for col in tabela.columns:
    if col not in ["Exercício", "Codigo", "Especificacao"]:
        tabela[col] = tabela[col].apply(fmt_moeda)

st.dataframe(tabela, use_container_width=True)

# =====================================================
# DOWNLOAD
# =====================================================
st.markdown("---")

csv = tabela.to_csv(index=False, sep=";", encoding="utf-8")
st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="metas_por_fonte_competencia.csv",
    mime="text/csv"
)

st.caption("Metas por Fonte / Recurso • Estrutura oficial")
