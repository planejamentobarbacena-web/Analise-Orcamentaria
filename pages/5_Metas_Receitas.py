import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

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
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Metas de Receita",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Metas de Receita")

# =====================================================
# CONSTANTES
# =====================================================
MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# =====================================================
# FUNÇÕES
# =====================================================
def fmt_moeda(v):
    if pd.isna(v) or v == 0:
        return ""
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def normalizar(txt):
    if pd.isna(txt):
        return ""
    return (
        unicodedata.normalize("NFKD", str(txt))
        .encode("ASCII", "ignore")
        .decode("utf-8")
        .lower()
        .strip()
    )

# =====================================================
# DADOS
# =====================================================
anos = exercicios_metas()
df_full = carregar_metas_multiplos_exercicios(anos)

df_full["Especificacao_norm"] = df_full["Especificação"].apply(normalizar)

# força ordem dos meses
df_full["Competência"] = pd.Categorical(
    df_full["Competência"],
    categories=MESES,
    ordered=True
)

# =====================================================
# FILTROS
# =====================================================
st.subheader("🎯 Filtros")

c1, c2, c3 = st.columns(3)

# ---- Receita
receitas = (
    df_full[["Especificação", "Especificacao_norm"]]
    .drop_duplicates()
    .sort_values("Especificação")
)

mapa = dict(zip(receitas["Especificação"], receitas["Especificacao_norm"]))

receita_sel = c1.selectbox(
    "Receita",
    ["Todas"] + list(mapa.keys())
)

df = df_full.copy()

if receita_sel != "Todas":
    df = df[df["Especificacao_norm"] == mapa[receita_sel]]

# ---- Exercício
anos_disp = sorted(df["Exercício"].unique())

ex_sel = c2.multiselect(
    "Exercício",
    ["Todos"] + anos_disp,
    default=["Todos"]
)

if "Todos" not in ex_sel:
    df = df[df["Exercício"].isin(ex_sel)]

# ---- Competência
mes_sel = c3.multiselect(
    "Competência",
    ["Todos"] + MESES,
    default=["Todos"]
)

if "Todos" not in mes_sel:
    df = df[df["Competência"].isin(mes_sel)]

# =====================================================
# GRÁFICO (AGORA SOMA, NÃO CONTA)
# =====================================================
st.markdown("---")
st.subheader("📈 Gráfico Comparativo")

tipo_valor = st.multiselect(
    "Tipo de Valor",
    ["Previsto", "Realizado"],
    default=["Previsto", "Realizado"]
)

if receita_sel == "Todas":
    st.info("Selecione uma receita para visualizar o gráfico.")
elif not tipo_valor:
    st.warning("Selecione Previsto e/ou Realizado.")
else:
    df_long = df.melt(
        id_vars=["Exercício", "Competência"],
        value_vars=tipo_valor,
        var_name="Tipo",
        value_name="Valor"
    )

    # 🔑 CORREÇÃO CRÍTICA
    df_long["Valor"] = pd.to_numeric(df_long["Valor"], errors="coerce").fillna(0)

    df_long = df_long[df_long["Valor"] > 0]

    df_long["Serie"] = (
        df_long["Tipo"] + " " + df_long["Exercício"].astype(str)
    )

    fig = px.bar(
        df_long,
        x="Competência",
        y="Valor",
        color="Serie",
        barmode="group",
        category_orders={"Competência": MESES},
        labels={"Valor": "Valor (R$)", "Serie": ""},
        title=f"Comparativo Mensal – {receita_sel}"
    )

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
# TABELA (ORDEM CORRETA)
# =====================================================
# =====================================================
# TABELA (ORDEM CORRETA: Previsto + Realizado POR MÊS)
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

# garante ordem dos meses
tabela = tabela.reindex(MESES, axis=1, level=1)

# 🔑 REORGANIZA AS COLUNAS PARA:
# Previsto Janeiro | Realizado Janeiro | Previsto Fevereiro | Realizado Fevereiro | ...
colunas_ordenadas = []
for mes in MESES:
    for tipo in ["Previsto", "Realizado"]:
        if (tipo, mes) in tabela.columns:
            colunas_ordenadas.append((tipo, mes))

tabela = tabela[colunas_ordenadas]

# renomeia colunas
tabela.columns = [f"{tipo} {mes}" for tipo, mes in tabela.columns]
tabela = tabela.reset_index()

# formatação monetária
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
    file_name="metas_receita.csv",
    mime="text/csv"
)

st.caption("Metas de Receita • Valores reais e meses ordenados")

