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
# CARREGAMENTO ÚNICO E CONFIÁVEL
# ==================================================
def carregar_extras():
    """
    Lê todos os arquivos extras_XXXX.csv da pasta data/extras
    Retorna DataFrame com:
    - Exercício: int
    - Competência: str (MAIÚSCULO)
    - Credor: str
    - Fonte: str
    - Repasse: float
    """

    if not os.path.exists(DATA_DIR):
        return pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)

    arquivos = [
        f for f in os.listdir(DATA_DIR)
        if f.startswith("extras_") and f.endswith(".csv")
    ]

    if not arquivos:
        return pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)

    dfs = []

    for arq in arquivos:
        caminho = os.path.join(DATA_DIR, arq)

        df = pd.read_csv(
            caminho,
            sep=";",
            dtype=str,
            encoding="utf-8"
        )

        # Normaliza cabeçalho
        df.columns = df.columns.str.strip()

        # Garante colunas mínimas
        faltando = set(COLUNAS_OBRIGATORIAS) - set(df.columns)
        if faltando:
            continue  # ignora arquivo inválido

        # =============================
        # NORMALIZAÇÃO FORTE
        # =============================
        df["Exercício"] = (
            df["Exercício"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .astype(int)
        )

        df["Competência"] = (
            df["Competência"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        df["Credor"] = df["Credor"].astype(str).str.strip()
        df["Fonte"] = df["Fonte"].astype(str).str.strip()

        # Repasse JÁ DEVE VIR COMO FLOAT NO CSV
        df["Repasse"] = (
            df["Repasse"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        dfs.append(df[COLUNAS_OBRIGATORIAS])

    if not dfs:
        return pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)

    df_final = pd.concat(dfs, ignore_index=True)

    return df_final


# ==================================================
# FILTRO SIMPLES (SEM LÓGICA ESCONDIDA)
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


