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
    page_title="Análise por Secretaria",
    page_icon="🏛️",
    layout="wide"
)

st.header("🏛️ Análise Orçamentária por Secretaria")

# =====================================================
# TABELA DE SECRETARIAS
# =====================================================
SECRETARIAS = {
    "18": "SESAP",
    "3": "CGEM",
    "5": "SEGAB",
    "13": "SEAPA",
    "15": "SEGOV",
    "16": "SEMOP",
    "19": "SEFAZ",
    "23": "AGM",
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

# =====================================================
# FILTRO SECRETARIA
# =====================================================
secretarias = ["Todas"] + sorted(df["Secretaria"].unique())

secretaria_sel = st.selectbox(
    "Secretaria",
    secretarias
)

if secretaria_sel != "Todas":
    df = df[df["Secretaria"] == secretaria_sel]


# =====================================================
# AGREGAÇÃO
# =====================================================
df_ag = (
    df
    .groupby(["Exercício", "Secretaria"], as_index=False)[
        ["valor_orcado", "valor_atualizado", "valor_empenhado"]
    ]
    .sum()
)

# =====================================================
# GRÁFICO
# =====================================================
st.markdown("---")
st.subheader("📊 Comparativo Orçamentário")

df_long = df_ag.melt(
    id_vars=["Exercício","Secretaria"],
    value_vars=["valor_orcado","valor_atualizado","valor_empenhado"],
    var_name="Tipo",
    value_name="Valor"
)

df_long["Tipo"] = df_long["Tipo"].map({
    "valor_orcado":"Orçada",
    "valor_atualizado":"Atualizada",
    "valor_empenhado":"Empenhada"
})

grafico = (
    alt.Chart(df_long)
    .mark_bar(size=25)
    .encode(
        x=alt.X("Exercício:N", title="Exercício"),
        y=alt.Y("Valor:Q", title="Valor"),
        color=alt.Color(
            "Tipo:N",
            sort=["Orçada","Atualizada","Empenhada"],
            scale=alt.Scale(
                domain=["Orçada","Atualizada","Empenhada"],
                range=["#4CAF50","#2196F3","#FF9800"]
            )
        ),
        xOffset=alt.XOffset(
            "Tipo:N",
            sort=["Orçada","Atualizada","Empenhada"]
        ),
        tooltip=["Exercício","Tipo","Valor"]
    )
    .properties(height=420)
)

st.altair_chart(grafico, use_container_width=True)

# =====================================================
# TABELA
# =====================================================
st.markdown("---")
st.subheader("📋 Detalhamento por Secretaria")

tabela = df_ag.rename(columns={
    "valor_orcado":"Valor Orçado",
    "valor_atualizado":"Valor Atualizado",
    "valor_empenhado":"Valor Empenhado"
})

for col in ["Valor Orçado","Valor Atualizado","Valor Empenhado"]:
    tabela[col] = tabela[col].apply(lambda x: f"R$ {fmt_moeda_br(x)}")

st.dataframe(tabela, use_container_width=True)

# =====================================================
# DOWNLOAD
# =====================================================
csv = tabela.to_csv(index=False, sep=";", encoding="utf-8")

st.download_button(
    "⬇️ Baixar CSV",
    csv,
    file_name="analise_secretaria.csv",
    mime="text/csv"
)
