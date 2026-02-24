import streamlit as st
import pandas as pd
import altair as alt

from utils import exercicios_disponiveis, carregar_despesas

# =====================================================
# SEGURANÇA
# =====================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado!")
    st.stop()

if st.session_state.get("perfil") not in ["administrador", "consulta"]:
    st.error("🚫 Perfil sem permissão.")
    st.stop()

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Análise por Ação",
    page_icon="📌",
    layout="wide"
)

st.header("📌 Análise Orçamentária por Ação")

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
    default=st.session_state.get("acao_exercicio", ["Todos"]),
    key="acao_exercicio"
)

anos = exercicios if "Todos" in sel_ex else sel_ex

# =====================================================
# CARGA DOS DADOS
# =====================================================
dfs = []

for ano in anos:
    try:
        df_ano = carregar_despesas(ano)
        df_ano["Exercício"] = ano
        dfs.append(df_ano)
    except Exception:
        pass

if not dfs:
    st.warning("Nenhum dado encontrado.")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

# =====================================================
# NORMALIZAÇÃO
# =====================================================
for col in ["Entidade", "Número da ação", "Descrição da ação", "Recurso"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# -----------------------------------------------------
# ENTIDADE (FILTRO LIVRE)
# -----------------------------------------------------
entidades = ["Todos"] + sorted(df["Entidade"].dropna().unique())

valor_atual = st.session_state.get("acao_entidade", "Todos")
if valor_atual not in entidades:
    valor_atual = "Todos"

entidade_sel = st.selectbox(
    "Entidade",
    entidades,
    index=entidades.index(valor_atual),
    key="acao_entidade"
)

if entidade_sel != "Todos":
    df = df[df["Entidade"] == entidade_sel]

# -----------------------------------------------------
# AÇÃO (FILTRO LIVRE)
# -----------------------------------------------------
acoes = ["Todos"] + sorted(df["Descrição da ação"].dropna().unique())

valor_atual = st.session_state.get("acao_desc", ["Todos"])
if not set(valor_atual).intersection(acoes):
    valor_atual = ["Todos"]

acoes_sel = st.multiselect(
    "Descrição da Ação",
    options=acoes,
    default=valor_atual,
    key="acao_desc"
)

if "Todos" not in acoes_sel:
    df = df[df["Descrição da ação"].isin(acoes_sel)]

# -----------------------------------------------------
# RECURSO (FILTRO LIVRE)
# -----------------------------------------------------
recursos = ["Todos"] + sorted(df["Recurso"].dropna().unique())

valor_atual = st.session_state.get("acao_recurso", ["Todos"])
if not set(valor_atual).intersection(recursos):
    valor_atual = ["Todos"]

recursos_sel = st.multiselect(
    "Fonte de Recurso",
    options=recursos,
    default=valor_atual,
    key="acao_recurso"
)

if "Todos" not in recursos_sel:
    df = df[df["Recurso"].isin(recursos_sel)]

# =====================================================
# AGREGAÇÃO
# =====================================================
chaves = [
    "Exercício",
    "Entidade",
    "Número da ação",
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
    df[["Número da ação", "Descrição da ação"]]
    .drop_duplicates()
)

df_ag = df_ag.merge(
    descricao,
    on="Número da ação",
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
st.subheader("📋 Detalhamento por Ação e Fonte de Recurso")

tabela = df_ag.rename(columns={
    "Descrição da ação": "Descrição da Ação",
    "Recurso": "Fonte de Recurso",
    "valor_orcado": "Valor Orçado",
    "valor_atualizado": "Valor Atualizado",
    "valor_empenhado": "Valor Empenhado",
})

for col in ["Valor Orçado", "Valor Atualizado", "Valor Empenhado"]:
    tabela[col] = tabela[col].apply(lambda x: f"R$ {fmt_moeda_br(x)}")

st.dataframe(
    tabela[
        [
            "Exercício",
            "Entidade",
            "Número da ação",
            "Descrição da Ação",
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
    file_name="analise_por_acao.csv",
    mime="text/csv"
)

st.caption("Análise por Ação • Execução Orçamentária Consolidada")
