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
# FUNÇÕES AUXILIARES
# ==================================================
def moeda_para_float(valor):
    if pd.isna(valor):
        return 0.0
    valor = str(valor).replace("R$", "").strip()
    valor = valor.replace(".", "").replace(",", ".")
    return float(valor) if valor else 0.0


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
            df = pd.read_csv(caminho, sep=";", dtype=str)

            df["Exercício"] = df["Exercício"].astype(int)
            df["Competência"] = df["Competência"].str.upper()
            df["Repasse"] = df["Repasse"].apply(moeda_para_float)

            dfs.append(df)

    if not dfs:
        return pd.DataFrame(columns=COLUNAS)

    return pd.concat(dfs, ignore_index=True)

# ==================================================
# INSERIR REPASSE
# ==================================================
def inserir_repasse(exercicio, competencia, credor, fonte, repasse):
    arquivo = os.path.join(DATA_DIR, f"extras_{exercicio}.csv")

    if os.path.exists(arquivo):
        df = pd.read_csv(arquivo, sep=";", dtype=str)
        df["Repasse"] = df["Repasse"].apply(moeda_para_float)
    else:
        df = pd.DataFrame(columns=COLUNAS)

    novo = pd.DataFrame([{
        "Exercício": int(exercicio),
        "Competência": competencia.upper(),
        "Credor": credor,
        "Fonte": fonte,
        "Repasse": float(repasse)
    }])

    df = pd.concat([df, novo], ignore_index=True)

    df_save = df.copy()
    df_save["Repasse"] = df_save["Repasse"].apply(float_para_moeda)

    df_save.to_csv(
        arquivo,
        sep=";",
        index=False,
        encoding="utf-8"
    )

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
