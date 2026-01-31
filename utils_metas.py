import os
import pandas as pd

# ==================================================
# CONFIGURAÇÃO
# ==================================================
DATA_DIR = "data"

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# ==================================================
# LISTAR EXERCÍCIOS DISPONÍVEIS
# ==================================================
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


# ==================================================
# CONVERSÃO MONETÁRIA SEGURA (STRING → FLOAT)
# ==================================================
def moeda_para_float(valor):
    if valor is None or pd.isna(valor):
        return 0.0

    return float(
        str(valor)
        .replace(".", "")
        .replace(",", ".")
    )


# ==================================================
# CARREGAR METAS – ARRECADAÇÃO (1 EXERCÍCIO)
# ==================================================
def carregar_metas_arrecadacao(exercicio):
    caminho = os.path.join(DATA_DIR, f"{exercicio}.metasgerais.csv")

    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho, sep=";", dtype=str)
    df["Exercício"] = str(exercicio)

    return df


# ==================================================
# NORMALIZAR METAS – ARRECADAÇÃO (MENSAL)
# ==================================================
def normalizar_metas(df):
    registros = []

    for _, row in df.iterrows():
        for mes in MESES:
            col_prev = f"Previsto {mes}"
            col_real = f"Realizado {mes}"

            previsto = row[col_prev] if col_prev in df.columns else "0"
            realizado = row[col_real] if col_real in df.columns else "0"

            registros.append({
                "Exercício": row["Exercício"],
                "Especificação": row.get("Especificação", "Não informado"),
                "Competência": mes,
                "Previsto": moeda_para_float(previsto),
                "Realizado": moeda_para_float(realizado),
            })

    df_final = pd.DataFrame(registros)

    # 🔒 BLINDAGEM FINAL DE TIPO (CRÍTICO PARA O CLOUD)
    df_final["Previsto"] = pd.to_numeric(df_final["Previsto"], errors="coerce").fillna(0)
    df_final["Realizado"] = pd.to_numeric(df_final["Realizado"], errors="coerce").fillna(0)

    return df_final


# ==================================================
# CARREGAR METAS – ARRECADAÇÃO (MÚLTIPLOS EXERCÍCIOS)
# ==================================================
def carregar_metas_multiplos_exercicios(anos):
    dfs = []

    for ano in anos:
        df_raw = carregar_metas_arrecadacao(ano)
        df_norm = normalizar_metas(df_raw)
        dfs.append(df_norm)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


# ==================================================
# CARREGAR METAS POR RECURSO (1 EXERCÍCIO)
# ==================================================
def carregar_metas_recurso(exercicio):
    caminho = os.path.join(DATA_DIR, f"{exercicio}.metasporfonte.csv")

    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = pd.read_csv(caminho, sep=";", dtype=str)
    df["Exercício"] = str(exercicio)

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

            previsto = row[col_prev] if col_prev in df.columns else "0"
            realizado = row[col_real] if col_real in df.columns else "0"

            registros.append({
                "Exercício": row["Exercício"],
                "Recurso": row.get("Código", "Não informado"),
                "Competência": mes,
                "Previsto": moeda_para_float(previsto),
                "Realizado": moeda_para_float(realizado),
            })

    df_final = pd.DataFrame(registros)

    # 🔒 BLINDAGEM FINAL
    df_final["Previsto"] = pd.to_numeric(df_final["Previsto"], errors="coerce").fillna(0)
    df_final["Realizado"] = pd.to_numeric(df_final["Realizado"], errors="coerce").fillna(0)

    return df_final


# ==================================================
# CARREGAR METAS POR RECURSO (MÚLTIPLOS EXERCÍCIOS)
# ==================================================
def carregar_metas_recurso_multiplos_exercicios(anos):
    dfs = []

    for ano in anos:
        df_raw = carregar_metas_recurso(ano)
        df_norm = normalizar_metas_recurso(df_raw)
        dfs.append(df_norm)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)
