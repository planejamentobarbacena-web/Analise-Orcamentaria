import streamlit as st
import pandas as pd
from utils import exercicios_disponiveis, carregar_despesas_por_natureza

# =====================================================
# SEGURANÇA
# =====================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado.")
    st.stop()

if st.session_state.get("perfil") not in ["administrador", "consulta"]:
    st.error("🚫 Perfil sem permissão.")
    st.stop()

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Legendar Natureza da Despesa",
    page_icon="📘",
    layout="wide"
)

st.header("📘 Legenda da Natureza da Despesa")
st.caption("Consulta rápida para identificar o significado de um código de natureza.")

# =====================================================
# EXERCÍCIO
# =====================================================
exercicios = exercicios_disponiveis()

exercicio = st.selectbox(
    "Exercício",
    exercicios,
    key="leg_nat_exercicio"
)

# =====================================================
# CARGA DO ARQUIVO DO ANO
# =====================================================
try:
    df = carregar_despesas_por_natureza(exercicio)
except Exception:
    st.error("Não foi possível carregar o arquivo do exercício.")
    st.stop()

# Base única de naturezas
base_nat = (
    df[["Natureza_Normalizada", "Descrição da Natureza"]]
    .dropna()
    .drop_duplicates()
    .sort_values("Natureza_Normalizada")
)

# =====================================================
# SELEÇÃO DA NATUREZA
# =====================================================
naturezas = base_nat["Natureza_Normalizada"].tolist()

natureza_sel = st.selectbox(
    "Natureza da Despesa (código)",
    naturezas,
    key="leg_nat_codigo"
)

# =====================================================
# RESULTADO
# =====================================================
resultado = base_nat[
    base_nat["Natureza_Normalizada"] == natureza_sel
]

st.markdown("---")
st.subheader("📖 Descrição")

if not resultado.empty:
    descricao = resultado.iloc[0]["Descrição da Natureza"]

    st.info(f"**{natureza_sel}**\n\n{descricao}")

    st.dataframe(resultado, use_container_width=True)
else:
    st.warning("Descrição não encontrada para este código.")

st.caption("Legenda de Natureza • Consulta rápida por exercício")
