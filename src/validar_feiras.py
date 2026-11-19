import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

arquivo = ROOT / "data" / "raw" / "brancoli_2022_feiras.csv"

df = pd.read_csv(arquivo)

print("\n===== VALIDAÇÃO DAS FEIRAS =====")

# 1. Estrutura
print("\n1. Colunas:")
print(df.columns.tolist())

# 2. Quantidade de feiras
print("\n2. Quantidade de registros:")
print(len(df))

# 3. Dados cadastrados
print("\n3. Registros:")
print(df.to_string(index=False))

# 4. Valores ausentes
print("\n4. Valores ausentes:")
print(df.isnull().sum())

# 5. Duplicidades
print("\n5. Market IDs duplicados:")
print(df["market_id"].duplicated().sum())

# 6. Conversão de colunas numéricas
colunas_numericas = [
    "idh",
    "number_of_stalls",
    "total_waste_kg"
]

for coluna in colunas_numericas:
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

print("\n6. Verificação de dados numéricos:")
print(df[colunas_numericas].isnull().sum())

# 7. Comparação com a Tabela 2 do artigo
referencia = {
    "SM1": {"stalls": 4, "waste": 74.2},
    "SM2": {"stalls": 73, "waste": 1523.7},
    "SM3": {"stalls": 40, "waste": 1033.9},
    "SM4": {"stalls": 39, "waste": 1483.5},
}

print("\n7. Comparação com o artigo:")

for _, linha in df.iterrows():
    market = linha["market_id"]
    esperado = referencia.get(market)

    if esperado is None:
        print(f"{market}: feira não encontrada na referência")
        continue

    stalls_ok = linha["number_of_stalls"] == esperado["stalls"]
    waste_ok = linha["total_waste_kg"] == esperado["waste"]

    print(
        f"{market}: "
        f"barracas={'OK' if stalls_ok else 'DIVERGENTE'} | "
        f"resíduos={'OK' if waste_ok else 'DIVERGENTE'}"
    )

# 8. Cálculo derivado de resíduos por barraca
df["waste_per_stall_kg"] = (
    df["total_waste_kg"] / df["number_of_stalls"]
)

print("\n8. Resíduos calculados por barraca:")
print(
    df[["market_id", "waste_per_stall_kg"]]
    .round(2)
    .to_string(index=False)
)

print("\n===== FIM DA VALIDAÇÃO =====")
