from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"


@st.cache_data
def carregar_csv(nome: str, sep: str = ",") -> pd.DataFrame:
    caminho = DATA / nome
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    return pd.read_csv(caminho, sep=sep)


def carregar_feiras():
    return carregar_csv("prefeitura_sp_feiras_livres_normalizado.csv", sep=";")


def carregar_brancoli():
    return carregar_csv("brancoli_2022_base_com_prefeitura.csv")


def carregar_conab():
    return carregar_csv("conab_precos_consolidados.csv")


def carregar_inmet():
    return carregar_csv("inmet_sp_mensal.csv")


def carregar_resultados_modelos_conab():
    return carregar_csv("resultados_modelos_conab.csv")


def carregar_inmet_horario():
    return carregar_csv("inmet_sp_horario.csv")


def carregar_brancoli_integrada():
    return carregar_csv("brancoli_2022_base_integrada.csv")


def carregar_correspondencias():
    return carregar_csv("correspondencias_brancoli_prefeitura.csv")


def carregar_feiras_correcao():
    return carregar_csv("prefeitura_sp_feiras_livres_correcoes.csv")


def carregar_auditoria_feiras():
    return carregar_csv("prefeitura_sp_valores_unicos_auditoria.csv")
