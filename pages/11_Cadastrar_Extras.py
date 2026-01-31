import streamlit as st
import re
from utils_extras import inserir_repasse

# ==================================================
# SEGURANÇA
# ==================================================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Acesso negado.")
    st.stop()

if st.session_state.get("perfil") != "administrador":
    st.error("🚫 Apenas administradores podem cadastrar repasses.")
    st.stop()

# ==================================================
# CONFIGURAÇÃO
# ==================================================
st.set_page_config(
    page_title="Cadastro – Repasse Indireta",
    page_icon="📝",
    layout="centered"
)

st.header("📝 Cadastro de Repasse – Administração Indireta")
st.caption("Inclusão manual de repasses (gravado diretamente no CSV)")

# ==================================================
# LISTAS
# ==================================================
COMPETENCIAS = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

CREDORES = [""] + ["SAS", "CÂMARA", "SIMPAS"]

FONTES = [""] + [
    "1.500.000.0000",
    "1.501.000.0000",
    "1.753.000.0000",
    "2.500.000.0000",
    "2.501.000.0000",
    "2.753.000.0000"
]

# ==================================================
# FUNÇÃO DE CONVERSÃO (SEGURA)
# ==================================================
def converter_valor_br(valor_str):
    if not valor_str:
        return None

    valor_str = valor_str.strip()

    padrao = r'^R?\$?\s?\d{1,3}(\.\d{3})*(,\d{2})?$|^\d+(,\d{2})?$'
    if not re.match(padrao, valor_str):
        raise ValueError("Formato inválido")

    valor_str = (
        valor_str.replace("R$", "")
                 .replace(" ", "")
                 .replace(".", "")
                 .replace(",", ".")
    )

    return float(valor_str)

# ==================================================
# FORMULÁRIO
# ==================================================
st.markdown("---")
st.subheader("📋 Dados do Repasse")

col1, col2 = st.columns(2)

exercicio = col1.number_input(
    "Exercício",
    min_value=2020,
    max_value=2100,
    value=st.session_state.get("exercicio", 2025),
    step=1,
    key="exercicio"
)

competencia = col2.selectbox(
    "Competência",
    COMPETENCIAS,
    key="competencia"
)

credor = st.selectbox(
    "Credor",
    CREDORES,
    key="credor"
)

fonte = st.selectbox(
    "Fonte",
    FONTES,
    key="fonte"
)

valor_str = st.text_input(
    "Valor do Repasse",
    placeholder="Ex: 1.234,56",
    key="valor"
)

# ==================================================
# BOTÃO
# ==================================================
salvar = st.button("💾 Salvar Repasse")

# ==================================================
# SALVAMENTO + LIMPEZA
# ==================================================
if salvar:
    try:
        valor = converter_valor_br(valor_str)

        if not credor:
            st.warning("⚠️ Selecione um credor.")
        elif not fonte:
            st.warning("⚠️ Selecione uma fonte.")
        elif valor is None or valor <= 0:
            st.warning("⚠️ Informe um valor válido.")
        else:
            inserir_repasse(
                exercicio=exercicio,
                competencia=competencia,
                credor=credor,
                fonte=fonte,
                repasse=valor
            )

            st.success("✅ Repasse cadastrado com sucesso.")
    
            st.rerun()

    except ValueError:
        st.error("❌ Valor inválido. Use o formato 1.234,56")
