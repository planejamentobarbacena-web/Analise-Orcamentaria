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
# FUNÇÕES
# =====================================================
def fmt_moeda(valor):
    if pd.isna(valor) or valor == 0:
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# =====================================================
# CARGA DOS DADOS
# =====================================================
exercicios = exercicios_metas()
df_full = carregar_metas_multiplos_exercicios(exercicios)

df_full["Especificacao_norm"] = df_full["Especificação"].apply(normalizar)

# =====================================================
# FILTROS
# =====================================================
st.subheader("🎯 Filtros")

c1, c2, c3 = st.columns(3)

# ---- Receita (primeiro)
receitas = (
    df_full[["Especificação", "Especificacao_norm"]]
    .drop_duplicates()
    .sort_values("Especificação")
)

mapa_receitas = dict(zip(receitas["Especificação"], receitas["Especificacao_norm"]))

receita_sel = c1.selectbox(
    "Receita",
    ["Todas"] + list(mapa_receitas.keys())
)

df = df_full.copy()

if receita_sel != "Todas":
    df = df[df["Especificacao_norm"] == mapa_receitas[receita_sel]]

# ---- Exercício
anos = sorted(df["Exercício"].unique())

ex_sel = c2.multiselect(
    "Exercício",
    ["Todos"] + anos,
    default=["Todos"]
)

if "Todos" not in ex_sel:
    df = df[df["Exercício"].isin(ex_sel)]

# ---- Mês
mes_sel = c3.multiselect(
    "Competência",
    ["Todos"] + MESES,
    default=["Todos"]
)

meses_usados = MESES if "Todos" in mes_sel else mes_sel

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
    st.info("Selecione uma receita para exibir o gráfico.")
elif not tipo_valor:
    st.warning("Selecione Previsto e/ou Realizado.")
else:
    linhas = []

    for _, row in df.iterrows():
        for mes in meses_usados:
            if "Previsto" in tipo_valor:
                linhas.append({
                    "Competência": mes,
                    "Serie": f"Previsto {row['Exercício']}",
                    "Valor": row.get(f"Previsto {mes}", 0)
                })
            if "Realizado" in tipo_valor:
                linhas.append({
                    "Competência": mes,
                    "Serie": f"Realizado {row['Exercício']}",
                    "Valor": row.get(f"Realizado {mes}", 0)
                })

    df_graf = pd.DataFrame(linhas)
    df_graf = df_graf[df_graf["Valor"] > 0]

    fig = px.bar(
        df_graf,
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
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Metas de Receita – Visão Tabular")

tabela = (
    df
    .pivot_table(
        index=["Exercício", "Especificação"],
        values=[f"Previsto {m}" for m in MESES] + [f"Realizado {m}" for m in MESES],
        aggfunc="sum"
    )
    .reset_index()
)

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

st.caption("Metas de Receita • Gráfico e tabela coerentes com o CSV")
