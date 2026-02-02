import os
import pandas as pd

CABECALHO_ESPERADO = [
    "Exercício",
    "Competência",
    "Credor",
    "Fonte",
    "Repasse"
]

def carregar_dados(pasta_relativa="data/extras"):
    """
    Carrega todos os arquivos CSV de uma pasta e retorna um DataFrame único.
    Converte 'Repasse' para float, mesmo com R$, pontos ou vírgula.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pasta = os.path.join(base_dir, pasta_relativa)

    if not os.path.exists(pasta):
        raise FileNotFoundError(f"Pasta de dados não encontrada: {pasta}")

    arquivos = [f for f in os.listdir(pasta) if f.endswith(".csv")]
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado na pasta: {pasta}")

    dfs = []
    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)
        df = pd.read_csv(caminho, sep=";", encoding="utf-8")

        # Validação de cabeçalho
        if list(df.columns) != CABECALHO_ESPERADO:
            raise ValueError(
                f"Arquivo {arquivo} com cabeçalho inválido.\n"
                f"Esperado: {CABECALHO_ESPERADO}\n"
                f"Encontrado: {list(df.columns)}"
            )

        df["Arquivo"] = arquivo  # rastreabilidade

        # Converter Repasse robustamente
        df["Repasse"] = (
            df["Repasse"]
            .astype(str)
            .str.replace(r"[^\d,]", "", regex=True)  # remove tudo que não for dígito ou vírgula
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

        df["Exercício"] = df["Exercício"].astype(str)

        dfs.append(df)

    dados = pd.concat(dfs, ignore_index=True)
    return dados
