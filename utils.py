import os
import pandas as pd

DATA_DIR = "data"

# ==================================================
# NORMALIZAR COLUNAS
# ==================================================
def normalizar_colunas(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace("  ", " ", regex=False)
    )

    df.rename(columns={

        "Número do Organograma": "Organograma_Codigo",
        "Descrição do organograma": "Organograma",

        "Número da ação": "Numero_Acao",
        "Descrição da ação": "Descricao_Acao",

        "Número da subfunção": "Numero_Subfuncao",
        "Descrição da subfunção": "Subfuncao",

        "Descrição da natureza de despesa": "Descricao_Natureza",
        "Descrição do recurso": "Descricao_Recurso"

    }, inplace=True)

    return df


# ==================================================
# EXERCÍCIOS DISPONÍVEIS
# ==================================================
def exercicios_disponiveis():

    if not os.path.exists(DATA_DIR):
        return []

    arquivos = os.listdir(DATA_DIR)
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
# CARREGAR DESPESAS
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
        "Organograma_Codigo",
        "Organograma",
        "Numero_Acao",
        "Descricao_Acao",
        "Recurso",
        "Subfuncao"
    ]

    orcada = df_orc.groupby(chaves, as_index=False)["valor_orcado"].sum()
    atualizada = df_atu.groupby(chaves, as_index=False)["valor_atualizado"].sum()

    df_final = pd.merge(orcada, atualizada, on=chaves, how="outer")

    # ==================================================
    # EMPENHADA
    # ==================================================
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
