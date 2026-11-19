import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARQUIVO = (
    ROOT
    / "data"
    / "raw"
    / "prefeitura_sp_feiras_livres.csv"
)

COLUNAS_ESPERADAS = [
    "subprefeitura",
    "dia_feira",
    "categoria",
    "quantidade_feirantes",
    "nome_feira",
    "tipo_logradouro",
    "logradouro",
    "bairro",
    "pagina_pdf"
]

print("\n===== VALIDAÇÃO DAS FEIRAS DA PREFEITURA =====")

# 1. Verificar arquivo
if not ARQUIVO.exists():
    print("ERRO: arquivo CSV não encontrado.")
    raise SystemExit

# 2. Carregar dados
df = pd.read_csv(
    ARQUIVO,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

print("\n1. Estrutura:")
print("Colunas encontradas:", df.columns.tolist())
print("Total de registros:", len(df))

# 3. Verificar colunas
colunas_ausentes = [
    coluna for coluna in COLUNAS_ESPERADAS
    if coluna not in df.columns
]

print("\n2. Colunas ausentes:")
print(colunas_ausentes if colunas_ausentes else "Nenhuma")

if colunas_ausentes:
    print("\nERRO: estrutura diferente da esperada.")
    raise SystemExit

# 4. Limpar espaços externos
for coluna in COLUNAS_ESPERADAS:
    df[coluna] = df[coluna].str.strip()

# 5. Verificar campos vazios
print("\n3. Campos vazios:")
print(
    df[COLUNAS_ESPERADAS]
    .replace("", pd.NA)
    .isnull()
    .sum()
)

# 6. Verificar duplicidade de linhas
print("\n4. Linhas completamente duplicadas:")
print(df.duplicated(subset=COLUNAS_ESPERADAS[:-1]).sum())

# 7. Verificar possíveis feiras duplicadas
chave = [
    "subprefeitura",
    "dia_feira",
    "categoria",
    "nome_feira",
    "logradouro",
    "bairro"
]

duplicadas = df[df.duplicated(subset=chave, keep=False)]

print("\n5. Possíveis feiras duplicadas:")
print(len(duplicadas))

if not duplicadas.empty:
    print(duplicadas[chave].to_string(index=False))

# 8. Verificar quantidade de feirantes
df["quantidade_feirantes_num"] = pd.to_numeric(
    df["quantidade_feirantes"],
    errors="coerce"
)

print("\n6. Quantidade de feirantes:")
print(
    "Valores não numéricos:",
    df["quantidade_feirantes_num"].isna().sum()
)

print(
    "Valores negativos:",
    (df["quantidade_feirantes_num"] < 0).sum()
)

print(
    "Valores iguais a zero:",
    (df["quantidade_feirantes_num"] == 0).sum()
)

# 9. Verificar páginas do PDF
df["pagina_pdf_num"] = pd.to_numeric(
    df["pagina_pdf"],
    errors="coerce"
)

print("\n7. Páginas do PDF:")
print(
    "Páginas inválidas:",
    df["pagina_pdf_num"].isna().sum()
)

print(
    "Páginas fora do intervalo 1-25:",
    (
        (df["pagina_pdf_num"] < 1)
        | (df["pagina_pdf_num"] > 25)
    ).sum()
)

# 10. Conferir feira adicionada manualmente
feira_organica = df[
    df["nome_feira"].str.contains(
        "FEIRA LIVRE ORGANICA WHITAKER",
        case=False,
        na=False
    )
]

print("\n8. Feira orgânica recuperada manualmente:")

if feira_organica.empty:
    print("NÃO ENCONTRADA")
else:
    print(feira_organica[COLUNAS_ESPERADAS].to_string(index=False))

# 11. Quantidade de subprefeituras
print("\n9. Subprefeituras identificadas:")
print(df["subprefeitura"].nunique())

print("\n10. Feiras com zero feirantes:")

feiras_zero = df[
    df["quantidade_feirantes_num"] == 0
]

print(
    feiras_zero[COLUNAS_ESPERADAS]
    .to_string(index=False)
)

# 12. Resumo
print("\n===== RESUMO =====")
print(f"Registros encontrados: {len(df)}")
print("Registros esperados: 933")
print(f"Subprefeituras: {df['subprefeitura'].nunique()}")
print(f"Possíveis duplicidades: {len(duplicadas)}")

print("\n===== FIM DA VALIDAÇÃO =====")
