# Metadados — Preços da CONAB e experimento complementar com INMET

## 1. Identificação das fontes

### CONAB

- **Fonte:** Companhia Nacional de Abastecimento (CONAB).
- **Documento:** Boletim Hortigranjeiro — edição de outubro de 2026.
- **Arquivo de dados de origem:** `tabelas-de-dados-boletim-hortigranjeiro-outubro-2026.xlsx`.
- **Variável principal:** preço médio mensal, em reais por quilograma (R$/kg).
- **Período observado:** setembro de 2024 a setembro de 2026, com 25 referências mensais.

### INMET

- **Fonte:** Instituto Nacional de Meteorologia (INMET).
- **Estação utilizada:** A701 — São Paulo/Mirante de Santana.
- **Arquivos de origem:** pacotes anuais de dados automáticos de 2024, 2025 e 2026.
- **Uso no projeto:** experimento complementar restrito à série de preços da CEAGESP — São Paulo.

## 2. Escopo da base CONAB

A planilha contém abas de preços e quantidades para dez produtos:

- Alface;
- Batata;
- Cebola;
- Cenoura;
- Tomate;
- Banana;
- Laranja;
- Maçã;
- Mamão;
- Melancia.

As séries de preços abrangem doze CEASAs:

1. Ceagesp — São Paulo;
2. CeasaMinas — Belo Horizonte;
3. Ceasa/RJ — Rio de Janeiro;
4. Ceasa/SP — Campinas;
5. Ceasa/ES — Vitória;
6. Ceasa/PR — Curitiba;
7. Ceasa/SC — São José;
8. Ceasa/GO — Goiânia;
9. Ceasa/DF — Brasília;
10. Ceasa/PE — Recife;
11. Ceasa/CE — Fortaleza;
12. Ceasa/AC — Rio Branco.

O painel bruto esperado contém 3.000 combinações (10 produtos × 12 CEASAs × 25 meses), antes da consideração de valores ausentes.

## 3. Estrutura e tratamento da base de preços

A base consolidada possui as colunas:

`produto`, `grupo`, `ceasa`, `uf`, `data_ref`, `ano`, `mes`, `preco`.

A auditoria da base bruta registrou:
- 3.000 linhas;
- 249 preços ausentes;
- 20 preços iguais a zero;
- chave `produto × ceasa × data_ref` verificada para duplicidades.

Para a base principal de modelagem:
- Brasília foi excluída por apresentar 9,2% de cobertura bruta (23 de 250 observações);
- a base resultante contém 2.750 linhas, 11 CEASAs e dez produtos;
- foram identificados dez preços iguais a zero em Goiânia, todos em setembro de 2026, um por produto; esses valores foram tratados como suspeitos e convertidos em ausentes na cópia de modelagem, sem alterar a base consolidada original;
- após esse tratamento, a base de modelagem contém 32 preços ausentes e nenhum zero.

Goiânia apresenta 88% de cobertura útil após o tratamento (220 de 250 registros). Rio Branco apresenta duas lacunas pontuais (99,2% de cobertura bruta). As outras nove CEASAs possuem cobertura integral no painel considerado.

Os valores ausentes não foram imputados nesta etapa. A decisão de excluir Brasília e tratar os zeros suspeitos está documentada no Notebook 03.

**Atenção à contagem de zeros:** os 20 zeros pertencem à auditoria do arquivo consolidado bruto. Os dez zeros de Goiânia são os identificados na cópia de modelagem após a exclusão de Brasília. Não são contagens intercambiáveis.

## 4. Abas de quantidade

As abas de quantidade contêm apenas três referências: setembro de 2025, agosto de 2026 e setembro de 2026. Portanto, não formam uma série mensal contínua e não foram utilizadas como preditores da regressão de preços ao longo dos 25 meses.

Essas informações foram utilizadas apenas como contexto descritivo da participação da CEAGESP nas quantidades reportadas para os produtos e datas disponíveis. Não representam desperdício alimentar nem excedente disponível para doação.

## 5. Modelagem supervisionada principal

- **Unidade de observação:** produto × CEASA × mês.
- **Variável-alvo:** `preco` (R$/kg).
- **Atributos:** defasagens de preço (`lag_1`, `lag_2`, `lag_3`), média móvel histórica de três meses (`media_movel_3m`), sazonalidade cíclica (`mes_sin`, `mes_cos`) e identificadores categóricos de produto e CEASA.
- **Modelos comparados:** Baseline — Lag 1, Ridge Regression e Random Forest Regressor.
- **Separação:** cronológica; treinamento até junho de 2026 e teste final de julho a setembro de 2026. A seleção e a validação dos modelos são realizadas apenas no período de treinamento.
- **Métricas:** MAE, RMSE, MAPE e R².

As variáveis históricas devem ser construídas respeitando a ordem temporal de cada série de produto e CEASA. Médias móveis devem utilizar somente observações anteriores ao mês previsto. O conjunto de teste final não deve participar do ajuste ou da seleção dos modelos.

### 5.1 Resultado do teste final — painel nacional

O CSV `resultados_modelos_conab.csv` registra os seguintes resultados para o recorte geral:

| Modelo | MAE (R$/kg) | RMSE (R$/kg) | MAPE (%) | R² |
|---|---:|---:|---:|---:|
| Ridge | 0,7457 | 1,0605 | 17,6256 | 0,7403 |
| Random Forest | 0,7862 | 1,1107 | 19,0987 | 0,7152 |
| Baseline — Lag 1 | 0,7941 | 1,1764 | 18,9558 | 0,6805 |

Nesse recorte, Ridge apresentou o menor MAE e o maior R² entre os três modelos. A conclusão se refere ao teste final observado e não comprova desempenho futuro ou operacional.

### 5.2 Outros recortes de avaliação

O arquivo de resultados também apresenta recortes com populações de teste diferentes:

- **Nove CEASAs com cobertura integral (`n = 270`):** Ridge — MAE 0,7052; RMSE 0,9984; MAPE 17,3810%; R² 0,7251.
- **CEAGESP — São Paulo (`n = 30`):** Ridge — MAE 0,7194; RMSE 0,9240; MAPE 18,3471%; R² 0,6046.

Os recortes não devem ser comparados como se tivessem a mesma população. O geral inclui observações de teste das CEASAs com dados disponíveis; o segundo restringe-se às nove CEASAs com cobertura integral; o terceiro considera somente a CEAGESP-SP.

### 5.3 Interpretação da validação

Os resultados de validação interna e de teste final não apresentam necessariamente a mesma ordenação dos modelos. A escolha de modelo deve ser fundamentada na validação realizada exclusivamente dentro do treinamento, e o teste final deve ser utilizado como avaliação posterior, sem orientar ajustes retrospectivos.

O Notebook 03 deve explicitar o procedimento de validação efetivamente executado. Não se deve afirmar que foi utilizado `TimeSeriesSplit` ou validação cruzada temporal se essa rotina não estiver implementada no código.

## 6. Experimento complementar CONAB + INMET

O experimento climático utiliza somente os preços da CEAGESP — São Paulo e a estação A701 do INMET. A base inicial possui 250 observações (dez produtos × 25 meses), de setembro de 2024 a setembro de 2026.

As variáveis meteorológicas horárias foram agregadas por mês. Entre os indicadores utilizados estão temperatura média, máxima horária, precipitação acumulada e umidade relativa média, acompanhados de indicadores de cobertura. As variáveis meteorológicas são defasadas em um mês antes de entrar como preditoras.

Foram comparados cenários sem clima e com clima, usando Baseline — Lag 1, Ridge e Random Forest. O teste final contém 30 observações (julho a setembro de 2026; três por produto).

### Resultado do teste final

| Modelo | MAE (R$/kg) | RMSE (R$/kg) | MAPE (%) | R² |
|---|---:|---:|---:|---:|
| Random Forest — Com clima | 0,6412 | 0,8579 | 16,1689 | 0,6591 |
| Random Forest — Sem clima | 0,6579 | 0,8623 | 16,7379 | 0,6557 |
| Ridge — Sem clima | 0,6953 | 0,9120 | 16,8751 | 0,6148 |
| Ridge — Com clima | 0,6986 | 0,9072 | 17,0407 | 0,6188 |
| Baseline — Lag 1 | 0,7748 | 1,0151 | 19,9234 | 0,5228 |

No teste específico, o Random Forest com clima apresentou MAE aproximadamente 2,53% menor que a versão sem clima. A diferença é pequena e não demonstra causalidade nem garante que variáveis climáticas melhorem previsões em outros períodos ou entrepostos. A estação A701 representa a capital paulista, não as regiões produtoras que abastecem a CEAGESP.

## 7. Classificação dos dados

- **Observados/publicados:** preços e quantidades constantes nas planilhas da CONAB; observações meteorológicas do INMET.
- **Derivados:** estatísticas, índices sazonais, atributos defasados, médias móveis, agregações mensais e métricas dos modelos.
- **Previsões:** saídas estimadas pelos modelos. Não devem ser classificadas como observações reais.
- **Simulados:** não são necessários para os resultados de modelagem descritos neste notebook.

## 8. Limitações

- A série de preços tem 25 meses, pouco mais de dois ciclos anuais.
- Brasília foi excluída da modelagem principal por baixa cobertura.
- Goiânia possui lacunas no fim da série após o tratamento dos zeros suspeitos; Rio Branco possui lacunas pontuais.
- As abas de quantidade não formam uma série contínua.
- Preços atacadistas não medem desperdício e não correspondem necessariamente aos preços de venda nas feiras.
- A estação A701 não representa as condições meteorológicas das regiões produtoras.
- O teste final climático contém apenas três meses por produto; as métricas devem ser interpretadas com cautela.
- O notebook não treina um modelo para `excedente_real_kg`. Para isso seriam necessários registros observados de compras, vendas, estoque, sobras, perdas e destinação dos alimentos.
- Os resultados apresentados não comprovam que a previsão de preços possa ser convertida diretamente em previsão de excedentes.

## 9. Arquivos e rastreabilidade

Arquivos utilizados ou esperados na organização final do projeto:

- Planilha original da CONAB: `tabelas-de-dados-boletim-hortigranjeiro-outubro-2026.xlsx`.
- Base consolidada: `data/processed/conab_precos_consolidados.csv`.
- Resultados dos modelos: `data/processed/resultados_modelos_conab.csv`.
- Consolidação meteorológica horária: `data/processed/inmet_sp_horario.csv`.
- Consolidação meteorológica mensal: `data/processed/inmet_sp_mensal.csv`.
- Notebook analítico: `03_modelagem_precos_CONAB.ipynb` (ajustar ao nome efetivamente adotado no repositório).
- Arquivos anuais do INMET: dados automáticos de 2024, 2025 e 2026, conforme registrados no Notebook 03.

Os caminhos acima descrevem a organização recomendada/esperada. Confirmar os diretórios no repositório final antes da entrega. Não manter referências a scripts ou arquivos auxiliares que não estejam efetivamente incluídos no pacote entregue.
