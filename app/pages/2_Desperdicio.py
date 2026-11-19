
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import carregar_brancoli



from utils.theme import configurar_pagina, CORES, PALETA_GRAFICOS

configurar_pagina("2 Desperdicio")

# ==================================================
# CONFIGURAÇÃO VISUAL
# ==================================================

st.title("Análise de Desperdício")

st.caption(
    "Explore a composição dos resíduos alimentares "
    "e os indicadores derivados das feiras estudadas."
)

st.info(
    "**Sobre os dados:** esta análise utiliza o estudo de "
    "Brancoli et al. (2022), realizado em quatro feiras livres "
    "de São Paulo durante uma semana de dezembro de 2021. "
    "Os resultados não representam todas as feiras da cidade."
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
# CARREGAMENTO DOS DADOS
# ==================================================

df_raw = carregar_brancoli()
df = df_raw.copy()


# ==================================================
# VALIDAÇÃO DA ESTRUTURA
# ==================================================

colunas_obrigatorias = [
    "market_id",
    "name",
    "number_of_stalls",
    "kg_per_stall",
    "classification",
    "category_level_I",
    "category_level_II",
    "subprefeitura",
    "district",
    "idh"
]

colunas_ausentes = [
    coluna
    for coluna in colunas_obrigatorias
    if coluna not in df.columns
]

if colunas_ausentes:
    st.error(
        "A base Brancoli não contém todas as colunas necessárias: "
        + ", ".join(colunas_ausentes)
    )
    st.stop()


# ==================================================
# TRATAMENTO DOS DADOS
# ==================================================

df["kg_per_stall"] = pd.to_numeric(
    df["kg_per_stall"],
    errors="coerce"
)

df["number_of_stalls"] = pd.to_numeric(
    df["number_of_stalls"],
    errors="coerce"
)

# Volume derivado por categoria:
# kg por barraca × número de barracas

df["kg_total_derivado"] = (
    df["kg_per_stall"] * df["number_of_stalls"]
)

# Tradução das classificações

nomes_classificacao = {
    "avoidable_food_waste": "Desperdício evitável",
    "unavoidable_food_waste": "Desperdício inevitável",
    "packaging": "Embalagens",
    "external_waste": "Resíduos externos"
}

df["classificacao_pt"] = (
    df["classification"]
    .map(nomes_classificacao)
    .fillna(df["classification"])
)


# ==================================================
# FILTROS
# ==================================================

st.sidebar.divider()
st.sidebar.subheader("Filtros de exploração")

# Filtro de subprefeitura

subprefeituras = sorted(
    df["subprefeitura"]
    .dropna()
    .unique()
    .tolist()
)

subprefeituras_selecionadas = st.sidebar.multiselect(
    "Subprefeitura",
    options=subprefeituras,
    default=subprefeituras
)

# Aplicação do filtro territorial

df_sub = df[
    df["subprefeitura"].isin(subprefeituras_selecionadas)
].copy()

# Filtro de feiras

feiras_disponiveis = (
    df_sub[["market_id", "name"]]
    .drop_duplicates()
    .sort_values("name")
)

opcoes_feiras = {
    linha["name"]: linha["market_id"]
    for _, linha in feiras_disponiveis.iterrows()
}

nomes_feiras_selecionados = st.sidebar.multiselect(
    "Feiras estudadas",
    options=list(opcoes_feiras.keys()),
    default=list(opcoes_feiras.keys())
)

ids_selecionados = [
    opcoes_feiras[nome]
    for nome in nomes_feiras_selecionados
]

df = df_sub[
    df_sub["market_id"].isin(ids_selecionados)
].copy()

# Escolha do denominador

denominador_escolhido = st.sidebar.radio(
    "Base de cálculo do percentual evitável",
    options=[
        "Sem resíduos externos (somente resíduos da feira)",
        "Com resíduos externos (todas as categorias)"
    ],
    index=0
)


# ==================================================
# VALIDAÇÃO DOS FILTROS
# ==================================================

if df.empty:
    st.warning(
        "Nenhum registro encontrado. "
        "Ajuste os filtros selecionados."
    )
    st.stop()


# ==================================================
# INDICADORES
# ==================================================

# Uma linha por feira para não contar barracas repetidamente

feiras_unicas = (
    df.drop_duplicates(subset="market_id")
    .copy()
)

quantidade_feiras = feiras_unicas["market_id"].nunique()

total_barracas = (
    feiras_unicas["number_of_stalls"].sum()
)

# Volumes derivados por classificação

totais_classificacao = (
    df.groupby("classification")["kg_total_derivado"].sum()
)

total_evitavel = float(
    totais_classificacao.get("avoidable_food_waste", 0)
)

total_inevitavel = float(
    totais_classificacao.get("unavoidable_food_waste", 0)
)

total_embalagens = float(
    totais_classificacao.get("packaging", 0)
)

total_externos = float(
    totais_classificacao.get("external_waste", 0)
)

# Volume total incluindo resíduos externos

total_geral = float(
    df["kg_total_derivado"].sum()
)

# Volume total sem resíduos externos

total_sem_externos = total_geral - total_externos

# Seleção do denominador

if denominador_escolhido.startswith("Sem resíduos"):

    denominador = total_sem_externos
    rotulo_denominador = "sem resíduos externos"

else:

    denominador = total_geral
    rotulo_denominador = "com resíduos externos"

# Participação percentual do desperdício evitável

percentual_evitavel = (
    (total_evitavel / denominador) * 100
    if denominador > 0
    else 0
)



# ==================================================
# INDICADORES PRINCIPAIS
# ==================================================

st.subheader("Indicadores principais")

col1, col2, col3, col4 = st.columns([0.8, 1.3, 1.3, 1])

with col1:
    st.metric(
        label="Feiras estudadas",
        value=f"{quantidade_feiras}"
    )

with col2:
    st.metric(
        label="Desperdício evitável",
        value=f"{formatar_numero(total_evitavel)} kg"
    )

with col3:
    st.metric(
        label="Base de comparação",
        value=f"{formatar_numero(denominador)} kg"
    )

with col4:
    st.metric(
        label="Participação evitável",
        value=f"{formatar_numero(percentual_evitavel)}%"
    )

st.caption(
    f"Base de cálculo: {rotulo_denominador}. "
    f"Seleção atual: {int(total_barracas)} barracas. "
    "Os volumes são derivados da multiplicação do indicador "
    "em kg/barraca pelo número de barracas, não de uma nova pesagem."
)

st.divider()

# ==================================================
# ABAS
# ==================================================

aba1, aba2, aba3 = st.tabs([
    "Composição dos resíduos",
    "Comparação entre feiras",
    "Alimentos evitáveis"
])

# ==================================================
# ABA 1 — COMPOSIÇÃO DOS RESÍDUOS
# ==================================================

with aba1:

    st.subheader(
        "Composição do volume derivado por classificação"
    )

    dados_classificacao = (
        df.groupby("classificacao_pt")["kg_total_derivado"]
        .sum()
        .reset_index()
        .sort_values("kg_total_derivado", ascending=False)
    )

    fig_composicao = px.pie(
        dados_classificacao,
        names="classificacao_pt",
        values="kg_total_derivado",
        hole=0.55,
        color_discrete_sequence=PALETA_GRAFICOS
    )

    fig_composicao.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig_composicao.update_layout(
        height=480,
        legend_title_text="Classificação",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_composicao,
        use_container_width=True
    )

    st.subheader("Resumo por classificação")

    resumo = (
        df.groupby("classificacao_pt")
        .agg(
            indicador_kg_barraca=(
                "kg_per_stall",
                "sum"
            ),
            volume_derivado_kg=(
                "kg_total_derivado",
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "volume_derivado_kg",
            ascending=False
        )
    )

    st.dataframe(
        resumo.style.format({
            "indicador_kg_barraca": "{:.2f}",
            "volume_derivado_kg": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "O indicador em kg/barraca e o volume derivado em kg "
        "são medidas diferentes e devem ser interpretados separadamente."
    )


# ==================================================
# ABA 2 — COMPARAÇÃO ENTRE FEIRAS
# ==================================================

with aba2:

    st.subheader(
        "Comparação do volume evitável derivado por feira"
    )

    dados_evitaveis = df[
        df["classification"] == "avoidable_food_waste"
    ].copy()

    evitavel_feira = (
        dados_evitaveis
        .groupby("market_id")
        .agg(
            indicador_kg_barraca=(
                "kg_per_stall",
                "sum"
            ),
            volume_derivado_kg=(
                "kg_total_derivado",
                "sum"
            )
        )
        .reset_index()
    )

    tabela_feiras = (
        feiras_unicas[
            [
                "market_id",
                "name",
                "district",
                "idh",
                "number_of_stalls"
            ]
        ]
        .merge(
            evitavel_feira,
            on="market_id",
            how="left"
        )
        .fillna({
            "indicador_kg_barraca": 0,
            "volume_derivado_kg": 0
        })
    )

    tabela_feiras = tabela_feiras.sort_values(
        "volume_derivado_kg",
        ascending=False
    )

    fig_feiras = px.bar(
        tabela_feiras,
        x="volume_derivado_kg",
        y="name",
        orientation="h",
        color="volume_derivado_kg",
        color_continuous_scale=[
            "#DCE8D8",
            "#2F6B52"
        ],
        labels={
            "volume_derivado_kg": "Volume derivado estimado (kg)",
            "name": "Feira"
        }
    )

    fig_feiras.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        coloraxis_showscale=False,
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_feiras,
        use_container_width=True
    )

    st.subheader("Características das feiras")

    tabela_exibicao = tabela_feiras[
        [
            "name",
            "district",
            "idh",
            "number_of_stalls",
            "indicador_kg_barraca",
            "volume_derivado_kg"
        ]
    ].rename(columns={
        "name": "Feira",
        "district": "Distrito",
        "idh": "IDH informado no estudo",
        "number_of_stalls": "Barracas",
        "indicador_kg_barraca": "Indicador (kg/barraca)",
        "volume_derivado_kg": "Volume derivado estimado (kg)"
    })

    st.dataframe(
        tabela_exibicao.style.format({
            "IDH informado no estudo": "{:.3f}",
            "Indicador (kg/barraca)": "{:.2f}",
            "Volume derivado estimado (kg)": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.warning(
        "A comparação considera apenas quatro feiras observadas "
        "durante uma semana. Não permite generalizar os resultados "
        "para todas as feiras de São Paulo."
    )


# ==================================================
# ABA 3 — ALIMENTOS EVITÁVEIS
# ==================================================

with aba3:

    st.subheader(
        "Composição do desperdício alimentar evitável"
    )

    if dados_evitaveis.empty:

        st.info(
            "Não existem registros de desperdício evitável "
            "para os filtros selecionados."
        )

    else:

        alimentos = (
            dados_evitaveis
            .groupby("category_level_II")
            .agg(
                indicador_kg_barraca=(
                    "kg_per_stall",
                    "sum"
                ),
                volume_derivado_kg=(
                    "kg_total_derivado",
                    "sum"
                )
            )
            .reset_index()
            .sort_values(
                "volume_derivado_kg",
                ascending=False
            )
        )

        alimentos = alimentos.rename(columns={
            "category_level_II": "Alimento ou subcategoria"
        })

        fig_alimentos = px.bar(
            alimentos.head(15),
            x="volume_derivado_kg",
            y="Alimento ou subcategoria",
            orientation="h",
            color="volume_derivado_kg",
            color_continuous_scale=[
                "#DCE8D8",
                "#2F6B52"
            ],
            labels={
                "volume_derivado_kg": "Volume derivado estimado (kg)",
                "Alimento ou subcategoria": "Alimento ou subcategoria"
            }
        )

        fig_alimentos.update_layout(
            yaxis={"categoryorder": "total ascending"},
            showlegend=False,
            coloraxis_showscale=False,
            height=500,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_alimentos,
            use_container_width=True
        )

        st.subheader("Detalhamento por alimento")

        st.dataframe(
            alimentos.style.format({
                "indicador_kg_barraca": "{:.2f}",
                "volume_derivado_kg": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "A classificação como desperdício evitável segue "
            "a classificação do estudo original. Ela não atesta "
            "que os alimentos estejam próprios para consumo ou doação."
        )


# ==================================================
# NOTAS METODOLÓGICAS
# ==================================================

st.divider()

with st.expander(
    "Sobre os dados e limitações metodológicas"
):

    st.markdown("""
    **Fonte:** Brancoli et al. (2022), *Compositional Analysis
    of Street Market Food Waste in Brazil*.

    **Origem dos dados:**
    - Transcrição das tabelas publicadas no estudo.
    - 104 registros distribuídos entre quatro feiras.
    - Coleta realizada durante uma semana de dezembro de 2021.

    **Unidades:**
    - `kg_per_stall`: quilogramas por barraca.
    - `kg_total_derivado`: resultado de
      `kg_per_stall × number_of_stalls`.

    **Limitações:**
    - A amostra contempla somente quatro feiras.
    - O período observado corresponde a uma única semana.
    - Os resultados não representam automaticamente todas
      as feiras do município.
    - Desperdício evitável não significa alimento necessariamente
      seguro para doação.
    - A integração com o cadastro municipal possui caráter exploratório.
    """)

    st.info(
        "Nota metodológica: a faixa de 17 a 34,6 kg por barraca "
        "apresentada na seção 3.1 do estudo considera os resíduos "
        "sem a fração externa. Quando essa fração é incluída, "
        "os valores calculados a partir das tabelas chegam a "
        "38,04 kg por barraca na feira SM4. Portanto, os resultados "
        "são compatíveis quando se considera a diferença de escopo."
    )


# ==================================================
# FONTE
# ==================================================

st.caption(
    "NutriRota | Fonte: Brancoli et al. (2022). "
    "Indicadores derivados a partir das tabelas publicadas."
)
