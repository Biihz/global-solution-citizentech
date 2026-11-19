import pandas as pd
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[1]

ARQUIVO = (
    ROOT / "data" / "processed" /
    "prefeitura_sp_feiras_livres_normalizado.csv"
)

df = pd.read_csv(
    ARQUIVO,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

def normalizar(texto):
    texto = str(texto).upper().strip()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return " ".join(texto.split())

mercados = [
    {
        "nome": "Parque da Mooca",
        "distrito": "Parque da Mooca"
    },
    {
        "nome": "Sumaré Moderna",
        "distrito": "Pacaembú"
    },
    {
        "nome": "Baturité",
        "distrito": "Aclimação"
    },
    {
        "nome": "Belém",
        "distrito": "Belenzinho"
    }
]

print("\n===== INVESTIGAÇÃO DE CORRESPONDÊNCIAS =====")

for mercado in mercados:

    nome = normalizar(mercado["nome"])
    distrito = normalizar(mercado["distrito"])

    print(f"\n{'=' * 55}")
    print(f"MERCADO: {mercado['nome']}")
    print(f"DISTRITO: {mercado['distrito']}")
    print("=" * 55)

    nome_feira = df["nome_feira"].apply(normalizar)
    bairro = df["bairro"].apply(normalizar)
    subprefeitura = df["subprefeitura"].apply(normalizar)

    encontrados = (
        nome_feira.str.contains(nome, regex=False)
        | bairro.str.contains(distrito, regex=False)
        | subprefeitura.str.contains(distrito, regex=False)
    )

    resultado = df.loc[
        encontrados,
        [
            "subprefeitura",
            "dia_feira",
            "nome_feira",
            "logradouro",
            "bairro",
            "pagina_pdf"
        ]
    ]

    if resultado.empty:
        print("Nenhuma correspondência textual encontrada.")
    else:
        print(resultado.to_string(index=False))

print("\n===== INVESTIGAÇÃO FINALIZADA =====")
