import streamlit as st
import pandas as pd
import requests
import base64

# =====================================================
# SEGURANÇA
# =====================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado.")
    st.stop()

if st.session_state.get("perfil") != "administrador":
    st.error("🚫 Apenas administradores podem acessar esta página.")
    st.stop()

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Gestão de Usuários",
    page_icon="👥",
    layout="centered"
)

st.header("👥 Gestão de Usuários")

if "msg_sucesso" in st.session_state:
    st.success(f"✅ {st.session_state.msg_sucesso}")
    del st.session_state.msg_sucesso

COLUNAS = ["usuario", "senha", "perfil"]

# =====================================================
# CONFIG GITHUB
# =====================================================
REPO = "planejamentobarbacena-web/analise-orcamentaria"
BRANCH = "main"
CAMINHO_GITHUB = "data/usuarios.csv"

def carregar_usuarios():
    url_raw = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{CAMINHO_GITHUB}"
    try:
        return pd.read_csv(url_raw, dtype=str)
    except:
        return pd.DataFrame(columns=COLUNAS)

def salvar_no_github(df):
    token = st.secrets["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{REPO}/contents/{CAMINHO_GITHUB}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    # Verifica se arquivo já existe
    response = requests.get(url, headers=headers)
    sha = None

    if response.status_code == 200:
        sha = response.json()["sha"]

    csv_bytes = df.to_csv(index=False).encode()
    conteudo_base64 = base64.b64encode(csv_bytes).decode()

    data = {
        "message": "Atualização automática: usuarios.csv",
        "content": conteudo_base64,
        "branch": BRANCH
    }

    if sha:
        data["sha"] = sha

    response = requests.put(url, json=data, headers=headers)
    return response.status_code

df_usuarios = carregar_usuarios()

# =====================================================
# CADASTRO
# =====================================================
st.subheader("➕ Cadastrar Novo Usuário")

with st.form("form_usuario", clear_on_submit=True):
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox(
        "Perfil",
        ["", "consulta", "administrador"]
    )

    salvar = st.form_submit_button("💾 Cadastrar")

if salvar:
    if not usuario or not senha or not perfil:
        st.warning("⚠️ Preencha todos os campos.")
    elif usuario in df_usuarios["usuario"].values:
        st.error("❌ Usuário já existe.")
    else:
        novo = pd.DataFrame([{
            "usuario": usuario,
            "senha": senha,
            "perfil": perfil
        }])

        df_usuarios = pd.concat([df_usuarios, novo], ignore_index=True)

        status = salvar_no_github(df_usuarios)

        if status in [200, 201]:
            st.session_state.msg_sucesso = "Usuário cadastrado com sucesso."
            st.rerun()
        else:
            st.error("Erro ao salvar no GitHub.")

# =====================================================
# LISTAGEM E EXCLUSÃO
# =====================================================
st.markdown("---")
st.subheader("📋 Usuários Cadastrados")

if df_usuarios.empty:
    st.info("Nenhum usuário cadastrado.")
else:
    for _, row in df_usuarios.iterrows():
        col1, col2, col3, col4 = st.columns([3, 3, 3, 1])

        col1.write(row["usuario"])
        col2.write("••••••")
        col3.write(row["perfil"])

        if col4.button("🗑️", key=f"del_{row['usuario']}"):
            df_usuarios = df_usuarios[df_usuarios["usuario"] != row["usuario"]]

            status = salvar_no_github(df_usuarios)

            if status in [200, 201]:
                st.session_state.msg_sucesso = f"Usuário {row['usuario']} removido."
                st.rerun()
            else:
                st.error("Erro ao atualizar GitHub.")
