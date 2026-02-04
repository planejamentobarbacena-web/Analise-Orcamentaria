import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURAÇÃO GERAL
# =====================================================
st.set_page_config(
    page_title="Análise Orçamentária",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# ESTILO
# =====================================================
st.markdown("""
<style>
    .titulo-central {
        text-align: center;
        font-size: 3.6rem;
        font-weight: 700;
        color: #1f77b4;
        margin-top: 0;
        margin-bottom: 0.5rem;
    }
    .subtitulo-central {
        text-align: center;
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CSV DE USUÁRIOS
# =====================================================
USUARIOS_CSV = "data/usuarios.csv"

def carregar_usuarios():
    if not os.path.exists(USUARIOS_CSV):
        os.makedirs(os.path.dirname(USUARIOS_CSV), exist_ok=True)
        df = pd.DataFrame(columns=["usuario", "senha", "perfil"])
        df.to_csv(USUARIOS_CSV, index=False)

    df = pd.read_csv(USUARIOS_CSV).fillna("")

    df["usuario"] = df["usuario"].astype(str).str.strip()
    df["senha"] = df["senha"].astype(str).str.strip()
    df["perfil"] = df["perfil"].astype(str).str.strip()

    return df


def autenticar(usuario, senha):
    df = carregar_usuarios()
    user = df[
        (df["usuario"].str.lower() == usuario.lower()) &
        (df["senha"] == senha)
    ]
    if user.empty:
        return False, None
    return True, user.iloc[0]

# =====================================================
# CONTROLE DE SESSÃO
# =====================================================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "perfil" not in st.session_state:
    st.session_state.perfil = None

# =====================================================
# LOGOUT
# =====================================================
def logout():
    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.perfil = None
    st.rerun()

# =====================================================
# LOGIN
# =====================================================
if not st.session_state.logado:
    st.title("🔐 Login do Sistema")

    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuário")
    with col2:
        senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        ok, dados = autenticar(usuario, senha)
        if ok:
            st.session_state.logado = True
            st.session_state.usuario = dados["usuario"]
            st.session_state.perfil = dados["perfil"]
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.stop()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.success(f"👤 {st.session_state.usuario}")
st.sidebar.write(f"Perfil: **{st.session_state.perfil}**")

if st.sidebar.button("🚪 Sair"):
    logout()

# =====================================================
# TELA PRINCIPAL
# =====================================================
st.markdown('<div class="titulo-central">Análise Orçamentária</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitulo-central">Escolha o módulo que deseja acessar</div>',
    unsafe_allow_html=True
)
st.markdown("---")

# =====================================================
# FUNÇÃO DE CARD
# =====================================================
def card_modulo(titulo, descricao, pagina):
    chave = f"btn_{pagina.replace('/', '_').replace('.py','')}"
    with st.container():
        st.markdown(f"### {titulo}")
        st.caption(descricao)
        if st.button("Acessar", key=chave, use_container_width=True):
            st.experimental_set_query_params(page=f"pages/{pagina}")
            st.rerun()

# =====================================================
# GRID DE CARDS
# =====================================================
col1, col2, col3 = st.columns(3)

with col1:
    card_modulo(
        "📊 Visão Geral",
        "Resumo consolidado e indicadores",
        "2_Visão_Geral.py"
    )

with col2:
    card_modulo(
        "🔍 Análise por Ação",
        "Detalhamento por Ação Orçamentária",
        "3_Análise_Ação.py"
    )

with col3:
    card_modulo(
        "🧾 Análise por Natureza",
        "Classificação por Natureza da Despesa",
        "4_Análise_Natureza.py"
    )

st.markdown("---")

col4, col5, col6 = st.columns(3)

with col4:
    card_modulo(
        "💰 Metas de Receitas",
        "Acompanhamento das Metas de Arrecadação",
        "5_Metas_Receitas.py"
    )

with col5:
    card_modulo(
        "🏦 Metas por Recursos",
        "Metas por Fonte de Recurso",
        "6_Metas_Recursos.py"
    )

with col6:
    card_modulo(
        "🏛️ Extras – Indiretas",
        "Repasses às Administrações Indiretas",
        "7_Extras_Indiretas.py"
    )




