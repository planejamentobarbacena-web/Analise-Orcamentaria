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
    page_title="Metas por Recurso",
    page_icon="📊",
    layout="wide"
)

st.header("📊 Metas por Recurso")

# =====================================================
# FUNÇÃO DE FORMATAÇÃO MONETÁRIA
# =====================================================
def fmt_moeda(valor):
    if pd.isna(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =====================================================
# FILTROS GERAIS
# =====================================================
st.subheader("🎯 Filtros")

col1, col2, col3 = st.columns(3)

# ---- Exercício
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
df = carregar_metas_recurso_multiplos_exercicios(anos)

# ---- Recurso
recursos = ["Todos"] + sorted(df["Recurso"].dropna().unique())
recurso_sel = col2.selectbox("Recurso", recursos)

if recurso_sel != "Todos":
    df = df[df["Recurso"] == recurso_sel]

# ---- Competência
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

competencias = ["Todas"] + ordem_meses
comp_sel = col3.multiselect(
    "Competência",
    competencias,
    default=["Todas"]
)

if "Todas" not in comp_sel:
    df = df[df["Competência"].isin(comp_sel)]

# =====================================================
# FILTROS DO GRÁFICO
# =====================================================
st.markdown("---")
st.subheader("📈 Gráfico Comparativo")

tipo_valor = st.multiselect(
    "Tipo de Valor",
    ["Previsto", "Realizado"],
    default=["Previsto", "Realizado"]
)

# =====================================================
# GRÁFICO
# =====================================================
if recurso_sel == "Todos":
    st.info("Selecione um recurso específico para visualizar o gráfico.")
elif not tipo_valor:
    st.warning("Selecione ao menos um tipo de valor para o gráfico.")
else:
    df_long = df.melt(
        id_vars=["Exercício", "Competência"],
        value_vars=["Previsto", "Realizado"],
        var_name="Tipo",
        value_name="Valor"
    )

    df_long = df_long[
        (df_long["Tipo"].isin(tipo_valor)) &
        (df_long["Valor"] > 0)
    ]

    df_long["Serie"] = df_long["Tipo"] + " " + df_long["Exercício"].astype(str)

    fig = px.bar(
        df_long,
        x="Competência",
        y="Valor",
        color="Serie",
        barmode="group",
        category_orders={"Competência": ordem_meses},
        labels={
            "Valor": "Valor (R$)",
            "Competência": "Mês",
            "Serie": ""
        },
        title=f"Comparativo Mensal – {recurso_sel}"
    )

    fig.update_traces(width=0.32)

    fig.update_layout(
        bargap=0.15,
        bargroupgap=0.05,
        height=600,
        yaxis_tickprefix="R$ ",
        yaxis_tickformat=",.0f",
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=90)
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Metas por Recurso – Visão Tabular")

tabela = (
    df
    .pivot_table(
        index=["Exercício", "Recurso"],
        columns="Competência",
        values=["Previsto", "Realizado"],
        aggfunc="sum"
    )
)

tabela.columns = [f"{tipo} {mes}" for tipo, mes in tabela.columns]
tabela = tabela.reset_index()

colunas_ordenadas = ["Exercício", "Recurso"]
for mes in ordem_meses:
    for tipo in ["Previsto", "Realizado"]:
        col = f"{tipo} {mes}"
        if col in tabela.columns:
            colunas_ordenadas.append(col)

tabela = tabela[colunas_ordenadas]

for col in tabela.columns:
    if col not in ["Exercício", "Recurso"]:
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
    file_name="metas_recurso_competencia.csv",
    mime="text/csv"
)

st.caption("Metas por Recurso • Gráfico comparativo por tipo e exercício")