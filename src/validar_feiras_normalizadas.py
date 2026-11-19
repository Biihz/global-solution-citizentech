
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ORIGINAL = ROOT / "data/raw/prefeitura_sp_feiras_livres.csv"
NORMALIZADO = ROOT / "data/processed/prefeitura_sp_feiras_livres_normalizado.csv"
CORRECOES = ROOT / "data/processed/prefeitura_sp_feiras_livres_correcoes.csv"

df_original = pd.read_csv(ORIGINAL, sep=";", encoding="utf-8-sig", dtype=str)
df_normalizado = pd.read_csv(NORMALIZADO, sep=";", encoding="utf-8-sig", dtype=str)
df_correcoes = pd.read_csv(CORRECOES, sep=";", encoding="utf-8-sig")

print("\n===== VALIDAÇÃO DA BASE NORMALIZADA =====")

print(f"Registros originais: {len(df_original)}")
print(f"Registros normalizados: {len(df_normalizado)}")
print(f"Colunas originais: {len(df_original.columns)}")
print(f"Colunas normalizadas: {len(df_normalizado.columns)}")

assert len(df_original) == len(df_normalizado), "Quantidade de registros diferente!"
assert list(df_original.columns) == list(df_normalizado.columns), "Colunas diferentes!"

assert not (df_normalizado["nome_feira"] == "MAESTRO JOÞO EVANGELISTA").any()
assert not (df_normalizado["bairro"] == "SÞO MIGUEL").any()

assert (df_normalizado["nome_feira"] == "MAESTRO JOÃO EVANGELISTA").sum() == 1
assert (df_normalizado["bairro"] == "SÃO MIGUEL").sum() == 1

assert len(df_correcoes) == 2

print("\nTodas as verificações foram aprovadas.")
print("A base normalizada preservou a estrutura original.")
print("As duas correções foram confirmadas.")
print("\n===== FIM DA VALIDAÇÃO =====")
