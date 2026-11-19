import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARQUIVO_ORIGINAL = (
    ROOT / "data" / "raw" /
    "prefeitura_sp_feiras_livres.csv"
)

ARQUIVO_NORMALIZADO = (
    ROOT / "data" / "processed" /
    "prefeitura_sp_feiras_livres_normalizado.csv"
)

ARQUIVO_CORRECOES = (
    ROOT / "data" / "processed" /
    "prefeitura_sp_feiras_livres_correcoes.csv"
)

# Correções identificadas na auditoria textual
CORRECOES = {
    ("nome_feira", "MAESTRO JOÞO EVANGELISTA"):
        "MAESTRO JOÃO EVANGELISTA",

    ("bairro", "SÞO MIGUEL"):
        "SÃO MIGUEL"
}

# Leitura da base original
df = pd.read_csv(
    ARQUIVO_ORIGINAL,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

correcoes_aplicadas = []

# Verifica e aplica cada correção
for (coluna, valor_original), valor_novo in CORRECOES.items():

    if coluna not in df.columns:
        raise ValueError(f"Coluna não encontrada: {coluna}")

    mascara = df[coluna] == valor_original
    quantidade = int(mascara.sum())

    if quantidade != 1:
        raise ValueError(
            f"Esperado 1 registro para '{valor_original}', "
            f"mas foram encontrados {quantidade}. "
            "Nenhuma correção deve ser aplicada sem revisão."
        )

    indice = df.index[mascara][0]

    correcoes_aplicadas.append({
        "linha_csv": indice + 2,
        "coluna": coluna,
        "valor_original": valor_original,
        "valor_normalizado": valor_novo
    })

    df.loc[mascara, coluna] = valor_novo

# Cria a pasta de destino, caso necessário
ARQUIVO_NORMALIZADO.parent.mkdir(
    parents=True,
    exist_ok=True
)

# Salva a base normalizada
df.to_csv(
    ARQUIVO_NORMALIZADO,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# Salva o histórico de correções
pd.DataFrame(correcoes_aplicadas).to_csv(
    ARQUIVO_CORRECOES,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\n===== NORMALIZAÇÃO CONCLUÍDA =====")
print(f"Registros preservados: {len(df)}")
print(f"Correções aplicadas: {len(correcoes_aplicadas)}")

for correcao in correcoes_aplicadas:
    print(
        f"{correcao['coluna']}: "
        f"{correcao['valor_original']} -> "
        f"{correcao['valor_normalizado']}"
    )

print(f"\nBase normalizada: {ARQUIVO_NORMALIZADO}")
print(f"Histórico de correções: {ARQUIVO_CORRECOES}")
print("\n===== FIM =====")
