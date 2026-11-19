import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import (
    carregar_feiras,
    carregar_brancoli,
    carregar_conab,
    carregar_csv,
    carregar_inmet,
)


from utils.theme import configurar_pagina, CORES, PALETA_GRAFICOS

configurar_pagina("4 Insights")

# ============================================================
# INSIGHTS ESTRATÉGICOS — NUTRIROTA
# Esta página integra indicadores de fontes diferentes sem
# misturá-las como se representassem a mesma população.
# ============================================================

st.title("Insights Estratégicos")
st.caption(
    "Síntese das evidências territoriais, do estudo de desperdício "
    "e da inteligência de preços do NutriRota."
)

VERDE = "#2F6B52"
VERDE_MEDIO = "#5F8D70"
VERDE_CLARO = "#9DB9A1"
AMARELO = "#D6B45C"


def fmt_num(valor, casas=2):
    return (
        f"{valor:,.{casas}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def fmt_int(valor):
    return f"{int(valor):,}".replace(",", ".")


def estilo_figura(fig, altura=380):
    fig.update_layout(
        height=altura,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=15, t=35, b=10),
        font=dict(size=12),
    )
    return fig


# ----------------------------
# Carregamento e validação
# ----------------------------

try:
    feiras = carregar_feiras().copy()
    brancoli = carregar_brancoli().copy()
    conab = carregar_conab().copy()
    resultados = carregar_csv("resultados_modelos_conab.csv").copy()
    inmet = carregar_inmet().copy()
except FileNotFoundError as erro:
    st.error(
        "Não foi possível carregar um dos arquivos necessários. "
        f"Verifique os arquivos em data/processed. Detalhe: {erro}"
    )
    st.stop()

colunas_feiras = {
    "subprefeitura", "dia_feira", "categoria",
    "quantidade_feirantes", "nome_feira"
}
colunas_brancoli = {
    "market_id", "name", "number_of_stalls",
    "kg_per_stall", "classification", "category_level_II"
}
colunas_conab = {
    "produto", "ceasa", "data_ref", "preco"
}
colunas_resultados = {
    "experimento", "recorte", "n", "modelo",
    "mae", "rmse", "mape_pct", "r2",
    "periodo_teste", "fonte"
}

for nome, base, obrigatorias in [
    ("Prefeitura", feiras, colunas_feiras),
    ("Brancoli", brancoli, colunas_brancoli),
    ("CONAB", conab, colunas_conab),
    ("Resultados ML", resultados, colunas_resultados),
]:
    faltantes = obrigatorias.difference(base.columns)
    if faltantes:
        st.error(
            f"A base {nome} não contém as colunas esperadas: "
            + ", ".join(sorted(faltantes))
        )
        st.stop()


# ============================================================
# 1. TERRITÓRIO — CADASTRO MUNICIPAL
# ============================================================

feiras["quantidade_feirantes"] = pd.to_numeric(
    feiras["quantidade_feirantes"], errors="coerce"
)
feiras["dia_analise"] = (
    feiras["dia_feira"].fillna("Não informado").astype(str).str.strip().str.upper()
)
feiras["dia_analise"] = feiras["dia_analise"].replace({"SAB": "SÁB"})
feiras.loc[feiras["dia_analise"] == "QUA NOTURNA", "dia_analise"] = "QUA"

total_registros_feiras = len(feiras)
total_subprefeituras = feiras["subprefeitura"].nunique()
total_feirantes_informados = feiras["quantidade_feirantes"].sum()
registros_zero_feirantes = int((feiras["quantidade_feirantes"] == 0).sum())

feiras_sub = (
    feiras.groupby("subprefeitura")
    .size()
    .sort_values(ascending=False)
    .head(10)
    .sort_values()
    .reset_index(name="registros")
)
feiras_dia = (
    feiras["dia_analise"]
    .value_counts()
    .rename_axis("dia")
    .reset_index(name="registros")
)


# ============================================================
# 2. DESPERDÍCIO — BRANCOLI ET AL. (2022)
# ============================================================

brancoli["kg_per_stall"] = pd.to_numeric(
    brancoli["kg_per_stall"], errors="coerce"
)
brancoli["number_of_stalls"] = pd.to_numeric(
    brancoli["number_of_stalls"], errors="coerce"
)
brancoli["volume_derivado_kg"] = (
    brancoli["kg_per_stall"] * brancoli["number_of_stalls"]
)

volumes_classificacao = (
    brancoli.groupby("classification")["volume_derivado_kg"].sum()
)
volume_evitavel = float(
    volumes_classificacao.get("avoidable_food_waste", 0)
)
volume_inevitavel = float(
    volumes_classificacao.get("unavoidable_food_waste", 0)
)
volume_embalagens = float(
    volumes_classificacao.get("packaging", 0)
)
volume_externo = float(
    volumes_classificacao.get("external_waste", 0)
)
volume_total = float(brancoli["volume_derivado_kg"].sum())
volume_sem_externo = volume_total - volume_externo
pct_evitavel_sem_externo = (
    volume_evitavel / volume_sem_externo * 100
    if volume_sem_externo > 0 else 0
)
feiras_brancoli = brancoli["market_id"].nunique()
registros_brancoli = len(brancoli)

nomes_classificacao = {
    "avoidable_food_waste": "Desperdício evitável",
    "unavoidable_food_waste": "Desperdício inevitável",
    "packaging": "Embalagens",
    "external_waste": "Resíduos externos",
}
composicao = (
    volumes_classificacao.rename(index=nomes_classificacao)
    .rename_axis("classificacao")
    .reset_index(name="volume_kg")
)

alimentos_evitaveis = brancoli[
    brancoli["classification"] == "avoidable_food_waste"
].copy()
ranking_alimentos = (
    alimentos_evitaveis.groupby("category_level_II")["volume_derivado_kg"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .sort_values()
    .reset_index()
)


# ============================================================
# 3. CONAB — PREÇOS E COBERTURA DA BASE
# ============================================================

conab["preco"] = pd.to_numeric(conab["preco"], errors="coerce")
conab["data_ref"] = pd.to_datetime(conab["data_ref"], errors="coerce")

precos_validos = conab[
    conab["preco"].gt(0) & conab["data_ref"].notna()
].copy()

n_registros_conab = len(conab)
n_produtos = conab["produto"].nunique()
n_ceasas = conab["ceasa"].nunique()
n_referencias = conab["data_ref"].nunique()
n_ausentes_conab = int(conab["preco"].isna().sum())
n_zeros_conab = int(conab["preco"].eq(0).sum())

preco_medio_geral = (
    precos_validos["preco"].mean() if not precos_validos.empty else float("nan")
)
ultima_referencia = precos_validos["data_ref"].max() if not precos_validos.empty else None

preco_produto = (
    precos_validos.groupby("produto")["preco"]
    .mean()
    .sort_values(ascending=False)
    .reset_index(name="preco_medio")
)


# ============================================================
# 4. MODELOS — RESULTADOS EXPORTADOS DO NOTEBOOK 03
# ============================================================

for coluna in ["n", "mae", "rmse", "mape_pct", "r2"]:
    resultados[coluna] = pd.to_numeric(resultados[coluna], errors="coerce")

painel_nacional = resultados[
    resultados["experimento"] == "CONAB - Painel Nacional"
].copy()
recorte_geral = painel_nacional[
    painel_nacional["recorte"] == "Geral (todas com dados no teste)"
].copy()

melhor_geral = (
    recorte_geral.loc[recorte_geral["mae"].idxmin()]
    if not recorte_geral.empty else None
)

clima = resultados[
    resultados["experimento"] == "CEAGESP + INMET"
].copy()

rf_com_clima = clima[
    clima["modelo"] == "Random Forest - Com clima"
]
rf_sem_clima = clima[
    clima["modelo"] == "Random Forest - Sem clima"
]

reducao_mae_rf_pct = None
if not rf_com_clima.empty and not rf_sem_clima.empty:
    mae_rf_com = float(rf_com_clima.iloc[0]["mae"])
    mae_rf_sem = float(rf_sem_clima.iloc[0]["mae"])
    if mae_rf_sem != 0:
        reducao_mae_rf_pct = (
            (mae_rf_sem - mae_rf_com) / mae_rf_sem * 100
        )


# ============================================================
# VISÃO EXECUTIVA
# ============================================================

st.subheader("Visão executiva")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros no cadastro municipal", fmt_int(total_registros_feiras))
c2.metric("Agrupamentos de subprefeitura", fmt_int(total_subprefeituras))
c3.metric("Feiras no estudo Brancoli", fmt_int(feiras_brancoli))
c4.metric("Produtos na base CONAB", fmt_int(n_produtos))

st.caption(
    "Os indicadores acima vêm de bases distintas: cadastro municipal, "
    "estudo científico e série de preços. Não representam uma única amostra integrada."
)

st.divider()


# ============================================================
# 1. TERRITÓRIO
# ============================================================

st.subheader("1. Distribuição territorial das feiras")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Dez agrupamentos com mais registros**")
    fig = px.bar(
        feiras_sub,
        x="registros",
        y="subprefeitura",
        orientation="h",
        labels={"registros": "Registros de feiras", "subprefeitura": "Agrupamento"},
        color="registros",
        color_continuous_scale=[VERDE_CLARO, VERDE],
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(estilo_figura(fig, 430), use_container_width=True)

with col_b:
    st.markdown("**Registros por dia da semana**")
    fig = px.pie(
        feiras_dia,
        names="dia",
        values="registros",
        hole=0.55,
        color_discrete_sequence=[
            VERDE, VERDE_MEDIO, VERDE_CLARO, AMARELO,
            "#DCE8D8", "#B95C50", "#7D9184",
        ],
    )
    st.plotly_chart(estilo_figura(fig, 430), use_container_width=True)

st.info(
    f"O cadastro contém {fmt_int(total_registros_feiras)} registros e "
    f"{fmt_int(total_subprefeituras)} agrupamentos territoriais. "
    f"A soma do campo de feirantes informados é {fmt_int(total_feirantes_informados)}, "
    f"mas {registros_zero_feirantes} registros apresentam valor zero. "
    "Esse campo é cadastral: não deve ser interpretado como contagem de pessoas "
    "únicas nem como medida de desperdício."
)


# ============================================================
# 2. DESPERDÍCIO
# ============================================================

st.divider()
st.subheader("2. Evidências sobre desperdício alimentar")

st.caption(
    "Brancoli et al. (2022): quatro feiras, uma semana de coleta "
    "em dezembro de 2021. Os volumes abaixo são derivados das tabelas "
    "do estudo pela multiplicação de kg por barraca pelo número de barracas."
)

c1, c2, c3 = st.columns(3)
c1.metric("Volume derivado total", f"{fmt_num(volume_total)} kg")
c2.metric("Desperdício evitável derivado", f"{fmt_num(volume_evitavel)} kg")
c3.metric("Evitável / resíduos da feira", f"{fmt_num(pct_evitavel_sem_externo)}%")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Composição do volume derivado**")
    fig = px.pie(
        composicao,
        names="classificacao",
        values="volume_kg",
        hole=0.55,
        color_discrete_sequence=[VERDE, VERDE_MEDIO, VERDE_CLARO, AMARELO],
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(estilo_figura(fig, 420), use_container_width=True)

with col_b:
    st.markdown("**Categorias com maior volume evitável derivado**")
    if not ranking_alimentos.empty:
        fig = px.bar(
            ranking_alimentos,
            x="volume_derivado_kg",
            y="category_level_II",
            orientation="h",
            labels={
                "volume_derivado_kg": "Volume derivado (kg)",
                "category_level_II": "Categoria do estudo",
            },
            color="volume_derivado_kg",
            color_continuous_scale=[VERDE_CLARO, VERDE],
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(estilo_figura(fig, 420), use_container_width=True)
    else:
        st.info("Não há categorias evitáveis disponíveis para exibição.")

st.warning(
    "A amostra do estudo contempla somente quatro feiras e uma semana. "
    "Não representa automaticamente todas as feiras de São Paulo. "
    "Além disso, 'desperdício evitável' é uma classificação do estudo e "
    "não comprova que o alimento esteja próprio para consumo ou doação."
)


# ============================================================
# 3. MERCADO E MODELOS
# ============================================================

st.divider()
st.subheader("3. Inteligência de mercado e modelagem")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros CONAB", fmt_int(n_registros_conab))
c2.metric("CEASAs na base", fmt_int(n_ceasas))
c3.metric("Referências mensais", fmt_int(n_referencias))
c4.metric(
    "Preço médio dos registros válidos",
    f"R$ {fmt_num(preco_medio_geral, 2)}/kg" if pd.notna(preco_medio_geral) else "—",
)

if ultima_referencia is not None:
    st.caption(
        f"Período da base: {precos_validos['data_ref'].min():%m/%Y} a "
        f"{ultima_referencia:%m/%Y}. Produtos: {n_produtos}."
    )

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Preço médio por produto**")
    if not preco_produto.empty:
        dados_plot = preco_produto.sort_values("preco_medio")
        fig = px.bar(
            dados_plot,
            x="preco_medio",
            y="produto",
            orientation="h",
            labels={"preco_medio": "Preço médio (R$/kg)", "produto": "Produto"},
            color="preco_medio",
            color_continuous_scale=[VERDE_CLARO, VERDE],
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(estilo_figura(fig, 430), use_container_width=True)

with col_b:
    st.markdown("**Resultado do painel nacional — teste final**")
    if melhor_geral is not None:
        st.metric("Melhor modelo pelo menor MAE", str(melhor_geral["modelo"]))
        st.metric("MAE", f"R$ {fmt_num(melhor_geral['mae'], 4)}/kg")
        st.metric("R²", fmt_num(melhor_geral["r2"], 4))
        st.caption(
            f"Recorte: {melhor_geral['recorte']} | "
            f"n = {int(melhor_geral['n'])} | "
            f"Teste: {melhor_geral['periodo_teste']}."
        )
    else:
        st.info("Não foi localizado o recorte geral no CSV de resultados.")

if not recorte_geral.empty:
    st.markdown("**Comparação dos modelos no recorte geral**")
    grafico_modelos = recorte_geral[["modelo", "mae"]].copy()
    fig = px.bar(
        grafico_modelos.sort_values("mae", ascending=True),
        x="modelo",
        y="mae",
        text="mae",
        labels={"modelo": "Modelo", "mae": "MAE (R$/kg)"},
        color="modelo",
    )
    fig.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig.update_layout(showlegend=False)
    st.plotly_chart(estilo_figura(fig, 350), use_container_width=True)

with st.expander("Comparação dos três recortes da modelagem nacional"):
    st.dataframe(
        painel_nacional[
            ["recorte", "n", "modelo", "mae", "rmse", "mape_pct", "r2"]
        ].rename(
            columns={
                "recorte": "Recorte",
                "n": "Observações de teste",
                "modelo": "Modelo",
                "mae": "MAE (R$/kg)",
                "rmse": "RMSE (R$/kg)",
                "mape_pct": "MAPE (%)",
                "r2": "R²",
            }
        ).style.format(
            {
                "MAE (R$/kg)": "{:.4f}",
                "RMSE (R$/kg)": "{:.4f}",
                "MAPE (%)": "{:.4f}",
                "R²": "{:.4f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

with st.expander("Experimento complementar com INMET — CEAGESP-SP"):
    if not clima.empty:
        st.dataframe(
            clima[
                ["modelo", "n", "mae", "rmse", "mape_pct", "r2"]
            ].rename(
                columns={
                    "modelo": "Modelo",
                    "n": "Observações de teste",
                    "mae": "MAE (R$/kg)",
                    "rmse": "RMSE (R$/kg)",
                    "mape_pct": "MAPE (%)",
                    "r2": "R²",
                }
            ).style.format(
                {
                    "MAE (R$/kg)": "{:.4f}",
                    "RMSE (R$/kg)": "{:.4f}",
                    "MAPE (%)": "{:.4f}",
                    "R²": "{:.4f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
        if reducao_mae_rf_pct is not None:
            st.write(
                f"No experimento da CEAGESP, o Random Forest com clima "
                f"teve MAE {fmt_num(reducao_mae_rf_pct, 2)}% menor que "
                "a versão sem clima neste teste específico."
            )
        st.caption(
            "O teste tem 30 observações (julho a setembro de 2026). "
            "A diferença é pequena e não demonstra causalidade nem "
            "garante melhoria em outros períodos ou centrais."
        )
    else:
        st.info("Não há linhas do experimento CEAGESP + INMET no CSV.")

st.caption(
    f"Qualidade da base CONAB: {fmt_int(n_ausentes_conab)} preços ausentes "
    f"e {fmt_int(n_zeros_conab)} preços iguais a zero no arquivo consolidado. "
    "Os valores originais são preservados; registros não positivos não entram "
    "no cálculo do preço médio exibido."
)


# ============================================================
# 4. LEITURAS ESTRATÉGICAS — SEM EXTRAPOLAR AS FONTES
# ============================================================

st.divider()
st.subheader("4. O que os dados indicam para o NutriRota")

with st.container(border=True):
    st.markdown("**01 — O cadastro municipal pode orientar a articulação territorial**")
    st.write(
        "A distribuição dos registros de feiras ajuda a identificar onde "
        "a solução pode iniciar a aproximação com feirantes e organizações "
        "receptoras. A concentração cadastral, sozinha, não mede desperdício "
        "nem demanda por doações."
    )

with st.container(border=True):
    st.markdown("**02 — O estudo de campo justifica o foco em excedentes evitáveis**")
    st.write(
        f"Nas quatro feiras estudadas, o volume evitável derivado foi de "
        f"{fmt_num(volume_evitavel)} kg. Esse resultado reforça a relevância "
        "de mecanismos de prevenção e redistribuição, mas não deve ser "
        "extrapolado para todo o município."
    )

with st.container(border=True):
    st.markdown("**03 — Preços são uma camada complementar de contexto**")
    st.write(
        "A modelagem da CONAB estima preços mensais de hortifrúti, com seleção "
        "por validação cruzada temporal e avaliação final em período posterior. "
        "Ela pode apoiar análises de mercado e planejamento, mas não é um modelo "
        "de previsão de desperdício ou de excedente."
    )

with st.container(border=True):
    st.markdown("**04 — O próximo salto depende de dados operacionais próprios**")
    st.write(
        "Para estimar excedentes reais por feira, o NutriRota precisará "
        "registrar, ao longo do tempo, quantidade comprada, estoque, "
        "vendas, sobras, perdas e destinação dos alimentos. Esses registros "
        "permitirão construir e validar futuramente um modelo específico."
    )


# ============================================================
# FONTES E LIMITAÇÕES
# ============================================================

st.divider()
with st.expander("Fontes, escopo e limitações"):
    st.markdown(
        """
        **Prefeitura de São Paulo**
        - Cadastro normalizado: 933 registros.
        - 31 agrupamentos territoriais no campo `subprefeitura`; não interpretar como 31 subprefeituras oficiais.
        - A contagem apresentada corresponde a registros do cadastro, não a uma deduplicação de feiras únicas.
        - O campo de quantidade de feirantes é cadastral; 23 registros
          possuem valor zero.
        - A base não contém vendas, estoque nem pesagem de desperdício.

        **Brancoli et al. (2022)**
        - 104 linhas transcritas das tabelas publicadas.
        - Quatro feiras, 26 linhas por feira.
        - Coleta durante uma semana de dezembro de 2021.
        - Os volumes em kg desta página são derivados por
          `kg_per_stall × number_of_stalls`.
        - A correspondência com o cadastro municipal é exploratória,
          não uma vinculação oficial.

        **CONAB**
        - 3.000 registros consolidados, 10 produtos, 12 CEASAs
          e 25 referências mensais, de setembro de 2024 a setembro de 2026.
        - A base contém valores ausentes e zeros; eles não são tratados
          como preços válidos no indicador de média.

        **INMET**
        - Série mensal da estação A701, em São Paulo, com 25 referências.
        - Utilizada apenas no experimento complementar CEAGESP-SP.

        **Machine Learning**
        - Alvo: preço mensal (`preco`, R$/kg).
        - Modelos comparados: Baseline Lag 1, Ridge e Random Forest.
        - Validação cruzada temporal: `TimeSeriesSplit` com três folds expansivos e três meses por fold.
        - Os folds são separados por mês; o pré-processamento é ajustado apenas no treino de cada fold.
        - Seleção de hiperparâmetros pelo MAE médio da validação temporal.
        - Teste final preservado: julho a setembro de 2026.
        - Os resultados exibidos são carregados do CSV exportado pelo Notebook 03.
        - Os modelos atuais não predizem kg de desperdício ou excedente.

        **Limitação central do projeto**
        - As fontes têm unidades, períodos e populações diferentes.
          Portanto, não devem ser somadas nem interpretadas como uma
          única base observacional.
        """
    )

st.caption(
    "NutriRota | Síntese analítica baseada nas bases da Prefeitura de São Paulo, "
    "Brancoli et al. (2022), CONAB e INMET."
)
