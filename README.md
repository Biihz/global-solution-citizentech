# NutriRota — Global Solution CitizenTech

**Instituição:** FIAP
**Curso:** Ciência de Dados
**Projeto:** Global Solution — CitizenTech
**Tema:** Combate ao desperdício de alimentos e apoio à segurança alimentar
**Recorte territorial inicial:** município de São Paulo (SP)

## 1. Apresentação

A **NutriRota** é uma proposta de plataforma para aproximar feirantes, pequenos comércios, supermercados e distribuidores de bancos de alimentos e organizações sociais. A solução pretende apoiar a identificação, comunicação e destinação de excedentes alimentares que ainda estejam adequados ao consumo, respeitando a avaliação sanitária e a capacidade operacional das organizações receptoras.

A prova de conceito reúne três frentes analíticas com fontes e unidades distintas: (1) caracterização dos resíduos observados em quatro feiras estudadas por Brancoli et al. (2022); (2) análise territorial do cadastro municipal de feiras livres de São Paulo; e (3) análise e modelagem de preços atacadistas da CONAB, com experimento climático complementar usando dados do INMET para a CEAGESP-SP.


> [!IMPORTANT]
> **Escopo real da prova de conceito:** os modelos supervisionados efetivamente treinados estimam **preços médios mensais (R$/kg)**. Eles **não** foram treinados para prever quilogramas de excedente ou desperdício. Os indicadores de Brancoli são derivados das tabelas publicadas e limitados às quatro feiras estudadas; não constituem uma estimativa municipal nem uma previsão operacional de excedentes.

* **Aplicação interativa:** [nutrirota.streamlit.app](https://nutrirota.streamlit.app)
* **Código-fonte:** [github.com/Biihz/global-solution-citizentech](https://github.com/Biihz/global-solution-citizentech)

## 2. Problema e motivação

A identificação tardia de alimentos que deixam de ter valor comercial, somada à comunicação fragmentada entre doadores e organizações sociais, pode dificultar o aproveitamento de produtos ainda próprios para consumo. A coordenação também depende de quantidade, prazo, localização, transporte, armazenamento e capacidade de recebimento.

A NutriRota propõe apoiar essa coordenação por meio de dados e tecnologia. A ferramenta não substitui a avaliação sanitária, a triagem ou as decisões das instituições responsáveis.

## 3. Objetivo

Desenvolver uma prova de conceito analítica que organize evidências sobre resíduos em feiras, contexto territorial e dinâmica de preços de FLV, como base para uma futura plataforma de identificação e coordenação de excedentes alimentares.

### Objetivos específicos

- Caracterizar a composição dos resíduos reportados em um estudo publicado sobre quatro feiras paulistanas.
- Descrever a distribuição territorial e cadastral das feiras livres do município de São Paulo.
- Integrar exploratoriamente as quatro feiras do estudo de Brancoli ao cadastro municipal, preservando a incerteza das correspondências.
- Analisar preços mensais de dez produtos em CEASAs brasileiras.
- Comparar modelos de previsão de preços com separação temporal, validação cruzada temporal e teste final.
- Investigar, em experimento complementar restrito à CEAGESP-SP, se variáveis meteorológicas defasadas acrescentam informação preditiva.
- Documentar limitações e requisitos de dados para uma futura previsão direta de excedentes.

## 4. Fontes de dados

| Fonte | Conteúdo utilizado | O que permite analisar | O que não mede |
|---|---|---|---|
| Brancoli et al. (2022) | Transcrições das Tabelas 2 e 3, com quatro feiras e frações de resíduos | Composição e indicadores derivados para a amostra estudada | Uma série histórica municipal ou excedente futuro por feira |
| Prefeitura de São Paulo | Cadastro de feiras livres extraído do documento municipal | Distribuição cadastral por agrupamento territorial, dia, categoria e endereço | Vendas, estoque, quantidade efetiva de alimentos ou desperdício |
| CONAB | Preços mensais de dez produtos em doze CEASAs, set/2024 a set/2026 | Evolução e previsão experimental de preço médio atacadista (R$/kg) | Preços de varejo nas feiras ou quantidade desperdiçada |
| INMET — estação A701 | Observações meteorológicas horárias agregadas mensalmente | Contextualização climática da capital e experimento complementar na CEAGESP-SP | Clima das regiões produtoras que abastecem a CEAGESP ou causalidade sobre preços |

Os arquivos de metadados individuais registram detalhes, transformações, unidades, qualidade e limitações de cada fonte.

## 5. Notebooks e resultados analíticos

### Notebook 01 — Brancoli et al. (2022)

Analisa a composição dos resíduos nas quatro feiras estudadas. A base transcrita contém 104 registros, correspondentes às categorias da Tabela 3 (26 por feira). Os valores publicados são mantidos distintos dos indicadores derivados. A amostra representa uma semana de dezembro de 2021 e não deve ser generalizada automaticamente para todas as feiras de São Paulo.

O volume derivado é calculado por `kg_per_stall × number_of_stalls`. Essa ponderação usa o número de barracas informado no estudo; não é uma nova pesagem. A publicação menciona 27 frações de nível II, enquanto a transcrição da Tabela 3 utilizada contém 26 linhas por feira. A diferença está documentada e nenhuma categoria foi criada para preencher a lacuna.

### Notebook 02 — Prefeitura de São Paulo

Analisa 933 registros do cadastro municipal. O campo `subprefeitura` contém 31 valores distintos, incluindo agrupamentos compostos; portanto, não se deve apresentar esse número como 31 subprefeituras oficiais individualizadas. Vinte e três registros com quantidade de feirantes igual a zero foram preservados, sem classificá-los automaticamente como feiras inativas.

As contagens descrevem registros cadastrais; não representam necessariamente feiras únicas em operação, barracas em funcionamento, volume comercializado ou desperdício.

### Notebook 03 — CONAB + INMET

A modelagem principal utiliza preços de dez produtos em 11 CEASAs, após excluir Brasília por cobertura muito baixa e tratar dez preços iguais a zero em Goiânia (setembro de 2026) como ausentes suspeitos. O alvo é `preco` em R$/kg.

Foram comparados:
- **Baseline — Lag 1:** utiliza o preço observado do mês anterior;
- **Ridge Regression:** regressão linear regularizada;
- **Random Forest Regressor:** conjunto de árvores de decisão.

A divisão é temporal: treinamento até junho de 2026 e teste final de julho a setembro de 2026. A seleção de hiperparâmetros da modelagem nacional ocorre dentro do período de treinamento, por `TimeSeriesSplit` com três folds temporais expansivos e três meses por janela de validação. A divisão é feita por mês, mantendo juntas as observações do mesmo mês. O pré-processamento é ajustado dentro de cada pipeline e fold, somente com os dados de treino.

**Horizonte da avaliação:** as previsões são avaliadas em esquema mensal sequencial de um passo à frente (*rolling one-step-ahead*). Para cada mês, as defasagens usam os preços observados disponíveis até o mês imediatamente anterior. Portanto, o teste de julho a setembro não representa uma única previsão fixa de três meses feita em julho sem atualização das informações.

No teste nacional (`n = 299`), Ridge obteve MAE de **0,7458 R$/kg**, RMSE de **1,0600 R$/kg**, MAPE de **17,65%** e R² de **0,7406**. O resultado é uma avaliação do período reservado, não uma garantia de desempenho futuro.

O experimento complementar considera somente a CEAGESP-SP e a estação INMET A701 (Mirante de Santana). No teste (`n = 30`), Random Forest com clima obteve MAE de **0,6413 R$/kg**, RMSE de **0,8579 R$/kg**, MAPE de **16,18%** e R² de **0,6591**. A diferença frente ao Random Forest sem clima foi pequena; não deve ser interpretada como evidência causal nem generalizada para outras CEASAs.

> [!IMPORTANT]
> As métricas são resultados dos recortes e períodos avaliados. A série contém 25 referências mensais, pouco mais de dois ciclos anuais, e o teste climático possui apenas três meses por produto. A interpretação deve considerar essas limitações.

## 6. Dashboard Streamlit

O protótipo de visualização está organizado em `app/` e contém:
- **Visão Territorial:** exploração dos registros do cadastro municipal;
- **Análise de Desperdício:** visualização dos dados e indicadores derivados do estudo Brancoli;
- **Inteligência de Preços:** histórico CONAB e métricas exportadas pelo Notebook 03;
- **Insights Estratégicos:** síntese das evidências e limitações.

> [!IMPORTANT]
> O dashboard apresenta resultados analíticos e não implementa, nesta prova de conceito, o fluxo operacional de cadastro de doadores, oferta, aceite, coleta ou confirmação de doações.

Para iniciar o dashboard a partir da raiz do projeto:

```bash
streamlit run app/nutrirota.py
```

## 7. O que foi desenvolvido e o que é proposta futura

### Desenvolvido nesta prova de conceito

- Transcrição e análise exploratória dos dados publicados por Brancoli et al.
- Extração, normalização conservadora e análise territorial do cadastro municipal.
- Correspondências exploratórias entre as quatro feiras de Brancoli e o cadastro da Prefeitura.
- Consolidação, auditoria e análise dos preços mensais da CONAB.
- Consolidação mensal de dados meteorológicos do INMET para a estação A701.
- Treinamento, validação temporal e avaliação final dos modelos de previsão de preços.
- Dashboard Streamlit para explorar as bases e os resultados analíticos.

### Evoluções propostas, ainda não implementadas como operação

- Cadastro e autenticação de doadores e organizações receptoras.
- Registro de ofertas, lotes, estoque, vendas e validade.
- Integração com ERP/WMS ou WhatsApp.
- Modelo supervisionado treinado diretamente para estimar excedente real em kg.
- Motor de compatibilidade logística, aceite de ofertas e rastreabilidade de coletas.
- Operação de doações, avaliação sanitária e indicadores de impacto em ambiente real.

> [!IMPORTANT]
> Essas funcionalidades compõem a visão futura da plataforma, não resultados implementados pelos notebooks ou pelo dashboard atual.

## 8. Limitações e uso responsável

- Os dados de Brancoli abrangem quatro feiras durante uma semana; os dados brutos originais do estudo não estão disponíveis nos arquivos utilizados.
- Os volumes ponderados de Brancoli são derivados das tabelas publicadas e sujeitos a arredondamentos; não são novas pesagens.
- As correspondências entre Brancoli e Prefeitura são exploratórias, pois a publicação não fornece endereços completos para confirmação por logradouro.
- O cadastro municipal é administrativo e não mede geração de resíduos, vendas ou estoque.
- Preços atacadistas da CONAB não são medidas de desperdício e não equivalem aos preços praticados no varejo.
- A avaliação dos modelos de preço é mensal e sequencial, um passo à frente; não é uma previsão fixa de três meses sem atualização.
- A estação INMET A701 representa condições meteorológicas da capital paulista, não necessariamente das regiões produtoras.
- Não foi treinado um modelo de excedente real por falta de uma variável-alvo observada e de histórico de vendas, estoque e sobras.
- A classificação de resíduo evitável em estudo científico não significa que todo o material esteja próprio para doação.
- Qualquer doação futura deverá observar requisitos sanitários, triagem e avaliação por responsáveis habilitados.

## 9. Estrutura de arquivos

```text
NutriRota/
├── README.md
├── app/
│   ├── nutrirota.py  # entrada principal do Streamlit
│   ├── pages/        # navegação e dashboards
│   └── utils/        # configurações gerais
├── notebooks/
│   ├── 01_analise_exploratoria_Brancoli.ipynb
│   ├── 02_analise_territorial_Prefeitura_SP.ipynb
│   └── 03_modelagem_precos_CONAB.ipynb
├── data/
│   ├── raw/          # fontes originais (PDF, XLSX, ZIP/CSV)
│   ├── processed/    # bases transcritas, tratadas e integradas
│   └── metadata/     # metadados e dicionários das bases
├── src/              # scripts de extração, transformação e validação
└── requirements.txt
```

## 10. Como reproduzir

1. Clone ou baixe o repositório.
2. Crie e ative um ambiente virtual Python.
3. Instale as dependências do projeto.
4. Preserve a estrutura de diretórios esperada pelos notebooks e scripts.
5. Execute os notebooks na ordem 01, 02 e 03, a partir da pasta `notebooks/`, conferindo os caminhos relativos e as fontes necessárias.
6. Execute o dashboard a partir da raiz com `streamlit run app/nutrirota.py`.

> [!IMPORTANT]
> O Notebook 03 aceita os arquivos anuais do INMET nomeados como `INMET2024.zip`, `INMET2025.zip` e `INMET2026.zip`, desde que estejam em `data/raw/`.

## 11. Referências principais

- Brancoli, P. et al. (2022). *Compositional Analysis of Street Market Food Waste in Brazil*. Sustainability, 14(12), 7014. https://doi.org/10.3390/su14127014
- Prefeitura de São Paulo. *Endereços das Feiras Livres*. Documento cadastral municipal utilizado na extração.
- Companhia Nacional de Abastecimento (CONAB). *Boletim Hortigranjeiro — outubro de 2026*, planilha de dados mensais de preços e quantidades.
- Instituto Nacional de Meteorologia (INMET). Dados horários da estação automática A701 — São Paulo/Mirante de Santana.

---

**Nota de escopo:** NutriRota é a proposta de solução; os notebooks documentam a prova de conceito analítica realizada. A caracterização de resíduos, os indicadores derivados de Brancoli, a previsão de preços e uma eventual previsão direta de excedentes são componentes distintos e não devem ser apresentados como equivalentes.
