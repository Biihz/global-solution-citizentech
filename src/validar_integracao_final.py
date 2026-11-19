
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent

ARQUIVO_ORIGINAL = (
    RAIZ / "data" / "processed" /
    "brancoli_2022_base_integrada.csv"
)

ARQUIVO_INTEGRADO = (
    RAIZ / "data" / "processed" /
    "brancoli_2022_base_com_prefeitura.csv"
)

COLUNAS_ORIGINAIS = [
    "market_id", "name", "weekday", "district", "idh",
    "number_of_stalls", "category_level_I",
    "category_level_II", "kg_per_stall", "classification",
    "source_table", "source_page",
]

COLUNAS_MUNICIPAIS = [
    "nome_feira_municipal", "dia_feira_municipal",
    "subprefeitura", "bairro_municipal",
    "tipo_logradouro", "logradouro", "status_correspondencia",
]

DISTRIBUICAO_ESPERADA = {
    "SM1": 26,
    "SM2": 26,
    "SM3": 26,
    "SM4": 26,
}


def carregar_bases():
    """Carrega as bases original e integrada."""
    original = pd.read_csv(ARQUIVO_ORIGINAL, encoding="utf-8-sig")
    integrado = pd.read_csv(ARQUIVO_INTEGRADO, encoding="utf-8-sig")
    return original, integrado


def validar_quantidade(original, integrado):
    """Valida registros e colunas."""
    erros = []

    if len(original) == len(integrado) == 104:
        print("[OK] 104 registros preservados.")
    else:
        erros.append("Quantidade de registros incorreta.")

    if len(integrado.columns) == 19:
        print("[OK] 19 colunas na base integrada.")
    else:
        erros.append("Quantidade de colunas diferente de 19.")

    return erros


def validar_colunas(integrado):
    """Verifica a presença das colunas originais e municipais."""
    erros = []

    if all(coluna in integrado.columns for coluna in COLUNAS_ORIGINAIS):
        print("[OK] Todas as 12 colunas originais foram preservadas.")
    else:
        erros.append("Existem colunas originais ausentes.")

    if all(coluna in integrado.columns for coluna in COLUNAS_MUNICIPAIS):
        print("[OK] Todas as 7 colunas municipais foram adicionadas.")
    else:
        erros.append("Existem colunas municipais ausentes.")

    return erros


def validar_distribuicao(integrado):
    """Verifica a quantidade de registros por feira."""
    distribuicao = integrado["market_id"].value_counts().sort_index()

    if distribuicao.to_dict() == DISTRIBUICAO_ESPERADA:
        print("[OK] Cada feira possui exatamente 26 registros.")
        return [], distribuicao

    return ["Distribuição de registros por feira incorreta."], distribuicao


def validar_valores_municipais(integrado):
    """Verifica valores ausentes nas colunas municipais."""
    if not integrado[COLUNAS_MUNICIPAIS].isna().any().any():
        print("[OK] Nenhum valor municipal ausente.")
        return []

    return ["Existem valores municipais ausentes."]


def validar_dados_originais(original, integrado):
    """Compara os dados originais com os dados da base integrada."""
    original = original[COLUNAS_ORIGINAIS].reset_index(drop=True)
    integrado = integrado[COLUNAS_ORIGINAIS].reset_index(drop=True)

    if original.equals(integrado):
        print("[OK] Dados originais preservados integralmente.")
        return []

    return ["Os dados originais foram alterados."]


def validar_status(integrado):
    """Verifica o status das correspondências."""
    status = integrado["status_correspondencia"].unique()

    if len(status) == 1 and status[0] == "exploratoria_consistente":
        print("[OK] Status das correspondências preservado.")
        return []

    return ["Status das correspondências inconsistente."]


def exibir_resultado(erros, distribuicao):
    """Apresenta o resultado final da validação."""
    print("\n=== RESULTADO FINAL ===")

    if erros:
        print("VALIDAÇÃO COM PENDÊNCIAS:")
        for erro in erros:
            print(f"- {erro}")
    else:
        print("TODAS AS VALIDAÇÕES FORAM APROVADAS!")

    print("\nDistribuição por feira:")
    print(distribuicao.to_string())


def main():
    """Executa todas as etapas de validação da integração."""
    original, integrado = carregar_bases()

    print("=== VALIDAÇÃO DA INTEGRAÇÃO FINAL ===")

    erros = []
    erros.extend(validar_quantidade(original, integrado))
    erros.extend(validar_colunas(integrado))

    erros_distribuicao, distribuicao = validar_distribuicao(integrado)
    erros.extend(erros_distribuicao)

    erros.extend(validar_valores_municipais(integrado))
    erros.extend(validar_dados_originais(original, integrado))
    erros.extend(validar_status(integrado))

    exibir_resultado(erros, distribuicao)


if __name__ == "__main__":
    main()