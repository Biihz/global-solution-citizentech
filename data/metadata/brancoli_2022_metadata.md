# Metadados — Brancoli et al. (2022)

## 1. Identificação da fonte

- **Título:** *Compositional Analysis of Street Market Food Waste in Brazil*.
- **Autores:** Brancoli et al.
- **Ano:** 2022.
- **Periódico:** *Sustainability*, volume 14, número 12, artigo 7014.
- **DOI:** https://doi.org/10.3390/su14127014
- **Local do estudo:** município de São Paulo, Brasil.

## 2. Caracterização do estudo

- Período de coleta: uma semana de dezembro de 2021.
- Feiras analisadas: quatro.
- Massa total de resíduos coletados e separados: aproximadamente 4,1 toneladas.
- O artigo descreve 27 frações no nível II.
- A transcrição utilizada da Tabela 3 contém 104 registros, distribuídos em 26 linhas por feira.

A diferença entre as 27 frações descritas no artigo e as 26 linhas transcritas por feira permanece documentada. Não foi criada uma categoria adicional sem evidência na tabela publicada.

## 3. Metodologia original

O estudo realizou análise gravimétrica: coleta dos resíduos ao final do funcionamento das feiras, pesagem e separação manual em categorias. A publicação apresenta massas por categoria e valores por barraca. As categorias incluem resíduos alimentares, embalagens e resíduos externos.

## 4. Arquivos derivados da publicação

### `brancoli_2022_transcricao.csv`

Transcrição da Tabela 3:
- 104 registros;
- quatro feiras;
- valores em kg por barraca;
- categorias de resíduos e classificações descritas na publicação.

### `brancoli_2022_feiras.csv`

Transcrição da Tabela 2:
- quatro registros;
- identificação das feiras, dia, distrito, IDH informado no artigo, número de barracas e massa total coletada.

### `brancoli_2022_base_integrada.csv`

Base derivada que reúne os dados transcritos das tabelas publicadas. Deve ser tratada como estrutura de análise, não como uma nova coleta.

### `brancoli_2022_base_com_prefeitura.csv`

Base integrada exploratoriamente com campos cadastrais municipais. A integração não transforma os dados da Prefeitura em medições do estudo de Brancoli. As correspondências permanecem exploratórias e estão documentadas em `correspondencias_brancoli_prefeitura.md` e `correspondencias_brancoli_prefeitura.csv`.

## 5. Classificação dos dados e unidades

- **Observados publicados/transcritos:** valores apresentados nas Tabelas 2 e 3 do artigo.
- **Derivados:** indicadores calculados a partir dos valores publicados, como ponderações e comparações entre feiras.
- **Simulados:** não há dados simulados nos arquivos de transcrição descritos aqui.

Unidades:
- `total_waste_kg`: quilogramas de resíduos coletados;
- `number_of_stalls`: quantidade de barracas;
- `kg_per_stall`: quilogramas por barraca.

`kg_per_stall` não representa excedente comercial não vendido, estoque disponível para doação nem previsão de desperdício futuro.

## 6. Limitações

- Somente quatro feiras foram analisadas.
- A coleta ocorreu durante uma única semana de dezembro de 2021.
- Os resultados não representam automaticamente todas as feiras do município.
- A publicação não fornece uma série histórica.
- Os dados brutos originais dos pesquisadores não estão disponíveis no conjunto utilizado; os CSVs são transcrições de tabelas publicadas.
- A classificação de alimento evitável não significa que todo o material ainda estivesse próprio para consumo ou doação.
- A transcrição de tabelas publicadas pode carregar arredondamentos e limitações de leitura; os valores devem ser interpretados conforme a unidade e o escopo de cada tabela.

## 7. Reconciliação dos valores de geração por barraca

A comparação entre as Tabelas 2 e 3 e a seção 3.1 do artigo foi revisada considerando o tratamento dos resíduos externos.

A divisão da massa total coletada na Tabela 2 pelo número de barracas produz aproximadamente:

- SM1: 18,55 kg/barraca;
- SM2: 20,87 kg/barraca;
- SM3: 25,85 kg/barraca;
- SM4: 38,04 kg/barraca.

Esses valores incluem a fração classificada como resíduos externos.

Ao subtrair os respectivos valores de resíduos externos transcritos da Tabela 3, obtêm-se:

- SM1: 16,99 kg/barraca;
- SM2: 20,30 kg/barraca;
- SM3: 23,11 kg/barraca;
- SM4: 34,55 kg/barraca.

Os resultados correspondem, por arredondamento, à faixa de 17 a 34,6 kg/barraca informada na seção 3.1 do artigo.

A diferença decorre do escopo de contabilização: os valores totais da Tabela 2 incluem resíduos externos, enquanto a faixa apresentada na discussão considera os resíduos sem essa fração. Os valores originais transcritos foram preservados.

## 8. Indicadores derivados utilizados na análise

A partir da base com número de barracas e valores em kg por barraca, foi calculado um volume derivado pela multiplicação:

`volume_derivado_kg = kg_per_stall × number_of_stalls`

No conjunto de quatro feiras, essa operação resulta em aproximadamente:
- volume derivado total: 4.116,04 kg;
- desperdício evitável derivado: 1.339,37 kg;
- resíduos externos derivados: 293,56 kg;
- embalagens derivadas: 597,82 kg;
- desperdício inevitável derivado: 1.885,29 kg.

> [!IMPORTANT]
> Esses valores são **cálculos derivados das tabelas transcritas**, não novas pesagens. A proporção de desperdício evitável de aproximadamente 35,04% utiliza como denominador o volume derivado total sem a classificação de resíduos externos. Não se deve interpretar esse percentual como proporção de alimentos seguros para doação.

A soma dos valores derivados pode diferir ligeiramente da massa total publicada na Tabela 2 devido a arredondamentos e ao escopo das categorias.

## 9. Rastreabilidade

- Tabela 2: página 6 do PDF.
- Metodologia: páginas 6 e 7.
- Tabela 3: página 8.
- Resultados e discussão: seção 3.1.
- Arquivo de referência: `sustainability-14-07014.pdf`.
- Data de transcrição registrada: 09/11/2026.
