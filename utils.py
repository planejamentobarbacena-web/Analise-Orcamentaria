import os
import pandas as pd

DATA_DIR = "data"

# ==================================================
# NORMALIZAR COLUNAS (PADRÃO DO SISTEMA)
# ==================================================
def normalizar_colunas(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace("  ", " ", regex=False)
    )

    # Padronização de nomes usados nos filtros
    df.rename(columns={
        "Descrição do organograma": "Organograma",
        "Descrição da subfunção": "Subfunção"
    }, inplace=True)

    return df


# ==================================================
# EXERCÍCIOS DISPONÍVEIS
# ==================================================
def exercicios_disponiveis():
    if not os.path.exists(DATA_DIR):
        return []

    arquivos = [f.strip() for f in os.listdir(DATA_DIR)]
    exercicios = set()

    for f in arquivos:
        if "." in f:
            exercicios.add(f.split(".")[0])

    validos = []
    for ano in sorted(exercicios):
        tipos = {f.split(".")[1] for f in arquivos if f.startswith(f"{ano}.")}
        if {"orçada", "atualizada"}.issubset(tipos):
            validos.append(ano)

    return validos


# ==================================================
# NORMALIZAÇÃO DA NATUREZA (X.X.XX.XX)
# ==================================================
def normalizar_natureza(codigo):
    if pd.isna(codigo):
        return None

    partes = str(codigo).split(".")
    if len(partes) >= 4:
        return ".".join(partes[:4])
    return codigo


# ==================================================
# CARREGAR DESPESAS — POR AÇÃO
# ==================================================
def carregar_despesas(exercicio):

    def caminho(tipo):
        return os.path.join(DATA_DIR, f"{exercicio}.{tipo}.csv")

    arq_orcada = caminho("orçada")
    arq_atualizada = caminho("atualizada")
    arq_empenhada = caminho("empenhada")

    if not os.path.exists(arq_orcada) or not os.path.exists(arq_atualizada):
        raise ValueError("Arquivos orçada e atualizada são obrigatórios.")

    df_orc = normalizar_colunas(pd.read_csv(arq_orcada, sep=";", dtype=str))
    df_atu = normalizar_colunas(pd.read_csv(arq_atualizada, sep=";", dtype=str))

    df_orc["valor_orcado"] = (
        df_orc["Valor orçado da despesa"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    df_atu["valor_atualizado"] = (
        df_atu["Valor orçado atualizado da despesa"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    chaves = [
        "Entidade",
        "Número da ação",
        "Descrição da ação",
        "Recurso",
        "Organograma",
        "Subfunção"
    ]

    orcada = df_orc.groupby(chaves, as_index=False)["valor_orcado"].sum()
    atualizada = df_atu.groupby(chaves, as_index=False)["valor_atualizado"].sum()

    df_final = pd.merge(orcada, atualizada, on=chaves, how="outer")

    if os.path.exists(arq_empenhada):
        df_emp = normalizar_colunas(pd.read_csv(arq_empenhada, sep=";", dtype=str))

        df_emp["valor_empenhado"] = (
            df_emp["Valor empenhado da despesa"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        empenhada = df_emp.groupby(chaves, as_index=False)["valor_empenhado"].sum()
        df_final = pd.merge(df_final, empenhada, on=chaves, how="left")
    else:
        df_final["valor_empenhado"] = 0.0

    for col in ["valor_orcado", "valor_atualizado", "valor_empenhado"]:
        df_final[col] = df_final[col].fillna(0)

    return df_final


# ==================================================
# MULTI-EXERCÍCIOS (VISÃO GERAL)
# ==================================================
def carregar_despesas_multiplos_exercicios(anos, func_carregamento):
    dfs = []

    for ano in anos:
        df_ano = func_carregamento(ano)
        df_ano["Exercício"] = ano
        dfs.append(df_ano)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)

# ==================================================
# CARREGAR DESPESAS — POR NATUREZA
# ==================================================
def carregar_despesas_por_natureza(exercicio):

    def caminho(tipo):
        return os.path.join(DATA_DIR, f"{exercicio}.{tipo}.csv")

    arq_orcada = caminho("orçada")
    arq_atualizada = caminho("atualizada")
    arq_empenhada = caminho("empenhada")

    if not os.path.exists(arq_orcada) or not os.path.exists(arq_atualizada):
        raise ValueError("Arquivos orçada e atualizada são obrigatórios.")

    # =============================
    # LEITURA
    # =============================
    df_orc = normalizar_colunas(pd.read_csv(arq_orcada, sep=";", dtype=str))
    df_atu = normalizar_colunas(pd.read_csv(arq_atualizada, sep=";", dtype=str))

    # =============================
    # NORMALIZA NATUREZA
    # =============================
    df_orc["Natureza_Normalizada"] = df_orc["Natureza de Despesa"].apply(normalizar_natureza)
    df_atu["Natureza_Normalizada"] = df_atu["Natureza de Despesa"].apply(normalizar_natureza)

    # =============================
    # VALORES
    # =============================
    df_orc["valor_orcado"] = (
        df_orc["Valor orçado da despesa"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    df_atu["valor_atualizado"] = (
        df_atu["Valor orçado atualizado da despesa"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # =============================
    # CHAVES (NATUREZA)
    # =============================
    chaves = [
        "Entidade",
        "Natureza_Normalizada",
        "Descrição da natureza de despesa",
        "Recurso"
    ]

    orcada = df_orc.groupby(chaves, as_index=False)["valor_orcado"].sum()
    atualizada = df_atu.groupby(chaves, as_index=False)["valor_atualizado"].sum()

    df_final = pd.merge(orcada, atualizada, on=chaves, how="outer")

    # =============================
    # EMPENHADA
    # =============================
    if os.path.exists(arq_empenhada):
        df_emp = normalizar_colunas(pd.read_csv(arq_empenhada, sep=";", dtype=str))
        df_emp["Natureza_Normalizada"] = df_emp["Natureza de Despesa"].apply(normalizar_natureza)

        df_emp["valor_empenhado"] = (
            df_emp["Valor empenhado da despesa"]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        empenhada = (
            df_emp
            .groupby(
                ["Entidade", "Natureza_Normalizada", "Recurso"],
                as_index=False
            )["valor_empenhado"]
            .sum()
        )

        df_final = pd.merge(
            df_final,
            empenhada,
            on=["Entidade", "Natureza_Normalizada", "Recurso"],
            how="left"
        )
    else:
        df_final["valor_empenhado"] = 0.0

    # =============================
    # AJUSTES
    # =============================
    for col in ["valor_orcado", "valor_atualizado", "valor_empenhado"]:
        df_final[col] = df_final[col].fillna(0)

    df_final.rename(
        columns={"Descrição da natureza de despesa": "Descrição da Natureza"},
        inplace=True
    )

    return df_final