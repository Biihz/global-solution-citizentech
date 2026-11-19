from pathlib import Path
import pandas as pd

# Diretório raiz do projeto
RAIZ = Path(__file__).resolve().parent.parent

# Arquivos de entrada
ARQUIVO_BRANCOLI = (
    RAIZ / "data" / "processed" /
    "brancoli_2022_base_integrada.csv"
)

ARQUIVO_CORRESPONDENCIAS = (
    RAIZ / "data" / "processed" /
    "correspondencias_brancoli_prefeitura.csv"
)

# Arquivo de saída
ARQUIVO_SAIDA = (
    RAIZ / "data" / "processed" /
    "brancoli_2022_base_com_prefeitura.csv"
)


def main():
    # Leitura das bases
    brancoli = pd.read_csv(
        ARQUIVO_BRANCOLI,
        encoding="utf-8-sig"
    )

    correspondencias = pd.read_csv(
        ARQUIVO_CORRESPONDENCIAS,
        sep=";",
        encoding="utf-8-sig",
        dtype=str
    )

    print("=== BASES DE ENTRADA ===")
    print(f"Brancoli: {len(brancoli)} registros")
    print(f"Correspondências: {len(correspondencias)} registros")

    # Verificar existência da chave de integração
    if "market_id" not in brancoli.columns:
        raise ValueError("Coluna market_id ausente na base Brancoli.")

    if "market_id" not in correspondencias.columns:
        raise ValueError("Coluna market_id ausente nas correspondências.")

    # Verificar duplicidades nas chaves da tabela de correspondências
    if correspondencias["market_id"].duplicated().any():
        raise ValueError(
            "Existem market_id duplicados na tabela de correspondências."
        )

    # Verificar se todas as feiras do estudo possuem correspondência
    ids_brancoli = set(brancoli["market_id"].dropna())
    ids_correspondencias = set(correspondencias["market_id"].dropna())

    ids_sem_correspondencia = ids_brancoli - ids_correspondencias

    if ids_sem_correspondencia:
        raise ValueError(
            "Feiras sem correspondência: "
            f"{sorted(ids_sem_correspondencia)}"
        )

    # Selecionar os campos municipais que serão acrescentados
    colunas_municipais = [
        "market_id",
        "nome_feira_municipal",
        "dia_feira_municipal",
        "subprefeitura",
        "bairro_municipal",
        "tipo_logradouro",
        "logradouro",
        "status_correspondencia",
    ]

    correspondencias = correspondencias[colunas_municipais]

    # Integração: muitos registros Brancoli para uma feira municipal
    base_integrada = brancoli.merge(
        correspondencias,
        on="market_id",
        how="left",
        validate="many_to_one",
        indicator=True
    )

    # Validar o resultado da integração
    if len(base_integrada) != len(brancoli):
        raise ValueError(
            "A quantidade de registros mudou após a integração."
        )

    if (base_integrada["_merge"] != "both").any():
        raise ValueError(
            "Existem registros Brancoli sem correspondência municipal."
        )

    base_integrada = base_integrada.drop(columns=["_merge"])

    # Salvar resultado
    base_integrada.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n=== INTEGRAÇÃO CONCLUÍDA ===")
    print(f"Registros finais: {len(base_integrada)}")
    print(f"Colunas finais: {len(base_integrada.columns)}")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")

    print("\nRegistros por feira:")
    print(
        base_integrada["market_id"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nColunas da base final:")
    print(base_integrada.columns.tolist())


if __name__ == "__main__":
    main()
