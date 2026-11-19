from pathlib import Path
import pandas as pd
import unicodedata

# Caminhos do projeto
RAIZ = Path(__file__).resolve().parent.parent

ARQUIVO_FEIRAS = (
    RAIZ / "data" / "processed" /
    "prefeitura_sp_feiras_livres_normalizado.csv"
)

ARQUIVO_SAIDA = (
    RAIZ / "data" / "processed" /
    "correspondencias_brancoli_prefeitura.csv"
)


def normalizar(texto):
    """Padroniza texto para comparação, ignorando acentos e caixa."""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(
        caractere for caractere in texto
        if not unicodedata.combining(caractere)
    )


# Correspondências identificadas na investigação
correspondencias = [
    {
        "market_id": "SM1",
        "nome_estudo": "Parque da Mooca",
        "dia_estudo": "terça-feira",
        "bairro_estudo": "Parque da Mooca",
        "nome_municipal": "PARQUE DA MOOCA",
        "dia_busca": "TER",
        "bairro_busca": "PQ DA MOOCA",
    },
    {
        "market_id": "SM2",
        "nome_estudo": "Sumaré Moderna",
        "dia_estudo": "terça-feira",
        "bairro_estudo": "Pacaembú",
        "nome_municipal": "SUMARE MODERNA",
        "dia_busca": "TER",
        "bairro_busca": "PACAEMBU",
    },
    {
        "market_id": "SM3",
        "nome_estudo": "Baturité",
        "dia_estudo": "quarta-feira",
        "bairro_estudo": "Aclimação",
        "nome_municipal": "BATURITE",
        "dia_busca": "QUA",
        "bairro_busca": "ACLIMACAO",
    },
    {
        "market_id": "SM4",
        "nome_estudo": "Belém",
        "dia_estudo": "quinta-feira",
        "bairro_estudo": "Belenzinho",
        "nome_municipal": "BELEM",
        "dia_busca": "QUI",
        "bairro_busca": "BELENZINHO",
    },
]


def main():
    feiras = pd.read_csv(
        ARQUIVO_FEIRAS,
        sep=";",
        encoding="utf-8-sig",
        dtype=str
    ).fillna("")

    # Colunas auxiliares para comparação
    for coluna in ["nome_feira", "dia_feira", "bairro"]:
        feiras[f"_{coluna}_normalizado"] = (
            feiras[coluna].apply(normalizar)
        )

    registros = []

    for item in correspondencias:
        nome = normalizar(item["nome_municipal"])
        dia = normalizar(item["dia_busca"])
        bairro = normalizar(item["bairro_busca"])

        resultado = feiras[
            (feiras["_nome_feira_normalizado"] == nome)
            & (feiras["_dia_feira_normalizado"].str.startswith(dia))
            & (feiras["_bairro_normalizado"] == bairro)
        ]

        if len(resultado) != 1:
            raise ValueError(
                f'{item["market_id"]}: esperado 1 registro, '
                f'encontrados {len(resultado)}. '
                "Verifique os critérios antes de continuar."
            )

        feira = resultado.iloc[0]

        registros.append({
            "market_id": item["market_id"],
            "nome_estudo": item["nome_estudo"],
            "dia_estudo": item["dia_estudo"],
            "bairro_estudo": item["bairro_estudo"],
            "nome_feira_municipal": feira["nome_feira"],
            "dia_feira_municipal": feira["dia_feira"],
            "subprefeitura": feira["subprefeitura"],
            "bairro_municipal": feira["bairro"],
            "tipo_logradouro": feira["tipo_logradouro"],
            "logradouro": feira["logradouro"],
            "status_correspondencia": "exploratoria_consistente",
        })

    base = pd.DataFrame(registros)

    base.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    print("Correspondências geradas com sucesso!")
    print(f"Registros: {len(base)}")
    print(f"Arquivo: {ARQUIVO_SAIDA}")

    print("\nFeiras relacionadas:")
    print(
        base[
            ["market_id", "nome_feira_municipal", "logradouro"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
