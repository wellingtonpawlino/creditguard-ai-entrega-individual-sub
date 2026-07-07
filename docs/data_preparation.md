# Data Preparation

## Objetivo

Preparar os dados para a construção da ABT (Analytical Base Table) e para o treinamento dos modelos de Machine Learning.

---

## Problemas Identificados no Data Understanding

### Valores Ausentes

- Variáveis imobiliárias apresentam mais de 60% de valores nulos.

### Variáveis com Comportamento Anômalo

- DAYS_EMPLOYED apresentou valores extremamente elevados.

### Variáveis Categóricas

- Foram identificadas 16 variáveis categóricas que exigirão tratamento antes da modelagem.

### Identificadores

- SK_ID_CURR atua como identificador único dos registros.

### Scores Externos

- EXT_SOURCE_1
- EXT_SOURCE_2
- EXT_SOURCE_3

Possuem potencial valor preditivo e diferentes níveis de disponibilidade dos dados.

---

## Plano de Tratamento

| Item | Status | Próxima Ação |
|----------|----------|----------|
| Valores ausentes | Pendente | Avaliar relevância para modelagem |
| DAYS_EMPLOYED | Investigado | Definir tratamento |
| Variáveis categóricas | Pendente | Definir estratégia de encoding |
| SK_ID_CURR | Definido | Utilizar apenas para rastreabilidade |
| EXT_SOURCE_1 | Investigado | Definir estratégia de imputação |
| EXT_SOURCE_2 | Pendente | Avaliar tratamento |
| EXT_SOURCE_3 | Pendente | Avaliar tratamento |

---

# Investigação 01 - DAYS_EMPLOYED

## Problema

Durante o Data Understanding foram identificados valores extremamente elevados na variável DAYS_EMPLOYED.

## Evidências

Resumo estatístico:

- Média: 63.815 dias
- Mediana: -1.213 dias
- Máximo: 365.243 dias

Valor especial identificado:

- 365.243 dias

Ocorrências:

- 55.374 registros

Percentual da base:

- 18,01%

## Resultado

Taxa de inadimplência observada:

- Clientes sem o valor especial: 8,66%
- Clientes com valor 365243: 5,40%

## Interpretação

O valor aparece exatamente igual em uma quantidade muito elevada de registros, indicando que provavelmente não representa um tempo real de emprego.

Além disso, os clientes associados a esse valor apresentam comportamento diferente do restante da população, com menor taxa de inadimplência.

Isso sugere que o valor não deve ser tratado apenas como erro de cadastro.

## Decisão

- Não remover registros.
- Não descartar a variável.
- Avaliar estratégia que preserve essa informação durante a modelagem.
- Investigar posteriormente se o valor representa um código especial do sistema de origem.

## Status

✅ Investigação concluída.

---

# Investigação 02 - EXT_SOURCE_1

## Problema

A variável EXT_SOURCE_1 apresentou elevado percentual de valores ausentes.

## Evidências

Percentual de valores ausentes:

- EXT_SOURCE_1: 56,38%

Análise da taxa de inadimplência:

- Clientes com informação disponível: 7,50%
- Clientes sem informação disponível: 8,52%

## Interpretação

A ausência da informação está associada a uma taxa de inadimplência superior à observada nos clientes que possuem o valor preenchido.

Isso indica que o missing pode carregar informação relevante para o problema de negócio.

Em outras palavras, a ausência da informação pode ser tão importante quanto a própria informação disponível.

## Decisão

- Não remover a variável.
- Avaliar estratégia de imputação.
- Avaliar criação de uma flag binária indicando ausência do valor.

## Status

✅ Investigação concluída.

---

# Situação Atual da Preparação dos Dados

## Investigações Concluídas

- DAYS_EMPLOYED
- EXT_SOURCE_1

## Investigações Pendentes

- Variáveis imobiliárias com mais de 60% de valores ausentes;
- Estratégia de tratamento para EXT_SOURCE_2;
- Estratégia de tratamento para EXT_SOURCE_3;
- Estratégia de encoding para variáveis categóricas;
- Definição das variáveis que irão compor a ABT.

## Próximo Passo

Avaliar as variáveis imobiliárias com elevado percentual de valores ausentes para determinar sua relevância para a modelagem e decidir entre remoção, imputação ou criação de indicadores de ausência.




## Investigação 03 - Variáveis Imobiliárias

### Problema

Diversas variáveis relacionadas a imóveis apresentam mais de 68% de valores ausentes.

### Evidências

Percentual de ausência:

- COMMONAREA_AVG: 69,87%
- LIVINGAPARTMENTS_AVG: 68,35%
- NONLIVINGAPARTMENTS_AVG: 69,43%

Taxa de inadimplência:

COMMONAREA_AVG

- Com informação: 6,91%
- Sem informação: 8,57%

LIVINGAPARTMENTS_AVG

- Com informação: 6,89%
- Sem informação: 8,62%

NONLIVINGAPARTMENTS_AVG

- Com informação: 6,91%
- Sem informação: 8,58%

### Interpretação

A ausência das informações está associada a uma taxa de inadimplência superior à observada nos clientes com dados preenchidos.

Isso sugere que os valores ausentes possuem potencial valor preditivo.

### Decisão

- Não remover automaticamente essas variáveis.
- Avaliar criação de indicadores de ausência.
- Avaliar impacto na modelagem antes de qualquer exclusão.

### Status

✅ Investigação concluída.


## Investigação 04 - Variáveis Categóricas

### Problema

A base possui 16 variáveis categóricas que não podem ser utilizadas diretamente pelos algoritmos de Machine Learning.

### Evidências

Foram identificadas:

- Variáveis binárias;
- Variáveis com baixa cardinalidade;
- Variáveis com alta cardinalidade;
- Categorias raras;
- Variáveis com elevado percentual de ausências.

Principais observações:

- CODE_GENDER possui categoria XNA com apenas 4 registros;
- NAME_FAMILY_STATUS possui categoria Unknown com apenas 2 registros;
- OCCUPATION_TYPE possui aproximadamente 31% de valores ausentes;
- ORGANIZATION_TYPE apresenta 58 categorias distintas.

### Interpretação

As variáveis categóricas apresentam potencial informacional relevante para o problema de crédito.

Entretanto, exigirão definição cuidadosa da estratégia de encoding e tratamento de categorias raras.

### Decisão

Pendente.

## Definição Inicial da ABT V1

Objetivo:
Construir uma primeira base analítica contendo apenas variáveis consideradas relevantes para risco de crédito e com menor complexidade de tratamento.

Quantidade inicial:
~25 atributos + TARGET

## Auditoria da ABT V1

### Estrutura

- 307.511 registros
- 28 atributos

### Principais Problemas Identificados

#### Elevado volume de ausência

- EXT_SOURCE_1 (56,38%)
- OCCUPATION_TYPE (31,35%)
- EXT_SOURCE_3 (19,83%)

#### Volume moderado de ausência

Variáveis de consulta ao bureau:

- AMT_REQ_CREDIT_BUREAU_DAY
- AMT_REQ_CREDIT_BUREAU_WEEK
- AMT_REQ_CREDIT_BUREAU_MON
- AMT_REQ_CREDIT_BUREAU_QRT
- AMT_REQ_CREDIT_BUREAU_YEAR

Todas com aproximadamente 13,50% de valores ausentes.

### Conclusão

A ABT V1 apresenta boa qualidade geral dos dados e quantidade limitada de variáveis críticas para tratamento.


## Investigação 05 - Variáveis do Bureau

### Problema

As variáveis de consulta ao bureau apresentaram aproximadamente 13,5% de valores ausentes.

### Evidências

Variáveis analisadas:

- AMT_REQ_CREDIT_BUREAU_DAY
- AMT_REQ_CREDIT_BUREAU_WEEK
- AMT_REQ_CREDIT_BUREAU_MON
- AMT_REQ_CREDIT_BUREAU_QRT
- AMT_REQ_CREDIT_BUREAU_YEAR

As distribuições apresentaram forte concentração em zero.

### Interpretação

As variáveis representam contagens de consultas ao bureau em diferentes janelas temporais.

A predominância de valores iguais a zero sugere que a ausência da informação pode representar inexistência de consulta registrada.

### Decisão

- Manter as variáveis.
- Substituir valores ausentes por zero na ABT V1.

### Status

✅ Investigação concluída.

# Matriz de Tratamento - ABT V1

| Variável | Tratamento |
|-----------|-----------|
| TARGET | Manter |
| AMT_INCOME_TOTAL | Manter |
| AMT_CREDIT | Manter |
| AMT_ANNUITY | Manter |
| AMT_GOODS_PRICE | Imputar mediana |
| DAYS_BIRTH | Manter |
| DAYS_EMPLOYED | Investigar tratamento do valor 365243 |
| CNT_CHILDREN | Manter |
| CNT_FAM_MEMBERS | Manter |
| FLAG_OWN_CAR | Encoding binário |
| FLAG_OWN_REALTY | Encoding binário |
| NAME_INCOME_TYPE | Encoding |
| NAME_EDUCATION_TYPE | Encoding |
| NAME_FAMILY_STATUS | Encoding |
| NAME_HOUSING_TYPE | Encoding |
| OCCUPATION_TYPE | Preencher UNKNOWN + Encoding |
| ORGANIZATION_TYPE | Encoding |
| EXT_SOURCE_1 | Criar flag + imputação |
| EXT_SOURCE_2 | Imputação simples |
| EXT_SOURCE_3 | Criar flag + imputação |
| REGION_POPULATION_RELATIVE | Manter |
| REGION_RATING_CLIENT | Manter |
| REGION_RATING_CLIENT_W_CITY | Manter |
| Bureau_* | Substituir nulos por zero |


## ABT V1 Clean

### Tratamentos Aplicados

- OCCUPATION_TYPE preenchido com UNKNOWN;
- Variáveis Bureau preenchidas com zero;
- Criação das flags:
    - EXT_SOURCE_1_MISSING
    - EXT_SOURCE_3_MISSING
- Imputação pela mediana para variáveis numéricas restantes.

### Resultado

A ABT V1 passou a apresentar:

- 307.511 registros;
- ausência de valores nulos;
- conjunto reduzido de atributos relevantes para modelagem.

### Status

✅ ABT V1 Clean concluída.

## Validação da ABT V1 Clean

### Estrutura Final

- Registros: 307.511
- Variáveis: 30
- Valores ausentes: 0

### Variáveis Numéricas

22 colunas prontas para modelagem.

### Variáveis Categóricas

8 colunas exigirão transformação:

- FLAG_OWN_CAR
- FLAG_OWN_REALTY
- NAME_INCOME_TYPE
- NAME_EDUCATION_TYPE
- NAME_FAMILY_STATUS
- NAME_HOUSING_TYPE
- OCCUPATION_TYPE
- ORGANIZATION_TYPE

### Conclusão

A ABT V1 encontra-se preparada para a etapa de encoding e posterior modelagem.

## Investigação 04 - Variáveis Categóricas

### Resultado

Cardinalidade identificada:

- FLAG_OWN_CAR: 2
- FLAG_OWN_REALTY: 2
- NAME_INCOME_TYPE: 8
- NAME_EDUCATION_TYPE: 5
- NAME_FAMILY_STATUS: 6
- NAME_HOUSING_TYPE: 6
- OCCUPATION_TYPE: 19
- ORGANIZATION_TYPE: 58

### Interpretação

A maior parte das variáveis categóricas apresenta baixa ou média cardinalidade.

A variável ORGANIZATION_TYPE possui maior complexidade devido à quantidade de categorias.

### Decisão

Todas as variáveis categóricas serão mantidas na ABT V1 e tratadas por meio de encoding durante a preparação para modelagem.

### Status

✅ Investigação concluída.

## ABT V1 Final

### Estrutura

- Registros: 307.511
- Variáveis: 30
- Valores ausentes: 0

### Tratamentos Aplicados

- Imputação de valores ausentes em variáveis numéricas utilizando mediana;
- Preenchimento de OCCUPATION_TYPE com UNKNOWN;
- Variáveis Bureau preenchidas com zero;
- Criação de indicadores de ausência:
  - EXT_SOURCE_1_MISSING
  - EXT_SOURCE_3_MISSING

### Resultado

A ABT V1 foi validada e encontra-se apta para a etapa de modelagem.

### Status

✅ Data Preparation concluída.




# Modeling

## Modelo Baseline

Algoritmo:

- Logistic*Regression

Justificativa:

A Regressão Logística é amplamente utilizada em problemas de Credit Scoring devido à sua simplicidade, interpretabilidade e capacidade de fornecer probabilidades de inadimplência.

Objetivo:

Estabelecer uma linha de base de desempenho para comparação com modelos mais complexos.