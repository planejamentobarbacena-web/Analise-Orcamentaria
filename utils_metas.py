import os
import pandas as pd

DATA_DIR = "data"

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# ==================================================
# EXERCÍCIOS DISPONÍVEIS
# ==================================================
def exercicios_metas():
    arquivos = os.listdir(DATA_DIR)
    anos = [
        arq.split(".")[0]
        for arq in arquivos
        if arq.endswith(".metasgerais.csv")
    ]
    return sorted(anos)

# ==================================================
# CONVERSÃO MONETÁRIA
# ==================================================
def moeda_para_float(serie):
    return (
        serie.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

# ==================================================
# CARREGAR METAS — 1 EXERCÍCIO
# ==================================================
def carregar_metas_arrecadacao(exercicio):
    caminho = os.path.join(DATA_DIR, f"{exercicio}.metasgerais.csv")

    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho, sep=";", dtype=str)
    df["Exercício"] = exercicio

    return df

# ==================================================
# NORMALIZAR POR COMPETÊNCIA (MENSAL)
# ==================================================
def normalizar_metas(df):
    registros = []

    for _, row in df.iterrows():
        for mes in MESES:
            col_prev = f"Previsto {mes}"
            col_real = f"Realizado {mes}"

            if col_prev in df.columns or col_real in df.columns:
                previsto = row[col_prev] if col_prev in df.columns else "0"
                realizado = row[col_real] if col_real in df.columns else "0"

                registros.append({
                    "Exercício": row["Exercício"],
                    "Especificação": row.get("Especificação", "Não informado"),
                    "Competência": mes,
                    "Previsto": moeda_para_float(pd.Series([previsto]))[0],
                    "Realizado": moeda_para_float(pd.Series([realizado]))[0],
                })

    return pd.DataFrame(registros)

# ==================================================
# CARREGAR MÚLTIPLOS EXERCÍCIOS (JÁ NORMALIZADO)
# ==================================================
def carregar_metas_multiplos_exercicios(anos):
    dfs = []

    for ano in anos:
        df_raw = carregar_metas_arrecadacao(ano)
        df_norm = normalizar_metas(df_raw)
        dfs.append(df_norm)

    return pd.concat(dfs, ignore_index=True)

# ==================================================
# CARREGAR METAS POR RECURSO — 1 EXERCÍCIO
# ==================================================
def carregar_metas_recurso(exercicio):
    caminho = os.path.join(DATA_DIR, f"{exercicio}.metasporfonte.csv")

    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho, sep=";", dtype=str)
    df["Exercício"] = exercicio

    return df


# ==================================================
# NORMALIZAR METAS POR RECURSO (MENSAL)
# ==================================================
def normalizar_metas_recurso(df):
    registros = []

    for _, row in df.iterrows():
        for mes in MESES:
            col_prev = f"Previsto {mes}"
            col_real = f"Realizado {mes}"

            if col_prev in df.columns or col_real in df.columns:
                previsto = row[col_prev] if col_prev in df.columns else "0"
                realizado = row[col_real] if col_real in df.columns else "0"

                registros.append({
                    "Exercício": row["Exercício"],
                    "Recurso": row.get("Código", "Não informado"),
                    "Competência": mes,
                    "Previsto": moeda_para_float(pd.Series([previsto]))[0],
                    "Realizado": moeda_para_float(pd.Series([realizado]))[0],
                })

    return pd.DataFrame(registros)


# ==================================================
# CARREGAR MÚLTIPLOS EXERCÍCIOS — RECURSO
# ==================================================
def carregar_metas_recurso_multiplos_exercicios(anos):
    dfs = []

    for ano in anos:
        df_raw = carregar_metas_recurso(ano)
        df_norm = normalizar_metas_recurso(df_raw)
        dfs.append(df_norm)

    return pd.concat(dfs, ignore_index=True)