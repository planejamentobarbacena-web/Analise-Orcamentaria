import os
import pandas as pd

CABECALHO_ESPERADO = [
    "Exercício",
    "Competência",
    "Credor",
    "Fonte",
    "Repasse"
]

def carregar_dados(pasta="dados"):
    arquivos = [
        f for f in os.listdir(pasta)
        if f.endswith(".csv")
    ]

    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado na pasta de dados.")

    dfs = []

    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)

        df = pd.read_csv(
            caminho,
            sep=";",
            encoding="utf-8"
        )

        # Validação de cabeçalho
        if list(df.columns) != CABECALHO_ESPERADO:
            raise ValueError(
                f"Arquivo {arquivo} com cabeçalho inválido.\n"
                f"Esperado: {CABECALHO_ESPERADO}\n"
                f"Encontrado: {list(df.columns)}"
            )

        df["Arquivo"] = arquivo  # rastreabilidade
        dfs.append(df)

    dados = pd.concat(dfs, ignore_index=True)

    # Tratamento de tipos
    dados["Exercício"] = dados["Exercício"].astype(str)

    dados["Repasse"] = (
        dados["Repasse"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    return dados
