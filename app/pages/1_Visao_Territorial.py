import streamlit as st
import plotly.express as px
import pandas as pd

from utils.data_loader import carregar_feiras



from utils.theme import configurar_pagina, CORES, PALETA_GRAFICOS

configurar_pagina("1 Visao Territorial")

# ==================================================
# CONFIGURAÇÃO
# ==================================================

st.title("Visão Territorial")
st.caption(
    "Explore a distribuição das feiras livres "
    "no município de São Paulo."
)


# ==================================================
# CARREGAMENTO DOS DADOS
# ==================================================

feiras = carregar_feiras()
df = feiras.copy()


# ==================================================
# TRATAMENTO ANALÍTICO
# Preserva os dados originais
# ==================================================

# Preservar os valores originais
df["dia_feira_original"] = df["dia_feira"]
df["categoria_original"] = df["categoria"]

# Padronização dos dias da semana
df["dia_analise"] = (
    df["dia_feira"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
)

# Identificação de quarta-feira noturna
df["periodo_observado"] = "NÃO INFORMADO"

mascara_noturna = df["dia_analise"].eq("QUA NOTURNA")

df.loc[mascara_noturna, "dia_analise"] = "QUA"
df.loc[mascara_noturna, "periodo_observado"] = "NOTURNA"

# Unificação das grafias de sábado
df["dia_analise"] = df["dia_analise"].replace({
    "SAB": "SÁB"
})

# Padronização das categorias
df["categoria_analise"] = (
    df["categoria"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .replace({
        "ÔRGANICA": "ORGÂNICA",
        "ORGANICA": "ORGÂNICA"
    })
)

# Conversão numérica
df["quantidade_feirantes"] = pd.to_numeric(
    df["quantidade_feirantes"],
    errors="coerce"
)


# ==================================================
# FILTROS
# ==================================================

st.sidebar.divider()
st.sidebar.subheader("Filtros territoriais")

# Filtro de subprefeitura
subprefeituras = sorted(
    df["subprefeitura"].dropna().unique().tolist()
)

selecionadas = st.sidebar.multiselect(
    "Subprefeitura",
    options=subprefeituras,
    default=subprefeituras
)

# Filtro de dia da semana
dias = sorted(
    df["dia_analise"].dropna().unique().tolist()
)

dias_selecionados = st.sidebar.multiselect(
    "Dia da semana",
    options=dias,
    default=dias
)

# Filtro de categoria
categorias = sorted(
    df["categoria_analise"].dropna().unique().tolist()
)

categorias_selecionadas = st.sidebar.multiselect(
    "Categoria da feira",
    options=categorias,
    default=categorias
)

# Aplicação dos filtros
df_filtrado = df[
    (df["subprefeitura"].isin(selecionadas))
    & (df["dia_analise"].isin(dias_selecionados))
    & (df["categoria_analise"].isin(categorias_selecionadas))
].copy()


# ==================================================
# INDICADORES
# ==================================================

total_feiras = len(df_filtrado)

total_subprefeituras = (
    df_filtrado["subprefeitura"].nunique()
)

total_feirantes = (
    df_filtrado["quantidade_feirantes"].sum()
)

media_feirantes = (
    df_filtrado["quantidade_feirantes"].mean()
    if not df_filtrado["quantidade_feirantes"].dropna().empty
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Registros no cadastro municipal",
    f"{total_feiras:,}".replace(",", ".")
)

col2.metric(
    "Agrupamentos territoriais",
    total_subprefeituras
)

col3.metric(
    "Feirantes registrados",
    f"{total_feirantes:,.0f}".replace(",", ".")
)

col4.metric(
    "Média de feirantes por feira",
    f"{media_feirantes:.1f}"
)

st.divider()


# ==================================================
# GRÁFICOS
# ==================================================

if df_filtrado.empty:

    st.warning(
        "Nenhum registro encontrado para os filtros selecionados."
    )

else:

    col_grafico1, col_grafico2 = st.columns(2)

    # ----------------------------------------------
    # GRÁFICO 1 — FEIRAS POR SUBPREFEITURA
    # ----------------------------------------------

    with col_grafico1:

        st.subheader("Registros por agrupamento territorial")

        dados_sub = (
            df_filtrado
            .groupby("subprefeitura")
            .size()
            .reset_index(name="total_feiras")
            .sort_values("total_feiras", ascending=True)
        )

        fig_sub = px.bar(
            dados_sub,
            x="total_feiras",
            y="subprefeitura",
            orientation="h",
            labels={
                "total_feiras": "Quantidade de registros",
                "subprefeitura": "Agrupamento territorial"
            },
            color="total_feiras",
            color_continuous_scale=[
                "#DCE8D8",
                "#2F6B52"
            ]
        )

        fig_sub.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            height=500,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_sub,
            use_container_width=True
        )

    # ----------------------------------------------
    # GRÁFICO 2 — DISTRIBUIÇÃO POR DIA
    # ----------------------------------------------

    with col_grafico2:

        st.subheader("Distribuição por dia da semana")

        dados_dias = (
            df_filtrado
            .groupby("dia_analise")
            .size()
            .reset_index(name="total_feiras")
            .sort_values("total_feiras", ascending=False)
        )

        fig_dias = px.pie(
            dados_dias,
            names="dia_analise",
            values="total_feiras",
            hole=0.55,
            color_discrete_sequence=PALETA_GRAFICOS
        )

        fig_dias.update_layout(
            height=500,
            legend_title_text="Dia da semana",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_dias,
            use_container_width=True
        )


    # ==================================================
    # ANÁLISE COMPLEMENTAR
    # ==================================================

    st.divider()
    st.subheader("Distribuição por categoria")

    dados_categoria = (
        df_filtrado
        .groupby("categoria_analise")
        .size()
        .reset_index(name="total_feiras")
        .sort_values("total_feiras", ascending=False)
    )

    fig_categoria = px.bar(
        dados_categoria,
        x="categoria_analise",
        y="total_feiras",
        labels={
            "categoria_analise": "Categoria",
            "total_feiras": "Quantidade de feiras"
        },
        color="total_feiras",
        color_continuous_scale=[
            "#DCE8D8",
            "#2F6B52"
        ]
    )

    fig_categoria.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_categoria,
        use_container_width=True
    )


    # ==================================================
    # TABELA DE DADOS
    # ==================================================

    st.divider()
    st.subheader("Registros do cadastro municipal de feiras livres")

    st.caption(
        "Consulte os registros municipais conforme os filtros aplicados. A contagem representa linhas do cadastro, não necessariamente feiras únicas."
    )

    colunas_tabela = [
        "subprefeitura",
        "dia_feira_original",
        "periodo_observado",
        "categoria_original",
        "quantidade_feirantes",
        "nome_feira",
        "bairro",
        "logradouro"
    ]

    st.dataframe(
        df_filtrado[colunas_tabela],
        use_container_width=True,
        hide_index=True
    )

    # Download
    csv = df_filtrado.to_csv(
        index=False,
        sep=";"
    ).encode("utf-8-sig")

    st.download_button(
        label="Baixar dados filtrados",
        data=csv,
        file_name="nutrirota_feiras_filtradas.csv",
        mime="text/csv"
    )


# ==================================================
# FONTE E OBSERVAÇÕES
# ==================================================

st.divider()

st.caption(
    "Fonte: Cadastro de Feiras Livres da Prefeitura de São Paulo."
)

st.caption(
    "A base contém registros cadastrais municipais e agrupamentos territoriais. "
    "Não correspondem a medições de desperdício, vendas ou excedente alimentar."
)
