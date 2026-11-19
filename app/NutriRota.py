import streamlit as st
from utils.data_loader import (
    carregar_feiras,
    carregar_brancoli,
    carregar_conab,
)
from utils.theme import configurar_pagina, CORES

configurar_pagina("Visão geral")

try:
    feiras = carregar_feiras()
    brancoli = carregar_brancoli()
    conab = carregar_conab()
except Exception as erro:
    st.error(f"Não foi possível carregar os dados: {erro}")
    st.stop()

with st.sidebar:
    st.markdown(
        "<div style='font-family:Manrope,sans-serif;font-size:1.65rem;"
        "font-weight:800;color:white;padding:.35rem 0 0'>🌱 NutriRota</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:.67rem;letter-spacing:.19em;color:#BFD4C4;"
        "font-weight:700;margin-bottom:1.4rem'>DATA • FOOD • IMPACT</div>",
        unsafe_allow_html=True,
    )
    st.caption("GLOBAL SOLUTION 2026")
    st.caption("CitizenTech • FIAP")

st.markdown(
    """
    <section class="nr-hero">
      <div class="eyebrow">CitizenTech · Data Intelligence</div>
      <h1>Menos desperdício.<br>Mais possibilidades.</h1>
      <p>Transformando dados em inteligência para compreender os resíduos alimentares,
      analisar o abastecimento e apoiar caminhos para um sistema alimentar mais sustentável.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="nr-eyebrow">PANORAMA DO PROJETO</div>', unsafe_allow_html=True)
st.header("NutriRota em números")

c1, c2, c3 = st.columns(3)
c1.metric("Registros no cadastro municipal", f"{len(feiras):,}".replace(",", "."))
c2.metric("Registros transcritos do estudo Brancoli", f"{len(brancoli):,}".replace(",", "."))
c3.metric("Registros de preços CONAB", f"{len(conab):,}".replace(",", "."))

st.caption(
    "Indicadores referentes às bases utilizadas na prova de conceito. "
    "São registros de fontes distintas e não representam quantidade de alimentos desperdiçados ou doados."
)

st.divider()
st.markdown('<div class="nr-eyebrow">EXPLORE A PLATAFORMA</div>', unsafe_allow_html=True)
st.header("Inteligência alimentar em diferentes perspectivas")

c1, c2 = st.columns(2)
with c1:
    st.markdown(
        """<div class="nr-card">
        <h4>Mapeamento territorial</h4>
        <p>Explore a distribuição cadastral das feiras livres de São Paulo e suas características territoriais.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        """<div class="nr-card">
        <h4>Inteligência de preços</h4>
        <p>Analise a evolução dos preços hortigranjeiros e os resultados da modelagem mensal da CONAB.</p>
        </div>""",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """<div class="nr-card">
        <h4>Análise de desperdício</h4>
        <p>Conheça a composição dos resíduos observados nas quatro feiras estudadas por Brancoli et al.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown(
        """<div class="nr-card">
        <h4>Insights estratégicos</h4>
        <p>Explore os principais resultados, limitações e oportunidades identificadas nas análises.</p>
        </div>""",
        unsafe_allow_html=True,
    )

st.divider()
st.markdown('<div class="nr-eyebrow">NOSSO PROPÓSITO</div>', unsafe_allow_html=True)
st.header("Dados que conectam pessoas e oportunidades.")
st.markdown(
    "A NutriRota é uma proposta de plataforma que busca aproximar feirantes, pequenos comércios, "
    "supermercados e distribuidores de bancos de alimentos e organizações sociais. "
    "A prova de conceito reúne análises de resíduos alimentares, dados territoriais e inteligência "
    "de preços para apoiar o desenvolvimento dessa solução."
)
st.info(
    "Os modelos de Machine Learning desta etapa estimam preços mensais de produtos (R$/kg). "
    "A previsão direta de excedentes alimentares depende de dados operacionais próprios "
    "— como estoque, compras, vendas, sobras e destinação — e permanece como evolução futura."
)

with st.expander("Consultar bases de dados utilizadas"):
    aba1, aba2, aba3 = st.tabs(["Prefeitura", "Brancoli", "CONAB"])
    with aba1:
        st.dataframe(feiras.head(100), use_container_width=True, hide_index=True)
        st.caption(f"Total de registros: {len(feiras):,}".replace(",", "."))
    with aba2:
        st.dataframe(brancoli.head(100), use_container_width=True, hide_index=True)
        st.caption(f"Total de registros: {len(brancoli):,}".replace(",", "."))
    with aba3:
        st.dataframe(conab.head(100), use_container_width=True, hide_index=True)
        st.caption(f"Total de registros: {len(conab):,}".replace(",", "."))

st.markdown(
    """<div class="nr-footer">NUTRIROTA © 2026 · GLOBAL SOLUTION FIAP<br>
    Tecnologia e dados a serviço de um sistema alimentar mais sustentável.</div>""",
    unsafe_allow_html=True,
)
