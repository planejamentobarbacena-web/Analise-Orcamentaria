import streamlit as st
import os
import pandas as pd
import requests
import base64

# =====================================================
# BLOQUEIO DE ACESSO
# =====================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado! Faça login no sistema para acessar esta página.")
    st.stop()

PERFIS_PERMITIDOS = ["administrador"]
perfil_usuario = st.session_state.get("perfil", "")
if perfil_usuario not in PERFIS_PERMITIDOS:
    st.error(f"🚫 Acesso negado! Perfil '{perfil_usuario}' não tem permissão para acessar esta página.")
    st.stop()

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Upload de Arquivos",
    page_icon="📤",
    layout="wide"
)

st.header("📤 Gerenciamento de Arquivos CSV")

# =====================================================
# CONFIGURAÇÃO GITHUB
# =====================================================
REPO = "planejamentobarbacena-web/analise-orcamentaria"
BRANCH = "main"

def enviar_para_github(caminho_arquivo, conteudo_bytes):
    token = st.secrets["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{REPO}/contents/{caminho_arquivo}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    # Verifica se o arquivo já existe
    response = requests.get(url, headers=headers)
    sha = None

    if response.status_code == 200:
        sha = response.json()["sha"]

    conteudo_base64 = base64.b64encode(conteudo_bytes).decode()

    data = {
        "message": f"Upload automático: {caminho_arquivo}",
        "content": conteudo_base64,
        "branch": BRANCH
    }

    if sha:
        data["sha"] = sha  # Necessário para sobrescrever

    response = requests.put(url, json=data, headers=headers)

    return response.status_code, response.json()

# =====================================================
# UPLOAD – BASES ORÇAMENTÁRIAS
# =====================================================
st.subheader("📊 Upload – Bases Orçamentárias")

uploaded_files = st.file_uploader(
    "Selecione arquivos CSV (orçada, atualizada, empenhada)",
    type="csv",
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        nome_arquivo = uploaded_file.name.strip()

        if not any(p in nome_arquivo.lower() for p in ["orcada", "atualizada", "empenhada"]):
            st.warning(f"❌ {nome_arquivo} fora do padrão esperado.")
            continue

        caminho_github = f"data/{nome_arquivo}"

        status, resposta = enviar_para_github(
            caminho_github,
            uploaded_file.getbuffer()
        )

        if status in [200, 201]:
            st.success(f"✅ {nome_arquivo} enviado ao GitHub com sucesso!")
        else:
            st.error(resposta)

# =====================================================
# LISTAGEM (via GitHub API)
# =====================================================
st.markdown("---")
st.subheader("📂 Arquivos no Repositório")

def listar_arquivos_github(pasta):
    token = st.secrets["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{REPO}/contents/{pasta}?ref={BRANCH}"

    headers = {
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        arquivos = [item["name"] for item in response.json() if item["type"] == "file"]
        return sorted(arquivos)

    return []

arquivos_repo = listar_arquivos_github("data")

if arquivos_repo:
    for arq in arquivos_repo:
        st.write("📄", arq)
else:
    st.info("Nenhum arquivo encontrado no repositório.")

# =====================================================
# VISUALIZAÇÃO
# =====================================================
st.markdown("---")
st.subheader("🔍 Visualizar Arquivo do GitHub")

arquivo_sel = st.selectbox("Selecione o arquivo", [""] + arquivos_repo)

if arquivo_sel:
    url_raw = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/data/{arquivo_sel}"
    df = pd.read_csv(url_raw, sep=";", dtype=str)
    st.dataframe(df.head(50), use_container_width=True)
