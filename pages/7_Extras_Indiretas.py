# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Repasses", layout="wide")

st.title("Análise de Repasses")

# --- CARREGAR DADOS ---
# Substitua pelo seu CSV ou planilha
@st.cache_data
def carregar_dados(caminho):
    df = pd.read_csv(caminho)
    # Garantir Repasse como float
    df["Repasse"] = df["Repasse"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
    return df

# Exemplo: CSV local
dados = carregar_dados("repasses.csv")

# --- FILTROS ---
exercicios = sorted(dados["Exercício"].unique())
credor_options = sorted(dados["Credor"].unique())

exercicio_selecionado = st.sidebar.multiselect("Selecione Exercício", exercicios, default=exercicios)
credor_selecionado = st.sidebar.multiselect("Selecione Credor", credor_options, default=credor_options)

filtrado = dados[(dados["Exercício"].isin(exercicio_selecionado)) & 
                 (dados["Credor"].isin(credor_selecionado))]

# --- AGRUPAR PARA GRÁFICO ---
ordem_comp = ["JANEIRO","FEVEREIRO","MARÇO","ABRIL","MAIO","JUNHO",
              "JULHO","AGOSTO","SETEMBRO","OUTUBRO","NOVEMBRO","DEZEMBRO"]

filtrado["Competência"] = pd.Categorical(filtrado["Competência"], categories=ordem_comp, ordered=True)

agrupado = filtrado.groupby(["Exercício","Competência","Credor"], as_index=False).agg({"Repasse":"sum"})
agrupado = agrupado.sort_values(["Exercício","Competência"])

# --- GRÁFICO ---
fig = px.bar(
    agrupado,
    x="Competência",
    y="Repasse",
    color="Exercício",
    text=agrupado["Repasse"],
    barmode="group",
    hover_data=["Credor"]
)
fig.update_layout(yaxis_title="Repasse (R$)", xaxis_title="Competência")
st.plotly_chart(fig, use_container_width=True)

# --- TABELA FILTRADA ---
st.subheader("Tabela de Repasses")
st.dataframe(filtrado.sort_values(["Exercício","Competência"]))
