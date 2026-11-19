import pandas as pd
from pathlib import Path

# Caminho principal do projeto
ROOT = Path(__file__).resolve().parents[1]

# Arquivos originais
arquivo_residuos = ROOT / "data" / "raw" / "brancoli_2022_transcricao.csv"
arquivo_feiras = ROOT / "data" / "raw" / "brancoli_2022_feiras.csv"

# Pasta de saída
pasta_saida = ROOT / "data" / "processed"
pasta_saida.mkdir(parents=True, exist_ok=True)

# Leitura dos CSVs
residuos = pd.read_csv(arquivo_residuos)
feiras = pd.read_csv(arquivo_feiras)

print("===== INTEGRAÇÃO BRANCOLI 2022 =====")

print("\n1. Dados carregados:")
print(f"Composição dos resíduos: {len(residuos)} registros")
print(f"Características das feiras: {len(feiras)} registros")

# Verifica se todas as feiras da composição existem na tabela de feiras
feiras_sem_cadastro = (
    set(residuos["market_id"]) - set(feiras["market_id"])
)

if feiras_sem_cadastro:
    raise ValueError(
        f"Feiras sem cadastro: {feiras_sem_cadastro}"
    )

# Integração pelo identificador da feira
base_integrada = residuos.merge(
    feiras,
    on="market_id",
    how="left",
    validate="many_to_one",
    indicator=True
)

# Verifica se todos os registros encontraram correspondência
if not (base_integrada["_merge"] == "both").all():
    raise ValueError("Existem registros sem correspondência.")

base_integrada.drop(columns="_merge", inplace=True)

# Organização das colunas
colunas = [
    "market_id",
    "name",
    "weekday",
    "district",
    "idh",
    "number_of_stalls",
    "category_level_I",
    "category_level_II",
    "kg_per_stall",
    "classification",
    "source_table",
    "source_page",
]

base_integrada = base_integrada[colunas]

# Exportação sem modificar os arquivos originais
saida = pasta_saida / "brancoli_2022_base_integrada.csv"

base_integrada.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)

# Resumo
print("\n2. Resultado da integração:")
print(f"Total de registros: {len(base_integrada)}")
print(f"Feiras integradas: {base_integrada['market_id'].nunique()}")

print("\n3. Registros por feira:")
print(base_integrada["market_id"].value_counts().sort_index())

print("\n4. Valores ausentes:")
print(base_integrada.isnull().sum())

print("\n5. Arquivo gerado:")
print(saida)

print("\n===== INTEGRAÇÃO CONCLUÍDA =====")
