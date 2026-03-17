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
    page_title="Análise Orçamentária",
    page_icon="📊",
    layout="wide"
)

st.header("📊 Análise Orçamentária")

# =====================================================
# SECRETARIAS
# =====================================================
SECRETARIAS = {
    "18": "SESAP",
    "02": "CGM - AR",
    "03": "CGEM",
    "05": "SEGAB",
    "13": "SEAPA",
    "15": "SEGOV",
    "14": "SEDEC - AR",
    "16": "SEMOP",
    "17": "SEPLAN - AR",
    "19": "SEFAZ",
    "21": "GCM",
    "23": "AGM",
    "24": "SETRAM - AR",
    "25": "SEMAS",
    "26": "SEMAD",
    "27": "SEPLAN",
    "28": "SEMUR",
    "29": "SEDEC",
    "30": "SESP",
    "31": "SEMMA",
    "32": "SEDUC",
    "33": "SSP",
    "34": "SECULT",
    "35": "SEMESP"
}

# =====================================================
# IDENTIFICAR SECRETARIA
# =====================================================
def identificar_secretaria(org):

    if pd.isna(org):
        return "Não identificada"

    org = str(org).strip()

    cod2 = org[:2]
    cod1 = org[:1]

    if cod2 in SECRETARIAS:
        return SECRETARIAS[cod2]

    if cod1 in SECRETARIAS:
        return SECRETARIAS[cod1]

    return "Não identificada"


# =====================================================
# FORMATAÇÃO MOEDA
# =====================================================
def fmt_moeda_br(valor):
    if pd.isna(valor):
        return "0,00"
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# =====================================================
# FILTROS
# =====================================================
st.subheader("🎯 Filtros")

col1, col2, col3 = st.columns(3)

# -----------------------------------------------------
# EXERCÍCIO
# -----------------------------------------------------
with col1:

    exercicios = exercicios_disponiveis()

    sel_ex = st.multiselect(
        "Exercício",
        ["Todos"] + exercicios,
        default=["Todos"]
    )

    anos = exercicios if "Todos" in sel_ex else sel_ex


# =====================================================
# CARGA DE DADOS
# =====================================================
dfs = []

for ano in anos:
    try:
        df_ano = carregar_despesas(ano)
        df_ano["Exercício"] = ano
        dfs.append(df_ano)
    except:
        pass

if not dfs:
    st.warning("Nenhum dado encontrado.")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

# =====================================================
# IDENTIFICAR SECRETARIA
# =====================================================
df["Secretaria"] = df["Organograma_Codigo"].apply(identificar_secretaria)


# -----------------------------------------------------
# SECRETARIA
# -----------------------------------------------------
with col2:

    secretarias = ["Todas"] + sorted(df["Secretaria"].unique())

    secretaria_sel = st.selectbox(
        "Secretaria",
        secretarias
    )

    if secretaria_sel != "Todas":
        df = df[df["Secretaria"] == secretaria_sel]


# -----------------------------------------------------
# RECURSO
# -----------------------------------------------------
with col3:

    recursos = ["Todos"] + sorted(df["Recurso"].dropna().unique())

    recurso_sel = st.selectbox(
        "Fonte de Recurso",
        recursos
    )

    if recurso_sel != "Todos":
        df = df[df["Recurso"] == recurso_sel]


# -----------------------------------------------------
# SEGUNDA LINHA – AÇÃO
# -----------------------------------------------------
acoes = ["Todas"] + sorted(df["Descrição da ação"].dropna().unique())

acoes_sel = st.multiselect(
    "Descrição da Ação",
    acoes,
    default=["Todas"]
)

if "Todas" not in acoes_sel:
    df = df[df["Descrição da ação"].isin(acoes_sel)]


# =====================================================
# AGREGAÇÃO
# =====================================================
df_ag = (
    df
    .groupby(
        [
            "Exercício",
            "Secretaria",
            "Número da ação",
            "Descrição da ação",
            "Recurso"
        ],
        as_index=False
    )[["valor_orcado", "valor_atualizado", "valor_empenhado"]]
    .sum()
)


# =====================================================
# GRÁFICO
# =====================================================
st.markdown("---")
st.subheader("📊 Comparativo Orçamentário")

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

grafico = (
    alt.Chart(df_long)
    .mark_bar(size=30)
    .encode(
        x=alt.X("Exercício:N", title="Exercício"),
        xOffset=alt.XOffset("Tipo:N", sort=ordem),
        y=alt.Y("Valor:Q", title="Valor"),
        color=alt.Color(
            "Tipo:N",
            sort=ordem,
            scale=alt.Scale(
                domain=ordem,
                range=["#000080", "#00CEC8", "#FF2C2C"]
            )
        ),
        tooltip=["Exercício", "Tipo", "Valor"]
    )
    .properties(height=420)
)

st.altair_chart(grafico, use_container_width=True)


# =====================================================
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Detalhamento")

tabela = df_ag.rename(columns={
    "Descrição da ação": "Descrição da Ação",
    "Recurso": "Fonte de Recurso",
    "valor_orcado": "Valor Orçado",
    "valor_atualizado": "Valor Atualizado",
    "valor_empenhado": "Valor Empenhado"
})

for col in ["Valor Orçado", "Valor Atualizado", "Valor Empenhado"]:
    tabela[col] = tabela[col].apply(lambda x: f"R$ {fmt_moeda_br(x)}")

st.dataframe(tabela, use_container_width=True)


# =====================================================
# DOWNLOAD
# =====================================================
csv = tabela.to_csv(index=False, sep=";", encoding="utf-8")

st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="analise_orcamentaria.csv",
    mime="text/csv"
)
