import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARQUIVO = (
    ROOT / "data" / "raw" /
    "prefeitura_sp_feiras_livres.csv"
)

SAIDA = (
    ROOT / "data" / "processed" /
    "prefeitura_sp_valores_unicos_auditoria.csv"
)

COLUNAS_TEXTO = [
    "subprefeitura",
    "dia_feira",
    "categoria",
    "nome_feira",
    "tipo_logradouro",
    "logradouro",
    "bairro"
]

df = pd.read_csv(
    ARQUIVO,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

relatorio = []

for coluna in COLUNAS_TEXTO:

    frequencias = (
        df[coluna]
        .fillna("")
        .value_counts()
    )

    for valor, quantidade in frequencias.items():

        relatorio.append({
            "coluna": coluna,
            "valor": valor,
            "frequencia": quantidade
        })

auditoria = pd.DataFrame(relatorio)

# Identifica caracteres fora do conjunto esperado
padrao = r"[^A-ZÀ-Ü0-9 /.,'()\-]"

auditoria["possivel_anomalia"] = (
    ~auditoria["valor"].str.upper().str.fullmatch(
        r"[A-ZÀ-Ü0-9 /.,'()\-]*"
    )
)

SAIDA.parent.mkdir(parents=True, exist_ok=True)

auditoria.to_csv(
    SAIDA,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\n===== AUDITORIA TEXTUAL =====")
print(f"Registros analisados: {len(df)}")
print(f"Valores distintos analisados: {len(auditoria)}")
print(
    "Valores com caracteres suspeitos:",
    auditoria["possivel_anomalia"].sum()
)

print(f"\nRelatório gerado: {SAIDA}")
print("\n===== FIM DA AUDITORIA =====")
