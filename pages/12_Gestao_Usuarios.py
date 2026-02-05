import streamlit as st
import pandas as pd
import os

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


DATA_DIR = "data"
ARQ_USUARIOS = os.path.join(DATA_DIR, "usuarios.csv")
os.makedirs(DATA_DIR, exist_ok=True)

COLUNAS = ["usuario", "senha", "perfil"]

# =====================================================
# CARREGAR / CRIAR CSV
# =====================================================
def carregar_usuarios():
    if not os.path.exists(ARQ_USUARIOS):
        df = pd.DataFrame(columns=COLUNAS)
        df.to_csv(ARQ_USUARIOS, index=False)
        return df
    return pd.read_csv(ARQ_USUARIOS, dtype=str)

def salvar_usuarios(df):
    df.to_csv(ARQ_USUARIOS, index=False)

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
        salvar_usuarios(df_usuarios)

        st.session_state.msg_sucesso = "Usuário cadastrado com sucesso."
        st.rerun()

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
            salvar_usuarios(df_usuarios)
            st.session_state.msg_sucesso = f"Usuário {row['usuario']} removido."
            st.rerun()

