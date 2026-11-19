from pathlib import Path
import pdfplumber
import csv

# Caminhos dos arquivos
PDF = Path("data/raw/prefeitura_sp_feiras_livres_enderecos.pdf")
CSV = Path("data/raw/prefeitura_sp_feiras_livres.csv")
REVISAO = Path("data/raw/prefeitura_sp_feiras_livres_revisar.csv")

# Dias encontrados no documento
DIAS = {
    "DOM", "SEG", "TER", "QUA", "QUI", "SEX",
    "SAB", "SÁB"
}

COLUNAS = [
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

registros = []
revisar = []
subprefeitura_atual = None

with pdfplumber.open(PDF) as pdf:
    total_paginas = len(pdf.pages)

    for numero_pagina, pagina in enumerate(pdf.pages, start=1):

        tabelas = pagina.extract_tables()

        for tabela in tabelas:

            for linha in tabela:

                # Limpa espaços e células vazias
                celulas = [
                    str(valor).strip() if valor else ""
                    for valor in linha
                ]

                if not any(celulas):
                    continue

                # Identifica o título da subprefeitura
                valores_preenchidos = [
                    valor for valor in celulas if valor
                ]

                if len(valores_preenchidos) == 1:
                    texto = valores_preenchidos[0]

                    if texto.upper() not in {
                        "DIA DA FEIRA", "CATEGORIA"
                    }:
                        subprefeitura_atual = texto

                    continue

                # Ignora cabeçalhos das tabelas
                if celulas[0].upper() == "DIA DA FEIRA":
                    continue

                # Identifica linhas de feiras
                if (
                    len(celulas) >= 7
                    and celulas[0].upper() in DIAS
                    and celulas[2].isdigit()
                    and subprefeitura_atual
                ):
                    registros.append({
                        "subprefeitura": subprefeitura_atual,
                        "dia_feira": celulas[0],
                        "categoria": celulas[1],
                        "quantidade_feirantes": celulas[2],
                        "nome_feira": celulas[3],
                        "tipo_logradouro": celulas[4],
                        "logradouro": celulas[5],
                        "bairro": celulas[6],
                        "pagina_pdf": numero_pagina
                    })

                else:
                    revisar.append({
                        "pagina_pdf": numero_pagina,
                        "linha_extraida": " | ".join(celulas)
                    })


# Exporta os registros encontrados
with CSV.open("w", newline="", encoding="utf-8-sig") as arquivo:
    escritor = csv.DictWriter(
        arquivo,
        fieldnames=COLUNAS,
        delimiter=";"
    )
    escritor.writeheader()
    escritor.writerows(registros)


# Exporta linhas que precisam de conferência
with REVISAO.open("w", newline="", encoding="utf-8-sig") as arquivo:
    escritor = csv.DictWriter(
        arquivo,
        fieldnames=["pagina_pdf", "linha_extraida"],
        delimiter=";"
    )
    escritor.writeheader()
    escritor.writerows(revisar)


# Relatório
print("\n===== EXTRAÇÃO CONCLUÍDA =====")
print(f"Páginas processadas: {total_paginas}")
print(f"Feiras extraídas: {len(registros)}")
print(
    "Subprefeituras identificadas:",
    len({r["subprefeitura"] for r in registros})
)
print(f"Linhas para revisão: {len(revisar)}")
print(f"\nCSV gerado: {CSV}")
print(f"Arquivo de revisão: {REVISAO}")
