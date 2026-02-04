import os
import pandas as pd

# =====================================================
# CONFIGURAÇÃO
# =====================================================
DATA_DIR = "data"

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# =====================================================
# DESCOBRIR EXERCÍCIOS AUTOMATICAMENTE
# =====================================================
def exercicios_metas():
    if not os.path.exists(DATA_DIR):
        return []

    arquivos = os.listdir(DATA_DIR)

    anos = [
        arq.split(".")[0]
        for arq in arquivos
        if arq.endswith(".metasgerais.csv")
    ]

    return sorted(anos)

# =====================================================
# CONVERSÃO MONETÁRIA SEGURA
# =====================================================
def moeda_para_float(valor):
    if pd.isna(valor):
        return 0.0

    valor = (
        str(valor)
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )

    return float(valor) if valor else 0.0

# =====================================================
# ========= METAS POR RECEITA (PÁGINA 5) ===============
# =====================================================
def carregar_metas_exercicio(exercicio):
    caminho = os.path.join(DATA_DIR, f"{exercicio}.metasgerais.csv")

    if not os.path.exists(caminho):
        raise FileNotFoundError(caminho)

    df = pd.read_csv(caminho, sep=";", dtype=str)

    if "Código" in df.columns:
        df = df.drop_duplicates(subset=["Código"], keep="first")

    df["Exercício"] = exercicio
    return df.reset_index(drop=True)

def normalizar_metas(df):
    registros = []

    for _, row in df.iterrows():
        for mes in MESES:
            registros.append({
                "Exercício": row["Exercício"],
                "Especificação": row.get("Especificação", "Não informado"),
                "Competência": mes,
                "Previsto": moeda_para_float(row.get(f"Previsto {mes}", 0)),
                "Realizado": moeda_para_float(row.get(f"Realizado {mes}", 0)),
            })

    return pd.DataFrame(registros)

def carregar_metas_multiplos_exercicios(anos):
    dfs = []

    for ano in anos:
        df_raw = carregar_metas_exercicio(ano)
        df_norm = normalizar_metas(df_raw)
        dfs.append(df_norm)

    df_final = pd.concat(dfs, ignore_index=True)

    df_final = (
        df_final
        .groupby(
            ["Exercício", "Especificação", "Competência"],
            as_index=False
        )[["Previsto", "Realizado"]]
        .sum()
    )

    return df_final

# =====================================================
# ========= METAS POR FONTE / RECURSO (PÁGINA 6) =======
# =====================================================
def normalizar_metas_recurso(df):
    registros = []

    for _, row in df.iterrows():
        for mes in MESES:
            registros.append({
                "Exercício": row["Exercício"],
                "Codigo": str(row.get("Código", "")).strip(),
                "Especificacao": row.get("Especificação", "Não informado"),
                "Competência": mes,
                "Previsto": moeda_para_float(row.get(f"Previsto {mes}", 0)),
                "Realizado": moeda_para_float(row.get(f"Realizado {mes}", 0)),
            })

    return pd.DataFrame(registros)

def carregar_metas_recurso_multiplos_exercicios(anos):
    dfs = []

    for ano in anos:
        caminho = os.path.join(DATA_DIR, f"{ano}.metasporfonte.csv")

        if not os.path.exists(caminho):
            continue

        df = pd.read_csv(caminho, sep=";", dtype=str)

        if "Código" in df.columns:
            df = df.drop_duplicates(subset=["Código"], keep="first")

        df["Exercício"] = ano

        df_norm = normalizar_metas_recurso(df)
        dfs.append(df_norm)

    if not dfs:
        return pd.DataFrame()

    df_final = pd.concat(dfs, ignore_index=True)

    df_final = (
        df_final
        .groupby(
            ["Exercício", "Codigo", "Especificacao", "Competência"],
            as_index=False
        )[["Previsto", "Realizado"]]
        .sum()
    )

    return df_final
