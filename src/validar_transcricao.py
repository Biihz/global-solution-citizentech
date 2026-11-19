import pandas as pd
from pathlib import Path

# Localiza o CSV na pasta data/raw
ROOT = Path(__file__).resolve().parents[1]
arquivo = ROOT / "data" / "raw" / "brancoli_2022_transcricao.csv"

# Lê os dados
df = pd.read_csv(arquivo)

print("\n===== VALIDAÇÃO BRANCOLI 2022 =====")

# 1. Estrutura
print("\n1. Colunas:")
print(df.columns.tolist())

# 2. Quantidade de registros
print("\n2. Quantidade de registros:")
print(len(df))

# 3. Valores ausentes
print("\n3. Valores ausentes:")
print(df.isnull().sum())

# 4. Feiras encontradas
print("\n4. Feiras:")
print(df["market_id"].value_counts().sort_index())

# 5. Categorias
print("\n5. Categorias de nível I:")
print(df["category_level_I"].value_counts())

print("\n6. Classificações:")
print(df["classification"].value_counts())

# 7. Valores numéricos
print("\n7. Valores inválidos ou negativos:")
print(df[pd.to_numeric(df["kg_per_stall"], errors="coerce").isna()])

df["kg_per_stall"] = pd.to_numeric(df["kg_per_stall"])

print("\nRegistros com valores negativos:")
print(df[df["kg_per_stall"] < 0])

# 8. Duplicidades
print("\n8. Registros duplicados:")
print(df.duplicated(
    subset=["market_id", "category_level_I", "category_level_II"]
).sum())

# 9. Total por feira
print("\n9. Total transcrito por feira (kg/barraca):")
print(
    df.groupby("market_id")["kg_per_stall"]
    .sum()
    .round(2)
)

print("\n===== FIM DA VALIDAÇÃO =====")