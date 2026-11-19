import streamlit as st
import plotly.io as pio

# Identidade visual NutriRota — tema escuro.
CORES = {
    "verde_escuro": "#101A17",
    "verde": "#6FA887",
    "verde_medio": "#4F8064",
    "salvia": "#9BC7A8",
    "verde_claro": "#C6DDC9",
    "fundo": "#101A17",
    "superficie": "#1B2C25",
    "superficie_2": "#22372D",
    "texto": "#F0F4F0",
    "texto_sutil": "#A5B5AA",
    "borda": "#30463A",
    "dourado": "#D6B45C",
    "vermelho": "#D4776D",
}

PALETA_GRAFICOS = [
    CORES["verde"],
    CORES["dourado"],
    CORES["salvia"],
    "#7296A8",
    "#B58C65",
    "#A88CB8",
    CORES["vermelho"],
]


def configurar_pagina(titulo="NutriRota"):
    st.set_page_config(
        page_title=f"{titulo} | NutriRota",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    aplicar_tema()


def aplicar_tema():
    # Plotly usa tema escuro; os gráficos existentes preservam seus dados e traços.
    pio.templates.default = "plotly_dark"
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

        :root {
            color-scheme: dark;
            --nr-bg: #101A17;
            --nr-sidebar: #14251F;
            --nr-surface: #1B2C25;
            --nr-surface-2: #22372D;
            --nr-green: #6FA887;
            --nr-green-light: #9BC7A8;
            --nr-text: #F0F4F0;
            --nr-muted: #A5B5AA;
            --nr-border: #30463A;
            --nr-gold: #D6B45C;
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            color: var(--nr-text);
        }
        .stApp, [data-testid="stAppViewContainer"] {
            background: var(--nr-bg);
            color: var(--nr-text);
        }
        [data-testid="stHeader"] { background: rgba(16,26,23,.94); }
        [data-testid="stToolbar"] { right: 1rem; }
        [data-testid="stSidebar"] {
            background: var(--nr-sidebar);
            border-right: 1px solid var(--nr-border);
        }
        [data-testid="stSidebar"] * { color: var(--nr-text); }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: var(--nr-muted);
        }
        [data-testid="stSidebar"] hr { border-color: var(--nr-border); }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            border-radius: 10px;
            padding: .45rem .65rem;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: rgba(155,199,168,.12);
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Manrope', sans-serif !important;
            color: var(--nr-text) !important;
            letter-spacing: -.025em;
        }
        p, li, label, [data-testid="stMarkdownContainer"] {
            color: var(--nr-text);
        }
        [data-testid="stCaptionContainer"], .stCaption {
            color: var(--nr-muted) !important;
        }

        [data-testid="stMetric"] {
            background: var(--nr-surface);
            border: 1px solid var(--nr-border);
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: 0 6px 20px rgba(0,0,0,.14);
        }
        [data-testid="stMetricLabel"] { color: var(--nr-muted) !important; }
        [data-testid="stMetricValue"] {
            color: var(--nr-green-light) !important;
            font-family: 'Manrope', sans-serif;
            font-weight: 800;
        }
        [data-testid="stMetricDelta"] { color: var(--nr-gold) !important; }

        [data-testid="stTabs"] button[role="tab"] {
            color: var(--nr-muted);
            font-weight: 600;
        }
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: var(--nr-green-light);
            border-bottom-color: var(--nr-green);
        }
        [data-testid="stExpander"] {
            background: var(--nr-surface);
            border: 1px solid var(--nr-border);
            border-radius: 13px;
        }
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid var(--nr-border);
            border-radius: 12px;
            overflow: hidden;
        }
        .stButton button, .stDownloadButton button {
            border-radius: 10px;
            border: 1px solid var(--nr-green);
            font-weight: 600;
            background: var(--nr-surface-2);
            color: var(--nr-text);
        }
        .stButton button:hover, .stDownloadButton button:hover {
            border-color: var(--nr-green-light);
            color: var(--nr-green-light);
            background: #294436;
        }
        .stButton button[kind="primary"] {
            background: var(--nr-green);
            color: #101A17;
        }
        div[data-testid="stAlert"] { border-radius: 12px; }
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div {
            background: var(--nr-surface) !important;
            border-color: var(--nr-border) !important;
            color: var(--nr-text) !important;
        }
        input, textarea { color: var(--nr-text) !important; }
        [data-baseweb="popover"] > div,
        [data-baseweb="menu"] {
            background: var(--nr-surface) !important;
            color: var(--nr-text) !important;
        }
        hr { border-color: var(--nr-border); }
        a { color: var(--nr-green-light); }

        .nr-eyebrow {
            color: var(--nr-green-light);
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .15em;
            text-transform: uppercase;
            margin-bottom: .35rem;
        }
        .nr-hero {
            background: linear-gradient(118deg, #14251F 0%, #1D4935 72%, #35694B 100%);
            border: 1px solid rgba(155,199,168,.18);
            border-radius: 22px;
            padding: 2.3rem 2.5rem;
            margin: .5rem 0 1.8rem;
            color: white;
            box-shadow: 0 14px 35px rgba(0,0,0,.22);
        }
        .nr-hero .eyebrow {
            color: #D6E7D8;
            font-size: .72rem;
            letter-spacing: .17em;
            font-weight: 800;
            text-transform: uppercase;
        }
        .nr-hero h1 {
            color: white !important;
            font-size: clamp(2rem, 4vw, 3rem) !important;
            margin: .65rem 0 .55rem;
            line-height: 1.12;
        }
        .nr-hero p {
            color: #E2EEE4;
            max-width: 760px;
            line-height: 1.7;
            margin: 0;
            font-size: 1rem;
        }
        .nr-card {
            background: var(--nr-surface);
            border: 1px solid var(--nr-border);
            border-radius: 16px;
            padding: 1.2rem 1.3rem;
            min-height: 150px;
            box-shadow: 0 6px 20px rgba(0,0,0,.14);
        }
        .nr-card .icon { font-size: 1.45rem; margin-bottom: .6rem; }
        .nr-card h4 {
            color: var(--nr-green-light);
            font-family: 'Manrope', sans-serif;
            margin: 0 0 .4rem;
            font-size: 1rem;
        }
        .nr-card p { color: var(--nr-muted); margin: 0; line-height: 1.55; font-size: .88rem; }
        .nr-footer {
            border-top: 1px solid var(--nr-border);
            color: var(--nr-muted);
            text-align: center;
            padding: 1.5rem 0 .5rem;
            margin-top: 2rem;
            font-size: .78rem;
        }
        #MainMenu, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
