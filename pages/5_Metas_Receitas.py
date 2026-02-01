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
df = carregar_metas_multiplos_exercicios(anos)
st.subheader("🧪 Debug – Tipos das colunas")
st.write(df[["Previsto", "Realizado"]].dtypes)


# ---- Receita
receitas = ["Todas"] + sorted(df["Especificação"].dropna().unique())
receita_sel = col2.selectbox("Receita", receitas)

if receita_sel != "Todas":
    df = df[df["Especificação"] == receita_sel]

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
# =====================================================
# GRÁFICO
# =====================================================
if receita_sel == "Todas":
    st.info("Selecione uma receita específica para visualizar o gráfico.")
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

    # 🔑 chave visual: Tipo + Exercício
    df_long["Serie"] = df_long["Tipo"] + " " + df_long["Exercício"].astype(str)

    fig = px.bar(
        df_long,
        x="Competência",
        y="Valor",
        color="Serie",                 # 👈 NÃO AGREGA MAIS
        barmode="group",
        category_orders={
            "Competência": ordem_meses
        },
        labels={
            "Valor": "Valor (R$)",
            "Competência": "Mês",
            "Serie": ""
        },
        title=f"Comparativo Mensal – {receita_sel}"
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
        orientation="h",      # 👈 legenda horizontal
        yanchor="top",
        y=-0.25,              # 👈 joga pra baixo do gráfico
        xanchor="center",
        x=0.5
    ),
    margin=dict(b=90)         # 👈 espaço extra para a legenda
)

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABELA (SEM DEPENDER DO GRÁFICO)
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

tabela.columns = [
    f"{tipo} {mes}"
    for tipo, mes in tabela.columns
]

tabela = tabela.reset_index()

colunas_ordenadas = ["Exercício", "Especificação"]
for mes in ordem_meses:
    for tipo in ["Previsto", "Realizado"]:
        col = f"{tipo} {mes}"
        if col in tabela.columns:
            colunas_ordenadas.append(col)

tabela = tabela[colunas_ordenadas]

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


st.caption("Metas de Receita • Gráfico comparativo por tipo e exercício")
