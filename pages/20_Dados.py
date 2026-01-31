import streamlit as st
import pandas as pd
import os
import re

# =====================================================
# Bloqueio de acesso e definição de perfis
# =====================================================

# Verifica se usuário está logado
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado! Faça login no sistema para acessar esta página.")
    st.stop()

# Perfis permitidos para esta página
PERFIS_PERMITIDOS = ["administrador"]

# Verifica se o perfil do usuário tem permissão
perfil_usuario = st.session_state.get("perfil", "")
if perfil_usuario not in PERFIS_PERMITIDOS:
    st.error(f"🚫 Acesso negado! Perfil '{perfil_usuario}' não tem permissão para acessar esta página.")
    st.stop()

st.set_page_config(
    page_title="Dados do Exercício",
    page_icon="📂",
    layout="wide"
)

st.header("📂 Dados do Exercício (visualização local)")

st.markdown(
    """
    Esta página apresenta os arquivos encontrados na pasta **data/**,
    permitindo a visualização prévia da estrutura dos dados
    antes da continuidade das análises.
    """
)

st.markdown("---")

DATA_PATH = "data"

if not os.path.exists(DATA_PATH):
    st.error("Pasta 'data/' não encontrada no projeto.")
    st.stop()

arquivos = [f for f in os.listdir(DATA_PATH) if f.lower().endswith(".csv")]

if not arquivos:
    st.warning("Nenhum arquivo CSV encontrado na pasta data/.")
    st.stop()

st.subheader("📄 Arquivos encontrados")
st.write(arquivos)

st.markdown("---")

def extrair_exercicio(nome):
    match = re.search(r"20\d{2}", nome)
    return match.group() if match else "Não identificado"

# Seleção do arquivo para visualização
arquivo_selecionado = st.selectbox(
    "Selecione um arquivo para visualização",
    arquivos
)

caminho = os.path.join(DATA_PATH, arquivo_selecionado)

st.markdown(f"**Exercício identificado:** {extrair_exercicio(arquivo_selecionado)}")

# Leitura do CSV
try:
    df = pd.read_csv(caminho, sep=";", encoding="utf-8")
except Exception as e:
    st.error(f"Erro ao ler o arquivo: {e}")
    st.stop()

st.markdown("---")

st.subheader("🧾 Estrutura do arquivo")
st.write(f"Linhas: {df.shape[0]} | Colunas: {df.shape[1]}")
st.write(list(df.columns))

st.markdown("---")

st.subheader("🔍 Visualização dos primeiros registros")
st.dataframe(df.head(20))