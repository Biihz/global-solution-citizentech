import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARQUIVOS = {
    "Brancoli": {
        "caminho": ROOT / "data/processed/brancoli_2022_base_integrada.csv",
        "separador": ","
    },
    "Prefeitura": {
        "caminho": ROOT / "data/processed/prefeitura_sp_feiras_livres_normalizado.csv",
        "separador": ";"
    }
}

for nome, config in ARQUIVOS.items():

    caminho = config["caminho"]

    print(f"\n{'=' * 60}")
    print(f"BASE: {nome.upper()}")
    print(f"{'=' * 60}")

    if not caminho.exists():
        print(f"Arquivo não encontrado: {caminho}")
        continue

    df = pd.read_csv(
        caminho,
        sep=config["separador"],
        encoding="utf-8-sig"
    )

    print(f"\nQuantidade de registros: {len(df)}")
    print(f"Quantidade de colunas: {len(df.columns)}")

    print("\nColunas:")
    for coluna in df.columns:
        print(f"- {coluna}")

    print("\nTipos de dados:")
    print(df.dtypes.to_string())

    print("\nPrimeiros 5 registros:")
    print(df.head().to_string(index=False))

print("\n===== INSPEÇÃO FINALIZADA =====")
