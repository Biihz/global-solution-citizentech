import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import carregar_conab, carregar_csv


from utils.theme import configurar_pagina, CORES, PALETA_GRAFICOS

configurar_pagina("3 Inteligencia Precos")

# ==================================================
# CONFIGURAÇÃO E CARREGAMENTO
# ==================================================

st.title("Inteligência de Preços")

df_raw = carregar_conab()
resultados = carregar_csv("resultados_modelos_conab.csv")

# Validar estrutura do CSV de resultados
colunas_resultados = [
    "experimento",
    "recorte",
    "n",
    "modelo",
    "mae",
    "rmse",
    "mape_pct",
    "r2",
    "periodo_teste",
    "fonte"
]

colunas_ausentes_resultados = [
    coluna for coluna in colunas_resultados
    if coluna not in resultados.columns
]

if colunas_ausentes_resultados:
    st.error(
        "O CSV de resultados não contém as colunas necessárias: "
        + ", ".join(colunas_ausentes_resultados)
    )
    st.stop()

df = df_raw.copy()

st.caption(
    "Acompanhe a evolução dos preços de produtos hortigranjeiros, "
    "compare entrepostos e explore os resultados dos modelos preditivos."
)

st.info(
    "**Sobre os dados:** a análise utiliza preços mensais da CONAB, "
    "com dez produtos e 12 CEASAs, entre setembro de 2024 e setembro "
    "de 2026. A modelagem supervisionada utiliza um recorte tratado "
    "de 11 CEASAs."
)


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def formatar_numero(valor, casas=2):
    """Formata números no padrão brasileiro."""
    return (
        f"{valor:,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ==================================================
# BASE ANALÍTICA
# ==================================================

df = df_raw.copy()


# ==================================================
# VALIDAÇÃO DA ESTRUTURA
# ==================================================

colunas_obrigatorias = [
    "produto",
    "grupo",
    "ceasa",
    "uf",
    "data_ref",
    "ano",
    "mes",
    "preco"
]

colunas_ausentes = [
    coluna
    for coluna in colunas_obrigatorias
    if coluna not in df.columns
]

if colunas_ausentes:
    st.error(
        "A base CONAB não contém todas as colunas necessárias: "
        + ", ".join(colunas_ausentes)
    )
    st.stop()


# ==================================================
# TRATAMENTO ANALÍTICO
# ==================================================

df["data_ref"] = pd.to_datetime(
    df["data_ref"],
    errors="coerce"
)

df["preco"] = pd.to_numeric(
    df["preco"],
    errors="coerce"
)

# Preservar o preço original
df["preco_original"] = df["preco"]

# Cópia analítica para visualização
# Zeros suspeitos são tratados como ausentes,
# sem modificar o CSV original.
df["preco_analise"] = df["preco"].where(
    df["preco"] > 0
)

df["ano"] = pd.to_numeric(
    df["ano"],
    errors="coerce"
)

df["mes"] = pd.to_numeric(
    df["mes"],
    errors="coerce"
)

# Identificação dos preços iguais a zero
quantidade_zeros = int(
    (df["preco"] == 0).sum()
)

quantidade_ausentes = int(
    df["preco"].isna().sum()
)


# ==================================================
# FILTROS
# ==================================================

st.sidebar.divider()
st.sidebar.subheader("Filtros de preços")

# Filtro de produto

produtos = sorted(
    df["produto"].dropna().unique().tolist()
)

produto_selecionado = st.sidebar.selectbox(
    "Produto",
    options=produtos
)

# Filtrar produto
df_produto = df[
    df["produto"] == produto_selecionado
].copy()

# Filtro de CEASA

ceasas = sorted(
    df_produto["ceasa"].dropna().unique().tolist()
)

ceasas_selecionadas = st.sidebar.multiselect(
    "Centrais de abastecimento",
    options=ceasas,
    default=ceasas
)

# Filtro de período

datas_validas = (
    df_produto["data_ref"]
    .dropna()
    .sort_values()
)

if datas_validas.empty:
    st.error("Não existem datas válidas na base selecionada.")
    st.stop()

data_minima = datas_validas.min().date()
data_maxima = datas_validas.max().date()

periodo = st.sidebar.date_input(
    "Período de análise",
    value=(data_minima, data_maxima),
    min_value=data_minima,
    max_value=data_maxima,
    format="DD/MM/YYYY"
)

if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    data_inicio, data_fim = periodo
else:
    data_inicio = data_minima
    data_fim = data_maxima

# Aplicação dos filtros

df_filtrado = df[
    (df["produto"] == produto_selecionado)
    & (df["ceasa"].isin(ceasas_selecionadas))
    & (df["data_ref"].dt.date >= data_inicio)
    & (df["data_ref"].dt.date <= data_fim)
].copy()

# Remover valores ausentes e zeros suspeitos
df_analise = df_filtrado[
    df_filtrado["preco_analise"].notna()
].copy()


# ==================================================
# VALIDAÇÃO
# ==================================================

if df_analise.empty:
    st.warning(
        "Não existem preços válidos para os filtros selecionados."
    )
    st.stop()


# ==================================================
# INDICADORES
# ==================================================

preco_medio = df_analise["preco_analise"].mean()

preco_minimo = df_analise["preco_analise"].min()

preco_maximo = df_analise["preco_analise"].max()

ultima_data = df_analise["data_ref"].max()

preco_mais_recente = df_analise.loc[
    df_analise["data_ref"] == ultima_data,
    "preco_analise"
].mean()


# ==================================================
# INDICADORES PRINCIPAIS
# ==================================================

st.subheader(
    f"Indicadores — {produto_selecionado}"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Preço médio",
        f"R$ {formatar_numero(preco_medio)}"
    )

with col2:
    st.metric(
        "Menor preço",
        f"R$ {formatar_numero(preco_minimo)}"
    )

with col3:
    st.metric(
        "Maior preço",
        f"R$ {formatar_numero(preco_maximo)}"
    )

with col4:
    st.metric(
        "Último preço disponível",
        f"R$ {formatar_numero(preco_mais_recente)}"
    )

st.caption(
    f"Última referência disponível: {ultima_data.strftime('%m/%Y')}. "
    "Valores expressos em R$/kg."
)

st.divider()


# ==================================================
# ABAS
# ==================================================

aba1, aba2, aba3 = st.tabs([
    "Evolução histórica",
    "Comparação entre CEASAs",
    "Modelos de Machine Learning"
])


# ==================================================
# ABA 1 — EVOLUÇÃO HISTÓRICA
# ==================================================

with aba1:

    st.subheader(
        f"Evolução histórica do preço — {produto_selecionado}"
    )

    dados_historicos = (
        df_analise
        .sort_values("data_ref")
    )

    fig_historico = px.line(
        dados_historicos,
        x="data_ref",
        y="preco_analise",
        color="ceasa",
        markers=True,
        labels={
            "data_ref": "Período",
            "preco_analise": "Preço (R$/kg)",
            "ceasa": "CEASA"
        }
    )

    fig_historico.update_layout(
        height=500,
        hovermode="x unified",
        legend_title_text="Central de abastecimento",
        xaxis_title="Mês",
        yaxis_title="Preço (R$/kg)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_historico,
        use_container_width=True
    )

    st.caption(
        "Cada linha representa a evolução mensal do preço "
        "do produto em uma central de abastecimento."
    )

    # Tabela histórica

    st.subheader("Histórico de preços")

    tabela_historica = (
        dados_historicos[
            [
                "data_ref",
                "produto",
                "ceasa",
                "uf",
                "preco_analise"
            ]
        ]
        .rename(columns={
            "data_ref": "Referência",
            "produto": "Produto",
            "ceasa": "CEASA",
            "uf": "UF",
            "preco_analise": "Preço (R$/kg)"
        })
    )

    st.dataframe(
        tabela_historica.style.format({
            "Preço (R$/kg)": "R$ {:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# ABA 2 — COMPARAÇÃO ENTRE CEASAs
# ==================================================

with aba2:

    st.subheader(
        f"Comparação de preços — {produto_selecionado}"
    )

    comparacao = (
        df_analise
        .groupby(["ceasa", "uf"])
        .agg(
            preco_medio=("preco_analise", "mean"),
            observacoes=("preco_analise", "count")
        )
        .reset_index()
        .sort_values("preco_medio", ascending=True)
    )

    fig_comparacao = px.bar(
        comparacao,
        x="preco_medio",
        y="ceasa",
        orientation="h",
        color="preco_medio",
        color_continuous_scale=[
            "#DCE8D8",
            "#2F6B52"
        ],
        labels={
            "preco_medio": "Preço médio (R$/kg)",
            "ceasa": "Central de abastecimento"
        },
        hover_data=["uf", "observacoes"]
    )

    fig_comparacao.update_layout(
        height=480,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Preço médio (R$/kg)",
        yaxis_title="CEASA",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_comparacao,
        use_container_width=True
    )

    st.caption(
        "A comparação utiliza a média dos preços válidos "
        "no período selecionado. Períodos diferentes podem "
        "alterar a classificação das centrais."
    )

    st.subheader("Resumo por central")

    tabela_comparacao = comparacao.rename(columns={
        "ceasa": "CEASA",
        "uf": "UF",
        "preco_medio": "Preço médio (R$/kg)",
        "observacoes": "Observações válidas"
    })

    st.dataframe(
        tabela_comparacao.style.format({
            "Preço médio (R$/kg)": "R$ {:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )



# ==================================================
# ABA 3 — MODELOS DE MACHINE LEARNING
# ==================================================

with aba3:

    st.subheader("Avaliação dos modelos preditivos")

    st.markdown(
        """
        Os modelos foram treinados para estimar o preço mensal
        dos produtos nas centrais de abastecimento.

        **Variável-alvo:** `preco`, em R$/kg. A modelagem atual não prevê
        quilogramas de desperdício nem excedente alimentar.
        """
    )

    st.info(
        "A tabela apresenta a avaliação final no conjunto de teste (julho a setembro de 2026). "
        "A seleção dos hiperparâmetros foi feita antes, por validação cruzada temporal "
        "somente dentro do treinamento. As métricas são carregadas do arquivo "
        "`resultados_modelos_conab.csv`, sem recalcular os modelos."
    )

    # ----------------------------------------------
    # MODELAGEM NACIONAL
    # ----------------------------------------------

    st.markdown("### Modelagem principal — painel nacional")

    st.caption(
        "Protocolo de seleção: TimeSeriesSplit com três folds temporais expansivos, "
        "três meses por validação e agrupamento por mês para evitar separar observações "
        "do mesmo período entre treino e validação."
    )

    nacionais = resultados[
        resultados["experimento"] == "CONAB - Painel Nacional"
    ].copy()

    recortes = nacionais["recorte"].dropna().unique().tolist()

    recorte_selecionado = st.selectbox(
        "Selecione o recorte da análise",
        options=recortes,
        key="recorte_modelagem_nacional"
    )

    resultados_nacionais = nacionais[
        nacionais["recorte"] == recorte_selecionado
    ].copy()

    if not resultados_nacionais.empty:

        n = int(resultados_nacionais["n"].iloc[0])
        periodo_teste = resultados_nacionais["periodo_teste"].iloc[0]

        st.caption(
            f"Teste temporal: {periodo_teste} | "
            f"{n} observações."
        )

        tabela_nacional = resultados_nacionais[
            ["modelo", "mae", "rmse", "mape_pct", "r2"]
        ].rename(columns={
            "modelo": "Modelo",
            "mae": "MAE (R$/kg)",
            "rmse": "RMSE (R$/kg)",
            "mape_pct": "MAPE (%)",
            "r2": "R²"
        })

        st.dataframe(
            tabela_nacional.style.format({
                "MAE (R$/kg)": "{:.4f}",
                "RMSE (R$/kg)": "{:.4f}",
                "MAPE (%)": "{:.4f}",
                "R²": "{:.4f}"
            }, na_rep="—"),
            use_container_width=True,
            hide_index=True
        )

        # Destaque dinâmico do melhor MAE
        melhor = resultados_nacionais.loc[
            resultados_nacionais["mae"].idxmin()
        ]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Melhor modelo no recorte",
            melhor["modelo"]
        )

        col2.metric(
            "Menor MAE",
            f"R$ {formatar_numero(melhor['mae'], 4)}/kg"
        )

        col3.metric(
            "R² do melhor modelo",
            formatar_numero(melhor["r2"], 4)
        )

        st.caption(
            "O melhor modelo é identificado pelo menor MAE no conjunto de teste do recorte. "
            "A validação cruzada temporal foi usada anteriormente para selecionar os hiperparâmetros; "
            "ela não substitui esta avaliação final."
        )

    st.divider()

    # ----------------------------------------------
    # EXPERIMENTO CLIMÁTICO
    # ----------------------------------------------

    st.markdown(
        "### Experimento complementar — CONAB + INMET"
    )

    resultados_clima = resultados[
        resultados["experimento"] == "CEAGESP + INMET"
    ].copy()

    if not resultados_clima.empty:

        n_clima = int(resultados_clima["n"].iloc[0])

        periodo_clima = resultados_clima[
            "periodo_teste"
        ].iloc[0]

        st.caption(
            f"Recorte CEAGESP-SP | INMET A701 | "
            f"Teste: {periodo_clima} | "
            f"{n_clima} observações."
        )

        tabela_clima = resultados_clima[
            ["modelo", "mae", "rmse", "mape_pct", "r2"]
        ].rename(columns={
            "modelo": "Modelo",
            "mae": "MAE (R$/kg)",
            "rmse": "RMSE (R$/kg)",
            "mape_pct": "MAPE (%)",
            "r2": "R²"
        })

        st.dataframe(
            tabela_clima.style.format({
                "MAE (R$/kg)": "{:.4f}",
                "RMSE (R$/kg)": "{:.4f}",
                "MAPE (%)": "{:.4f}",
                "R²": "{:.4f}"
            }, na_rep="—"),
            use_container_width=True,
            hide_index=True
        )

        # Comparação do Random Forest com e sem clima
        rf_com = resultados_clima[
            resultados_clima["modelo"] == "Random Forest - Com clima"
        ]

        rf_sem = resultados_clima[
            resultados_clima["modelo"] == "Random Forest - Sem clima"
        ]

        if not rf_com.empty and not rf_sem.empty:

            mae_com = rf_com["mae"].iloc[0]
            mae_sem = rf_sem["mae"].iloc[0]

            diferenca = mae_sem - mae_com

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "RF com clima",
                f"R$ {formatar_numero(mae_com, 4)}/kg"
            )

            col2.metric(
                "RF sem clima",
                f"R$ {formatar_numero(mae_sem, 4)}/kg"
            )

            col3.metric(
                "Redução do MAE",
                f"{formatar_numero(diferenca, 4)} R$/kg"
            )

        st.warning(
            "O ganho do Random Forest com variáveis climáticas foi pequeno neste teste. "
            "O resultado não demonstra causalidade e não garante melhoria em outras CEASAs "
            "ou períodos. O experimento climático é complementar e não substitui a modelagem principal."
        )

    st.divider()

    # ----------------------------------------------
    # GRÁFICO COMPARATIVO
    # ----------------------------------------------

    st.markdown("### Comparação dos erros dos modelos")

    experimento_grafico = st.selectbox(
        "Experimento",
        options=[
            "CONAB - Painel Nacional",
            "CEAGESP + INMET"
        ],
        format_func=lambda x: (
            "Painel nacional"
            if x == "CONAB - Painel Nacional"
            else "Experimento climático"
        ),
        key="experimento_grafico"
    )

    dados_grafico = resultados[
        resultados["experimento"] == experimento_grafico
    ].copy()

    if experimento_grafico == "CONAB - Painel Nacional":
        dados_grafico = dados_grafico[
            dados_grafico["recorte"] == recorte_selecionado
        ]

    if not dados_grafico.empty:

        fig_modelos = px.bar(
            dados_grafico,
            x="modelo",
            y="mae",
            color="modelo",
            text="mae",
            labels={
                "modelo": "Modelo",
                "mae": "Erro absoluto médio (R$/kg)"
            }
        )

        fig_modelos.update_traces(
            texttemplate="%{text:.4f}",
            textposition="outside"
        )

        fig_modelos.update_layout(
            height=420,
            showlegend=False,
            xaxis_title="Modelo",
            yaxis_title="MAE (R$/kg)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_modelos,
            use_container_width=True
        )

    # ----------------------------------------------
    # INTERPRETAÇÃO DAS MÉTRICAS
    # ----------------------------------------------

    with st.expander("Como interpretar as métricas?"):

        st.markdown("""
        - **MAE:** erro absoluto médio entre o preço previsto e o observado.
          Quanto menor, melhor.

        - **RMSE:** penaliza erros maiores. Quanto menor, melhor.

        - **MAPE:** erro percentual absoluto médio. Quanto menor, melhor,
          mas deve ser interpretado com cuidado quando há valores próximos de zero.

        - **R²:** proporção da variação dos preços explicada pelo modelo
          no conjunto avaliado. Quanto mais próximo de 1, melhor.
        """)

    with st.expander("Metodologia e limitações dos modelos"):

        st.markdown("""
        **Modelagem principal:**

        - Unidade de observação: produto × CEASA × mês.
        - Variável-alvo: `preco` (R$/kg).
        - Atributos: defasagens de preço, média móvel histórica,
          sazonalidade cíclica e identificadores categóricos.
        - Modelos: Baseline — Lag 1, Ridge e Random Forest.
        - Treinamento até junho de 2026.
        - Teste final de julho a setembro de 2026.
        - Validação cruzada temporal com `TimeSeriesSplit`, usando três folds expansivos.
        - Cada fold valida três meses completos; os registros de um mesmo mês permanecem juntos.
        - Pré-processamento ajustado dentro de cada fold, somente nos dados de treino.
        - Hiperparâmetros selecionados pela média do MAE nos folds de validação.
        - Ridge: `alpha=10`; Random Forest: `max_depth=5` e `min_samples_leaf=4`.
        - O teste final (julho a setembro de 2026) foi preservado para avaliação após a seleção.

        **Experimento climático:**

        - Recorte: CEAGESP-SP.
        - Estação meteorológica: INMET A701.
        - Variáveis meteorológicas agregadas mensalmente e defasadas em um mês.

        **Limitações:**

        - A série possui 25 referências mensais, pouco mais de dois ciclos anuais.
        - Brasília foi excluída da modelagem principal por baixa cobertura.
        - Os dez preços iguais a zero em Goiânia, em setembro de 2026,
          foram tratados como ausentes na cópia de modelagem.
        - O experimento climático possui apenas 30 observações no teste.
        - A estação A701 representa a capital paulista, não as regiões
          produtoras que abastecem a CEAGESP.
        """)


# ==================================================
# QUALIDADE E FONTE DOS DADOS
# ==================================================

st.divider()

with st.expander("Qualidade e origem dos dados"):

    st.markdown(f"""
    **Fonte:** CONAB — preços de produtos hortigranjeiros
    comercializados em centrais de abastecimento.

    **Base consolidada:**
    - Registros carregados: {len(df_raw):,}
    - Produtos: {df_raw["produto"].nunique()}
    - CEASAs: {df_raw["ceasa"].nunique()}
    - Referências mensais: {df_raw["data_ref"].nunique()}

    **Qualidade dos dados:**
    - Preços ausentes na base original: {quantidade_ausentes}
    - Preços iguais a zero na base original: {quantidade_zeros}

    Os valores iguais a zero foram preservados na base original.
    Na visualização analítica, são tratados como ausentes para evitar
    que registros suspeitos sejam interpretados como preços reais.
    """)

st.caption(
    "NutriRota | Fonte: CONAB e INMET. "
    "Resultados dos modelos conforme o Notebook 03."
)
