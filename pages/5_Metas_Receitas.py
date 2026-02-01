import streamlit as st
import pandas as pd
import plotly.express as px

from utils_metas import (
    exercicios_metas,
    carregar_metas_multiplos_exercicios
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
    page_title="Metas de Receita",
    page_icon="📊",
    layout="wide"
)

st.header("📊 Metas de Receita")

# =====================================================
# FUNÇÃO DE FORMATAÇÃO
# =====================================================
def fmt_moeda(valor):
    if pd.isna(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================
# FILTROS
# =====================================================
st.subheader("🎯 Filtros")

col1, col2, col3 = st.columns(3)

exercicios = exercicios_metas()
sel_exercicios = col1.multiselect(
    "Exercício",
    ["Todos"] + exercicios,
    default=["Todos"]
)

anos = exercicios if "Todos" in sel_exercicios else sel_exercicios

# =====================================================
# CARGA DOS DADOS
# =====================================================
df = carregar_metas_multiplos_exercicios(anos)

# Receita
receitas = ["Todas"] + sorted(df["Especificação"].dropna().unique())
receita_sel = col2.selectbox("Receita", receitas)

if receita_sel != "Todas":
    df = df[df["Especificação"] == receita_sel]

# Ordem correta dos meses
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# Competência
competencias = ["Todas"] + ordem_meses
comp_sel = col3.multiselect(
    "Competência",
    competencias,
    default=["Todas"]
)

if "Todas" not in comp_sel:
    df = df[df["Competência"].isin(comp_sel)]

# 🔑 GARANTIA ABSOLUTA DE ORDEM
df["Competência"] = pd.Categorical(
    df["Competência"],
    categories=ordem_meses,
    ordered=True
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

if receita_sel == "Todas":
    st.info("Selecione uma receita específica para visualizar o gráfico.")
elif not tipo_valor:
    st.warning("Selecione ao menos um tipo de valor.")
else:
    # TRANSFORMA EM LONGO
    df_long = df.melt(
        id_vars=["Exercício", "Competência"],
        value_vars=["Previsto", "Realizado"],
        var_name="Tipo",
        value_name="Valor"
    )

    df_long = df_long[df_long["Tipo"].isin(tipo_valor)]

    # ❗ NADA DE AGREGAÇÃO
    fig = px.bar(
        df_long,
        x="Competência",
        y="Valor",
        color="Tipo",
        barmode="group",
        facet_col="Exercício",  # 👈 separa os anos corretamente
        category_orders={"Competência": ordem_meses},
        labels={
            "Valor": "Valor (R$)",
            "Competência": "Mês",
            "Tipo": ""
        },
        title=f"Comparativo Mensal – {receita_sel}"
    )

    fig.update_layout(
        height=600,
        yaxis_tickprefix="R$ ",
        yaxis_tickformat=",.0f",
        legend_title_text="",
        margin=dict(t=80)
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Metas de Receita – Visão Tabular")

tabela = (
    df
    .pivot_table(
        index=["Exercício", "Especificação"],
        columns="Competência",
        values=["Previsto", "Realizado"],
        aggfunc="sum"
    )
)

tabela.columns = [f"{tipo} {mes}" for tipo, mes in tabela.columns]
tabela = tabela.reset_index()

for col in tabela.columns:
    if col not in ["Exercício", "Especificação"]:
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
    file_name="metas_receita_competencia.csv",
    mime="text/csv"
)

st.caption("Metas de Receita • Comparativo mensal por exercício")
