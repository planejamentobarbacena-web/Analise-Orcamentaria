import streamlit as st
import os
import pandas as pd

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
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Upload de Arquivos",
    page_icon="📤",
    layout="wide"
)

st.header("📤 Gerenciamento de Arquivos CSV")

# =====================================================
# PASTAS
# =====================================================
PASTA_DATA = "data"
PASTA_EXTRAS = "data/extras"

os.makedirs(PASTA_DATA, exist_ok=True)
os.makedirs(PASTA_EXTRAS, exist_ok=True)

# =====================================================
# UPLOAD BASES ORÇAMENTÁRIAS
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

        if not any(p in nome_arquivo for p in ["orçada", "atualizada", "empenhada"]):
            st.warning(f"❌ {nome_arquivo} fora do padrão esperado.")
            continue

        caminho = os.path.join(PASTA_DATA, nome_arquivo)
        with open(caminho, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ {nome_arquivo} salvo com sucesso.")

# =====================================================
# LISTAGEM E EXCLUSÃO
# =====================================================
st.markdown("---")
st.subheader("📂 Arquivos Disponíveis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Bases Orçamentárias")
    arquivos_data = sorted(os.listdir(PASTA_DATA))
    if arquivos_data:
        for arq in arquivos_data:
            c1, c2 = st.columns([4, 1])
            c1.write(arq)
            if c2.button("🗑️", key=f"del_data_{arq}"):
                os.remove(os.path.join(PASTA_DATA, arq))
                st.success(f"{arq} removido.")
                st.rerun()
    else:
        st.info("Nenhum arquivo encontrado.")

with col2:
    st.markdown("### ➕ Extras (gerados pelo cadastro)")
    arquivos_extras = sorted(os.listdir(PASTA_EXTRAS))
    if arquivos_extras:
        for arq in arquivos_extras:
            c1, c2 = st.columns([4, 1])
            c1.write(arq)
            if c2.button("🗑️", key=f"del_extra_{arq}"):
                os.remove(os.path.join(PASTA_EXTRAS, arq))
                st.success(f"{arq} removido.")
                st.rerun()
    else:
        st.info("Nenhum arquivo de extras.")

# =====================================================
# VISUALIZAÇÃO (OPCIONAL)
# =====================================================
st.markdown("---")
st.subheader("🔍 Visualizar Arquivo")

tipo = st.radio("Tipo de Arquivo", ["Bases", "Extras"], horizontal=True)

if tipo == "Bases":
    arquivos = arquivos_data
    pasta = PASTA_DATA
else:
    arquivos = arquivos_extras
    pasta = PASTA_EXTRAS

arquivo_sel = st.selectbox("Selecione o arquivo", [""] + arquivos)

if arquivo_sel:
    df = pd.read_csv(os.path.join(pasta, arquivo_sel), sep=";", dtype=str)
    st.dataframe(df.head(50), use_container_width=True)
