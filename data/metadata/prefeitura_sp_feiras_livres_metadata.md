# Metadados — Prefeitura de São Paulo (Feiras Livres)

## 1. Identificação da fonte

- **Fonte:** Prefeitura Municipal de São Paulo.
- **Documento:** *Endereços das Feiras Livres*.
- **Abrangência:** município de São Paulo, Brasil.
- **Formato original:** PDF, 25 páginas.
- **Data de consulta e extração registrada:** 09/11/2026.

## 2. Caracterização dos dados

O documento contém informações cadastrais das feiras livres distribuídas conforme a organização territorial apresentada pela Prefeitura. Os campos estruturados incluem subprefeitura/agrupamento territorial, dia, categoria, quantidade de feirantes, nome da feira, tipo de logradouro, logradouro, bairro e página de origem.

A base contém 933 registros e nove colunas. O campo `subprefeitura` apresenta 31 valores distintos, mas alguns valores representam agrupamentos compostos de subprefeituras. Portanto, **31 valores distintos nesse campo não devem ser descritos como 31 subprefeituras oficiais individualizadas**.

## 3. Arquivos relacionados

### `prefeitura_sp_feiras_livres_enderecos.pdf`

Documento original disponibilizado pela Prefeitura.

### `prefeitura_sp_feiras_livres.csv`

Base estruturada a partir da extração e revisão do PDF:
- 933 registros;
- nove colunas, incluindo a página de origem;
- separador `;`;
- codificação UTF-8 com BOM.

Uma linha que não foi reconhecida automaticamente foi recuperada por revisão manual e incorporada à base principal.

### `prefeitura_sp_feiras_livres_revisar.csv`

Arquivo auxiliar de linhas que exigiram conferência durante a extração. Deve ser mantido somente se o repositório final utilizar esse artefato como registro de auditoria.

### `prefeitura_sp_feiras_livres_normalizado.csv`

Versão tratada que preserva a quantidade de registros e colunas da base estruturada e aplica duas correções de caracteres identificadas na auditoria. Esta é a versão recomendada para análises e visualizações que dependam dos textos corrigidos.

### `prefeitura_sp_feiras_livres_correcoes.csv`

Histórico das correções textuais aplicadas à versão normalizada.

### `prefeitura_sp_valores_unicos_auditoria.csv`

Arquivo auxiliar de auditoria dos valores únicos e variações textuais. Não substitui a base normalizada utilizada nas análises.

## 4. Classificação dos dados

- **Observados/cadastrais:** informações transcritas do documento municipal.
- **Derivados:** contagens, agrupamentos, padronizações e cruzamentos calculados a partir do cadastro.
- **Simulados:** não há dados simulados nesta base.

A extração estrutura informações administrativas publicadas; não representa uma nova pesquisa de campo.

## 5. Tratamento e validação

A extração foi realizada com Python e `pdfplumber`. A validação registrada encontrou:
- 933 registros;
- nenhuma coluna esperada ausente;
- nenhum campo vazio;
- nenhuma linha completamente duplicada;
- nenhuma duplicidade identificada pela chave de conferência utilizada;
- nenhum valor não numérico ou negativo em `quantidade_feirantes`;
- nenhuma página inválida.

Essas verificações avaliam a estrutura e a consistência interna da extração. Não garantem que todas as informações cadastrais estejam atualizadas na operação cotidiana.

## 6. Registros com quantidade de feirantes igual a zero

Foram identificados 23 registros com `quantidade_feirantes = 0`; a conferência do PDF confirmou que os valores constam na fonte. A legislação municipal prevê competências administrativas relacionadas à criação, extinção e suspensão de feiras, mas não há evidência suficiente para afirmar que esses 23 registros representam feiras inativas.

Os valores foram preservados. A situação operacional desses registros permanece não confirmada.

A soma do campo `quantidade_feirantes` é um total de valores declarados no cadastro. Não deve ser interpretada automaticamente como quantidade de pessoas únicas, número de barracas em funcionamento em uma data específica ou medida de desperdício.

## 7. Anomalias de caracteres e normalização

A auditoria textual identificou:
- `MAESTRO JOÞO EVANGELISTA` → `MAESTRO JOÃO EVANGELISTA`;
- `SÞO MIGUEL` → `SÃO MIGUEL`.

As alterações foram aplicadas somente na base normalizada, preservando a extração original. A validação posterior confirmou 933 registros, nove colunas e duas correções aplicadas.

Scripts associados, conforme os nomes registrados no projeto:
- `extrair_feiras_prefeitura.py`;
- `validar_feiras_prefeitura.py`;
- `normalizar_feiras_prefeitura.py`;
- `validar_feiras_normalizadas.py`.

Confirmar a presença e os caminhos desses scripts no repositório final antes de citá-los como parte do pacote entregue.

## 8. Limitações

- O cadastro é administrativo, não uma pesquisa de campo sobre o funcionamento efetivo de cada feira.
- A quantidade de feirantes não equivale necessariamente à quantidade de barracas em funcionamento em uma data específica.
- Os dados não medem vendas, estoque, sobras ou geração de resíduos alimentares.
- A data de referência original do cadastro precisa ser confirmada na fonte.
- A extração automatizada foi validada estruturalmente, mas ainda pode conter erros de transcrição ou interpretação.
- Os 933 registros não devem ser tratados automaticamente como 933 feiras únicas e ativas.

## 9. Relação com Brancoli et al. (2022)

O cadastro municipal é utilizado como fonte complementar de localização e características administrativas. Seus dados não são tratados automaticamente como observações do estudo de Brancoli.

As fontes têm períodos, metodologias e finalidades diferentes. As quatro correspondências identificadas entre as feiras do estudo e o cadastro municipal permanecem exploratórias, conforme documentado em `correspondencias_brancoli_prefeitura.md`.

## 10. Rastreabilidade

- Documento original: Prefeitura de São Paulo, *Endereços das Feiras Livres*.
- PDF utilizado: `prefeitura_sp_feiras_livres_enderecos.pdf`.
- Base estruturada: `prefeitura_sp_feiras_livres.csv`.
- Base normalizada: `prefeitura_sp_feiras_livres_normalizado.csv`.
- Data de extração registrada: 09/11/2026.
