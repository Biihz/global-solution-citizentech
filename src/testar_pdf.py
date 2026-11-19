from pathlib import Path
import pdfplumber

# Caminho do PDF
arquivo = Path("data/raw/prefeitura_sp_feiras_livres_enderecos.pdf")

# Verifica se o arquivo existe
if not arquivo.exists():
    print("ERRO: PDF não encontrado.")
else:
    with pdfplumber.open(arquivo) as pdf:
        print("PDF encontrado com sucesso!")
        print(f"Total de páginas: {len(pdf.pages)}")

        # Testa a extração da primeira página
        primeira_pagina = pdf.pages[0]
        texto = primeira_pagina.extract_text()

        print("\n--- CONTEÚDO DA PRIMEIRA PÁGINA ---")
        print(texto[:2000] if texto else "Nenhum texto encontrado.")
