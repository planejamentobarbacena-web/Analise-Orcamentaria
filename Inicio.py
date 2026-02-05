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
        font-size: 3.4rem;
        font-weight: 700;
        color: #1f77b4;
        margin-top: 0;
        margin-bottom: 0.4rem;
    }
    .subtitulo-central {
        text-align: center;
        font-size: 1.05rem;
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
        pd.DataFrame(
            columns=["usuario", "senha", "perfil"]
        ).to_csv(USUARIOS_CSV, index=False)

    df = pd.read_csv(USUARIOS_CSV).fillna("")
    for c in ["usuario", "senha", "perfil"]:
        df[c] = df[c].astype(str).str.strip()
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
if "destino" not in st.session_state:
    st.session_state.destino = None

# =====================================================
# LOGOUT
# =====================================================
def logout():
    st.session_state.clear()
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

    if st.button("Entrar", use_container_width=True):
        ok, dados = autenticar(usuario, senha)
        if ok:
            st.session_state.logado = True
            st.session_state.usuario = dados["usuario"]
            st.session_state.perfil = dados["perfil"]
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.stop()

# =====================================================
# NAVEGAÇÃO VIA QUERY PARAM
# =====================================================
params = st.experimental_get_query_params()
if "page" in params and params["page"]:
    st.session_state.destino = params["page"][0]
    st.experimental_set_query_params()  # limpa a URL
    st.experimental_rerun()

# Se houver destino definido, redireciona para o módulo correspondente
if st.session_state.destino:
    destino = st.session_state.pop("destino")  # remove após usar
    try:
        # importa a página correspondente da pasta pages
        page_module = destino.replace(".py", "")
        page_path = f"pages.{page_module}"
        # Import dinâmico
        mod = __import__(page_path, fromlist=[page_module])
        st.stop()  # interrompe esta página
    except Exception as e:
        st.error(f"Não foi possível abrir a página {destino}: {e}")
        st.session_state.destino = None

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
# FUNÇÃO CARD
# =====================================================
def card_modulo(titulo, descricao, pagina):
    chave = f"btn_{pagina.replace('.py','')}"
    with st.container():
        st.markdown(f"### {titulo}")
        st.caption(descricao)
        if st.button("Acessar", key=chave, use_container_width=True):
            st.experimental_set_query_params(page=pagina)
            st.experimental_rerun()

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
