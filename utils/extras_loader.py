import os
import pandas as pd

# ==================================================
# CONFIGURAÇÃO
# ==================================================
DATA_DIR = "data/extras"

MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

COLUNAS_OBRIGATORIAS = [
    "Exercício",
    "Competência",
    "Credor",
    "Fonte",
    "Repasse"
]

# ==================================================
# FORMATADOR
# ==================================================
def float_para_moeda(valor):
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

# ==================================================
# CARGA
# ==================================================
def carregar_extras():
    if not os.path.exists(DATA_DIR):
        return pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)

    arquivos = [
        f for f in os.listdir(DATA_DIR)
        if f.startswith("extras_") and f.endswith(".csv")
    ]

    dfs = []

    for arq in arquivos:
        caminho = os.path.join(DATA_DIR, arq)

        df = pd.read_csv(
            caminho,
            sep=";",
            dtype=str,
            encoding="utf-8"
        )

        df.columns = df.columns.str.strip()

        if not set(COLUNAS_OBRIGATORIAS).issubset(df.columns):
            continue

        df["Exercício"] = (
            df["Exercício"]
            .str.replace(r"\D", "", regex=True)
            .astype(int)
        )

        df["Competência"] = df["Competência"].str.upper().str.strip()
        df["Credor"] = df["Credor"].str.strip()
        df["Fonte"] = df["Fonte"].str.strip()

        df["Repasse"] = (
            df["Repasse"]
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        dfs.append(df[COLUNAS_OBRIGATORIAS])

    if not dfs:
        return pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)

    return pd.concat(dfs, ignore_index=True)

# ==================================================
# FILTRO
# ==================================================
def filtrar_extras(
    df,
    exercicios=None,
    credores=None,
    competencias=None,
    fontes=None
):
    df_f = df.copy()

    if exercicios:
        df_f = df_f[df_f["Exercício"].isin(exercicios)]

    if credores:
        df_f = df_f[df_f["Credor"].isin(credores)]

    if competencias:
        df_f = df_f[df_f["Competência"].isin(competencias)]

    if fontes:
        df_f = df_f[df_f["Fonte"].isin(fontes)]

    return df_f
