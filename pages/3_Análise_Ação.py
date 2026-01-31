import streamlit as st
import pandas as pd
import altair as alt
from utils import exercicios_disponiveis, carregar_despesas

# =====================================================
# BLOQUEIO DE ACESSO E PERFIS
# =====================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado! Faça login no sistema para acessar esta página.")
    st.stop()

PERFIS_PERMITIDOS = ["administrador", "consulta"]
perfil_usuario = st.session_state.get("perfil", "")
if perfil_usuario not in PERFIS_PERMITIDOS:
    st.error("🚫 Seu perfil não tem permissão para acessar esta página.")
    st.stop()

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
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

col1, col2 = st.columns(2)

exercicios = exercicios_disponiveis()
opcoes_exercicio = ["Todos"] + exercicios
exercicio_sel = col1.multiselect(
    "Exercício",
    options=opcoes_exercicio,
    default=["Todos"]
)

exercicios_escolhidos = exercicios if "Todos" in exercicio_sel else exercicio_sel

# =====================================================
# CARGA DOS DADOS
# =====================================================
dfs = []

for ano in exercicios_escolhidos:
    try:
        df_ano = carregar_despesas(ano)
        df_ano["Exercício"] = ano
        dfs.append(df_ano)
    except Exception as e:
        st.warning(f"Ano {ano} ignorado: {e}")

if not dfs:
    st.warning("Nenhum dado encontrado.")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

# =====================================================
# NORMALIZAÇÃO
# =====================================================
for col in [
    "Entidade",
    "Número da ação",
    "Descrição da ação",
    "Recurso"
]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# =====================================================
# FILTRO ENTIDADE
# =====================================================
entidades = ["Todos"] + sorted(df["Entidade"].dropna().unique().tolist())
entidade_sel = col2.selectbox("Entidade", entidades)

if entidade_sel != "Todos":
    df = df[df["Entidade"] == entidade_sel]

# =====================================================
# FILTRO AÇÃO (DESCRIÇÃO – SOMENTE PARA LEITURA)
# =====================================================
acoes = ["Todos"] + sorted(df["Descrição da ação"].dropna().unique().tolist())
acoes_sel = st.multiselect(
    "Descrição da Ação",
    options=acoes,
    default=["Todos"]
)

if "Todos" not in acoes_sel:
    df = df[df["Descrição da ação"].isin(acoes_sel)]

# =====================================================
# FILTRO RECURSO
# =====================================================
recursos = ["Todos"] + sorted(df["Recurso"].dropna().unique().tolist())
recursos_sel = st.multiselect(
    "Fonte de Recurso",
    options=recursos,
    default=["Todos"]
)

if "Todos" not in recursos_sel:
    df = df[df["Recurso"].isin(recursos_sel)]

# =====================================================
# AGREGAÇÃO CORRETA
# (AÇÃO + RECURSO | NATUREZA IGNORADA)
# =====================================================
chaves = [
    "Exercício",
    "Entidade",
    "Número da ação",
    "Recurso"
]

df_agregado = (
    df
    .groupby(chaves, as_index=False)[
        ["valor_orcado", "valor_atualizado", "valor_empenhado"]
    ]
    .sum()
)

# Recupera descrição da ação apenas para exibição
descricao_acao = (
    df[["Número da ação", "Descrição da ação"]]
    .drop_duplicates()
)

df_agregado = df_agregado.merge(
    descricao_acao,
    on="Número da ação",
    how="left"
)

# =====================================================
# GRÁFICO – VISÃO GERAL POR EXERCÍCIO
# =====================================================
st.markdown("---")
st.subheader("📊 Comparativo Orçamentário por Exercício")

df_grafico = (
    df_agregado
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
df_long["Tipo"] = pd.Categorical(df_long["Tipo"], categories=ordem_tipo, ordered=True)
df_long["Valor_fmt"] = df_long["Valor"].apply(fmt_moeda_br)

grafico = (
    alt.Chart(df_long)
    .mark_bar()
    .encode(
        x=alt.X("Exercício:N", title="Exercício"),
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

# =====================================================
# TABELA DETALHADA
# =====================================================
st.markdown("---")
st.subheader("📋 Detalhamento por Ação e Fonte de Recurso")

tabela = df_agregado.rename(columns={
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
# DOWNLOAD CSV
# =====================================================
csv = tabela.to_csv(index=False, sep=";", encoding="utf-8")
st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="analise_por_acao.csv",
    mime="text/csv"
)

st.caption("Análise por Ação • Execução Orçamentária Consolidada")