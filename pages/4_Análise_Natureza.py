import streamlit as st
import pandas as pd
import altair as alt
from utils import exercicios_disponiveis, carregar_despesas_por_natureza

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
    page_title="Análise por Natureza",
    page_icon="📌",
    layout="wide"
)

st.header("📌 Análise Orçamentária por Natureza da Despesa")

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

# -----------------------------------------------------
# EXERCÍCIO (LIVRE)
# -----------------------------------------------------
exercicios = exercicios_disponiveis()

sel_ex = st.multiselect(
    "Exercício",
    ["Todos"] + exercicios,
    default=st.session_state.get("nat_exercicio", ["Todos"]),
    key="nat_exercicio"
)

anos = exercicios if "Todos" in sel_ex else sel_ex

# =====================================================
# CARGA DOS DADOS
# =====================================================
dfs = []
for ano in anos:
    try:
        df_ano = carregar_despesas_por_natureza(ano)
        df_ano["Exercício"] = ano
        dfs.append(df_ano)
    except Exception:
        pass

if not dfs:
    st.warning("Nenhum dado encontrado.")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

# =====================================================
# FILTRO – ENTIDADE (LIVRE)
# =====================================================
entidades = ["Todos"] + sorted(df["Entidade"].dropna().unique())

valor_atual = st.session_state.get("nat_entidade", "Todos")
if valor_atual not in entidades:
    valor_atual = "Todos"

ent_sel = st.selectbox(
    "Entidade",
    entidades,
    index=entidades.index(valor_atual),
    key="nat_entidade"
)

if ent_sel != "Todos":
    df = df[df["Entidade"] == ent_sel]

# =====================================================
# FILTRO – NATUREZA (LIVRE)
# =====================================================
naturezas = ["Todos"] + sorted(df["Natureza_Normalizada"].dropna().unique())

valor_atual = st.session_state.get("nat_natureza", ["Todos"])
if not set(valor_atual).intersection(naturezas):
    valor_atual = ["Todos"]

nat_sel = st.multiselect(
    "Natureza da Despesa (Código)",
    naturezas,
    default=valor_atual,
    key="nat_natureza"
)

if "Todos" not in nat_sel:
    df = df[df["Natureza_Normalizada"].isin(nat_sel)]

# =====================================================
# FILTRO – FONTE DE RECURSO (LIVRE)
# =====================================================
recursos = ["Todos"] + sorted(df["Recurso"].dropna().unique())

valor_atual = st.session_state.get("nat_recurso", ["Todos"])
if not set(valor_atual).intersection(recursos):
    valor_atual = ["Todos"]

rec_sel = st.multiselect(
    "Fonte de Recurso",
    recursos,
    default=valor_atual,
    key="nat_recurso"
)

if "Todos" not in rec_sel:
    df = df[df["Recurso"].isin(rec_sel)]

# =====================================================
# AGREGAÇÃO FINAL
# =====================================================
chaves = [
    "Exercício",
    "Entidade",
    "Natureza_Normalizada",
    "Recurso"
]

df_ag = (
    df
    .groupby(chaves, as_index=False)[
        ["valor_orcado", "valor_atualizado", "valor_empenhado"]
    ]
    .sum()
)

descricao = (
    df[["Natureza_Normalizada", "Descrição da Natureza"]]
    .drop_duplicates()
)

df_ag = df_ag.merge(
    descricao,
    on="Natureza_Normalizada",
    how="left"
)

# =====================================================
# GRÁFICO
# =====================================================
st.markdown("---")
st.subheader("📊 Comparativo Orçamentário por Exercício")

df_graf = (
    df_ag
    .groupby("Exercício", as_index=False)[
        ["valor_orcado", "valor_atualizado", "valor_empenhado"]
    ]
    .sum()
)

df_long = df_graf.melt(
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

# =====================================================
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Detalhamento por Natureza")

tabela = df_ag.rename(columns={
    "Natureza_Normalizada": "Natureza da Despesa",
    "Recurso": "Fonte de Recurso",
    "valor_orcado": "Valor Orçado",
    "valor_atualizado": "Valor Atualizado",
    "valor_empenhado": "Valor Empenhado",
})

for c in ["Valor Orçado", "Valor Atualizado", "Valor Empenhado"]:
    tabela[c] = tabela[c].apply(lambda x: f"R$ {fmt_moeda_br(x)}")

st.dataframe(
    tabela[
        [
            "Exercício",
            "Entidade",
            "Natureza da Despesa",
            "Descrição da Natureza",
            "Fonte de Recurso",
            "Valor Orçado",
            "Valor Atualizado",
            "Valor Empenhado",
        ]
    ],
    use_container_width=True
)

# =====================================================
# DOWNLOAD
# =====================================================
csv = tabela.to_csv(index=False, sep=";", encoding="utf-8")
st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="analise_por_natureza.csv",
    mime="text/csv"
)

st.caption("Análise por Natureza • Execução Orçamentária Consolidada")
