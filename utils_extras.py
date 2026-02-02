import os
import pandas as pd

# ==================================================
# CONFIGURAÇÃO
# ==================================================
DATA_DIR = "data/extras"
os.makedirs(DATA_DIR, exist_ok=True)

MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

COLUNAS = ["Exercício", "Competência", "Credor", "Fonte", "Repasse"]

# ==================================================
# CONVERSÃO MONETÁRIA (PT-BR BLINDADA)
# ==================================================
def moeda_para_float(valor):
    """
    Converte qualquer valor pt-BR para float:
    1.234.567,89 -> 1234567.89
    774.354,06   -> 774354.06
    7026,92      -> 7026.92
    """
    if pd.isna(valor):
        return 0.0

    valor = str(valor).strip()
    valor = valor.replace("R$", "").replace(" ", "")

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    else:
        valor = valor.replace(",", "")

    try:
        return float(valor)
    except ValueError:
        return 0.0


def float_para_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ==================================================
# CARREGAR EXTRAS
# ==================================================
def carregar_extras():
    dfs = []

    if not os.path.exists(DATA_DIR):
        return pd.DataFrame(columns=COLUNAS)

    for arq in os.listdir(DATA_DIR):
        if arq.startswith("extras_") and arq.endswith(".csv"):
            caminho = os.path.join(DATA_DIR, arq)

            df = pd.read_csv(
                caminho,
                sep=";",
                dtype=str,
                encoding="utf-8"
            )

            df.columns = [c.strip() for c in df.columns]

            df["Exercício"] = pd.to_numeric(df["Exercício"], errors="coerce")
            df["Competência"] = df["Competência"].str.upper().str.strip()
            df["Credor"] = df["Credor"].str.strip()
            df["Fonte"] = df["Fonte"].str.strip()
            df["Repasse"] = df["Repasse"].apply(moeda_para_float)

            dfs.append(df)

    if not dfs:
        return pd.DataFrame(columns=COLUNAS)

    df_final = pd.concat(dfs, ignore_index=True)
    df_final = df_final.dropna(subset=["Exercício"])

    df_final["Exercício"] = df_final["Exercício"].astype(int)

    return df_final

# ==================================================
# FILTROS
# ==================================================
def filtrar_extras(df, exercicios=None, credores=None, competencias=None):
    df_f = df.copy()

    if exercicios:
        df_f = df_f[df_f["Exercício"].isin(exercicios)]

    if credores:
        df_f = df_f[df_f["Credor"].isin(credores)]

    if competencias:
        df_f = df_f[df_f["Competência"].isin(competencias)]

    return df_f
