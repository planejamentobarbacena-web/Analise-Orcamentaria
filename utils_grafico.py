import plotly.express as px


# ==================================================
# GRÁFICO DE BARRAS POR EXERCÍCIO
# ==================================================
def grafico_barra_exercicio(
    df,
    coluna_exercicio="Exercício",
    coluna_valor="Valor",
    coluna_texto=None,
    titulo="Valor por Exercício",
    label_valor="Valor (R$)"
):
    """
    Cria gráfico de barras agregado por exercício.
    Retorna None se o dataframe estiver vazio.
    """

    if df is None or df.empty:
        return None

    fig = px.bar(
        df,
        x=coluna_exercicio,
        y=coluna_valor,
        text=coluna_texto,
        labels={coluna_valor: label_valor},
        title=titulo
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        yaxis_tickprefix="R$ ",
        xaxis_title="Exercício",
        bargap=0.25
    )

    return fig


# ==================================================
# GRÁFICO DE BARRAS MENSAL (COMPETÊNCIA)
# ==================================================
def grafico_barra_mensal(
    df,
    coluna_competencia="Competência",
    coluna_valor="Valor",
    ordem_meses=None,
    coluna_texto=None,
    titulo="Valor por Competência",
    label_valor="Valor (R$)"
):
    """
    Gráfico de barras por mês (competência).
    """

    if df is None or df.empty:
        return None

    if ordem_meses:
        df[coluna_competencia] = df[coluna_competencia].astype(str)
        df[coluna_competencia] = pd.Categorical(
            df[coluna_competencia],
            categories=ordem_meses,
            ordered=True
        )

    fig = px.bar(
        df,
        x=coluna_competencia,
        y=coluna_valor,
        text=coluna_texto,
        labels={coluna_valor: label_valor},
        title=titulo
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        yaxis_tickprefix="R$ ",
        xaxis_title="Competência",
        bargap=0.25
    )

    return fig


# ==================================================
# GRÁFICO DE LINHA (EVOLUÇÃO)
# ==================================================
def grafico_linha(
    df,
    coluna_x,
    coluna_y,
    titulo="Evolução do Valor",
    label_y="Valor (R$)"
):
    """
    Gráfico de linha simples (ex: evolução mensal).
    """

    if df is None or df.empty:
        return None

    fig = px.line(
        df,
        x=coluna_x,
        y=coluna_y,
        markers=True,
        labels={coluna_y: label_y},
        title=titulo
    )

    fig.update_layout(
        yaxis_tickprefix="R$ ",
        xaxis_title=coluna_x
    )

    return fig


# ==================================================
# GRÁFICO DE PIZZA (DISTRIBUIÇÃO)
# ==================================================
def grafico_pizza(
    df,
    coluna_categoria,
    coluna_valor,
    titulo="Distribuição"
):
    """
    Gráfico de pizza (ex: por credor, fonte, etc).
    """

    if df is None or df.empty:
        return None

    fig = px.pie(
        df,
        names=coluna_categoria,
        values=coluna_valor,
        title=titulo,
        hole=0.4
    )

    return fig
