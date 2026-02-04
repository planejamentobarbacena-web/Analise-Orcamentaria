import os
import pandas as pd

# ==================================================
# CONFIGURAÇÃO
# ==================================================
DATA_DIR = "data"
ARQUIVO_EXTRAS = os.path.join(DATA_DIR, "extras_repasses.csv")

MESES = [
    "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
    "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
]

# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
def moeda_para_float(valor):
    """
    Converte 'R$ 1.234.567,89' ou '1.234.567,89' para float
    """
    if pd.isna(valor):
        return 0.0

    valor = str(valor)
    valor = valor.replace("R$", "").strip()
    valor = valor.replace(".", "").replace(",", ".")
    return float(valor) if valor else 0.0


def float_para_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ==================================================
# CARREGAR EXTRAS
# ==================================================
def carregar_extras():
    if not os.path.exists(ARQUIVO_EXTRAS):
        colunas = ["Exercício", "Competência", "Credor", "Fonte", "Repasse"]
        return pd.DataFrame(columns=colunas)

    df = pd.read_csv(ARQUIVO_EXTRAS, sep=";", dtype=str)

    df["Exercício"] = df["Exercício"].astype(int)
    df["Competência"] = df["Competência"].str.upper()
    df["Repasse"] = df["Repasse"].apply(moeda_para_float)

    return df

# ==================================================
# SALVAR EXTRAS
# ==================================================
def salvar_extras(df):
    df_save = df.copy()
    df_save["Repasse"] = df_save["Repasse"].apply(float_para_moeda)

    df_save.to_csv(
        ARQUIVO_EXTRAS,
        sep=";",
        index=False,
        encoding="utf-8"
    )

# ==================================================
# INSERIR UM NOVO REPASSE
# ==================================================
def inserir_repasse(exercicio, competencia, credor, fonte, repasse):
    df = carregar_extras()

    novo = pd.DataFrame([{
        "Exercício": int(exercicio),
        "Competência": competencia.upper(),
        "Credor": credor,
        "Fonte": fonte,
        "Repasse": float(repasse)
    }])

    df = pd.concat([df, novo], ignore_index=True)
    salvar_extras(df)

# ==================================================
# INSERIR REPASSE FIXO (12 MESES)
# ==================================================
def inserir_repasse_fixo(exercicio, credor, fonte, valor_mensal):
    df = carregar_extras()

    registros = []
    for mes in MESES:
        registros.append({
            "Exercício": int(exercicio),
            "Competência": mes,
            "Credor": credor,
            "Fonte": fonte,
            "Repasse": float(valor_mensal)
        })

    df = pd.concat([df, pd.DataFrame(registros)], ignore_index=True)
    salvar_extras(df)

# ==================================================
# FILTROS BÁSICOS
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
