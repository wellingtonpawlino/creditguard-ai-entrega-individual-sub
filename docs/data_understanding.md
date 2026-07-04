## Estrutura dos Dados

### Descoberta

A tabela principal (application_train.csv) possui:

- 307.511 registros
- 122 variáveis

Distribuição dos tipos de dados:

- 65 variáveis do tipo float64
- 41 variáveis do tipo int64
- 16 variáveis categóricas (string)

Memória utilizada pela tabela:

- 286,2 MB

### Interpretação Técnica

A base possui predominância de variáveis numéricas, característica comum em problemas de Credit Scoring e Risco de Crédito.

As 16 variáveis categóricas exigirão tratamento durante a fase de Data Preparation para que possam ser utilizadas pelos algoritmos de Machine Learning.

### Impacto no Projeto

A diversidade de variáveis disponíveis aumenta o potencial preditivo do modelo e permite analisar características financeiras, profissionais e demográficas dos clientes.

## Qualidade dos Dados

### Descoberta

As variáveis com maior quantidade de valores ausentes são:

| Variável | Valores Nulos |
|-----------|--------------:|
| COMMONAREA_AVG | 214.865 |
| COMMONAREA_MODE | 214.865 |
| COMMONAREA_MEDI | 214.865 |
| NONLIVINGAPARTMENTS_MEDI | 213.514 |
| NONLIVINGAPARTMENTS_MODE | 213.514 |
| NONLIVINGAPARTMENTS_AVG | 213.514 |
| FONDKAPREMONT_MODE | 210.295 |
| LIVINGAPARTMENTS_AVG | 210.199 |
| LIVINGAPARTMENTS_MEDI | 210.199 |
| LIVINGAPARTMENTS_MODE | 210.199 |

### Interpretação Técnica

Foi identificada uma quantidade significativa de valores ausentes em diversas variáveis relacionadas às características físicas dos imóveis dos clientes.

Algumas colunas possuem mais de 200 mil registros ausentes, representando uma parcela expressiva da base de dados.

### Possíveis Hipóteses

- Essas informações podem não ter sido coletadas para todos os clientes.
- Alguns tipos de crédito podem não exigir informações detalhadas do imóvel.
- Existem diferenças entre perfis de clientes e processos de cadastro.

### Impacto no Projeto

As variáveis com elevado percentual de ausência deverão ser analisadas durante a etapa de Data Preparation para definir se serão:

- Removidas;
- Imputadas;
- Transformadas em indicadores de ausência;
- Mantidas para avaliação de relevância preditiva.

## Qualidade dos Dados - Valores Ausentes

### Descoberta

As variáveis com maior percentual de valores ausentes estão relacionadas principalmente às características físicas dos imóveis.

Principais ocorrências:

| Variável | % Nulos |
|------------|---------:|
| COMMONAREA_AVG | 69,87% |
| COMMONAREA_MODE | 69,87% |
| COMMONAREA_MEDI | 69,87% |
| NONLIVINGAPARTMENTS_MEDI | 69,43% |
| NONLIVINGAPARTMENTS_MODE | 69,43% |
| NONLIVINGAPARTMENTS_AVG | 69,43% |
| FONDKAPREMONT_MODE | 68,39% |
| LIVINGAPARTMENTS_AVG | 68,35% |
| LIVINGAPARTMENTS_MEDI | 68,35% |
| LIVINGAPARTMENTS_MODE | 68,35% |

### Interpretação Técnica

Foi identificado um conjunto de variáveis com mais de 60% de dados ausentes.

A maior concentração de valores nulos está associada a atributos imobiliários, indicando que essas informações podem não ter sido coletadas para todos os clientes ou não serem relevantes para determinados tipos de operação de crédito.

### Impacto no Projeto

Essas variáveis deverão ser analisadas cuidadosamente durante a etapa de Data Preparation.

Neste momento não será tomada nenhuma decisão de exclusão ou imputação dos dados, pois ainda é necessário avaliar:

- importância preditiva das variáveis;
- significado de negócio da ausência da informação;
- impacto sobre a performance dos modelos.

### Insight

A presença de grande quantidade de dados ausentes é uma característica relevante da base e indica que a etapa de preparação dos dados terá papel fundamental na construção da solução.

## Mapeamento das Variáveis

### Descoberta

As 122 variáveis da tabela principal podem ser agrupadas em diferentes categorias de informação sobre o cliente.

### Principais grupos identificados

#### Identificação

- SK_ID_CURR
- TARGET

#### Dados Demográficos

- CODE_GENDER
- DAYS_BIRTH
- CNT_CHILDREN
- CNT_FAM_MEMBERS

#### Dados Financeiros

- AMT_INCOME_TOTAL
- AMT_CREDIT
- AMT_ANNUITY
- AMT_GOODS_PRICE

#### Dados Profissionais

- NAME_INCOME_TYPE
- OCCUPATION_TYPE
- ORGANIZATION_TYPE
- DAYS_EMPLOYED

#### Educação e Perfil Familiar

- NAME_EDUCATION_TYPE
- NAME_FAMILY_STATUS
- NAME_HOUSING_TYPE

#### Informações de Contato

- FLAG_PHONE
- FLAG_EMAIL
- FLAG_WORK_PHONE
- FLAG_CONT_MOBILE

#### Dados Geográficos

- REGION_RATING_CLIENT
- REGION_RATING_CLIENT_W_CITY
- REGION_POPULATION_RELATIVE

#### Fontes Externas de Score

- EXT_SOURCE_1
- EXT_SOURCE_2
- EXT_SOURCE_3

#### Informações Imobiliárias

- APARTMENTS_*
- LIVINGAREA_*
- COMMONAREA_*
- LANDAREA_*

#### Histórico de Relacionamento

- DAYS_LAST_PHONE_CHANGE

#### Consulta ao Bureau de Crédito

- AMT_REQ_CREDIT_BUREAU_HOUR
- AMT_REQ_CREDIT_BUREAU_DAY
- AMT_REQ_CREDIT_BUREAU_WEEK
- AMT_REQ_CREDIT_BUREAU_MON
- AMT_REQ_CREDIT_BUREAU_QRT
- AMT_REQ_CREDIT_BUREAU_YEAR

### Interpretação Técnica

A base apresenta informações que abrangem múltiplas dimensões do cliente:

- perfil financeiro;
- perfil demográfico;
- histórico profissional;
- relacionamento com crédito;
- características patrimoniais.

### Impacto no Projeto

A variedade de informações disponíveis aumenta o potencial de criação de um modelo robusto de predição de inadimplência, permitindo capturar diferentes fatores associados ao risco de crédito.

## Estatísticas Descritivas Iniciais

### Descoberta

A análise estatística inicial revelou algumas características relevantes da população analisada:

#### Renda dos clientes

AMT_INCOME_TOTAL

- Média: 168.797,92
- Mediana: 147.150,00
- Valor mínimo: 25.650,00
- Valor máximo: 117.000.000,00

#### Valor dos empréstimos

AMT_CREDIT

- Média: 599.025,99
- Mediana: 513.531,00
- Valor mínimo: 45.000,00
- Valor máximo: 4.050.000,00

#### Quantidade de filhos

CNT_CHILDREN

- Média: 0,42
- Mediana: 0
- Valor máximo: 19

### Interpretação Técnica

Foi identificada uma grande dispersão nos valores financeiros da base.

A diferença entre média e mediana sugere a presença de valores extremos (outliers), principalmente em renda e valor de crédito.

Além disso, a maioria dos clientes não possui filhos, embora existam registros com quantidades excepcionalmente altas.

### Impacto no Projeto

As variáveis financeiras deverão ser analisadas com maior profundidade durante as próximas etapas para identificar possíveis outliers e avaliar seu impacto na modelagem.

Neste momento nenhuma transformação será realizada, pois ainda estamos na fase de entendimento dos dados.


## Principais Variáveis de Negócio

### Descoberta

As principais variáveis relacionadas à análise de crédito apresentam os seguintes valores:

#### Renda do Cliente (AMT_INCOME_TOTAL)

- Média: 168.797,92
- Mediana: 147.150,00
- Valor mínimo: 25.650,00
- Valor máximo: 117.000.000,00

#### Valor do Crédito (AMT_CREDIT)

- Média: 599.025,99
- Mediana: 513.531,00
- Valor mínimo: 45.000,00
- Valor máximo: 4.050.000,00

#### Valor da Parcela (AMT_ANNUITY)

- Média: 27.108,57
- Mediana: 24.903,00
- Valor mínimo: 1.615,50
- Valor máximo: 258.025,50

#### Idade (DAYS_BIRTH)

A variável é armazenada em dias negativos.

- Média: -16.036 dias (~43,9 anos)
- Mediana: -15.750 dias (~43,1 anos)

#### Tempo de Emprego (DAYS_EMPLOYED)

A variável é armazenada em dias relativos.

- Média: 63.815 dias
- Mediana: -1.213 dias

### Interpretação Técnica

As variáveis financeiras apresentam grande amplitude de valores, sugerindo a existência de clientes com perfis financeiros bastante distintos.

Também foi identificado um comportamento incomum na variável DAYS_EMPLOYED, que possui valores positivos muito elevados, exigindo investigação futura durante a preparação dos dados.

### Impacto no Projeto

As variáveis de renda, valor de crédito, valor da parcela, idade e tempo de emprego possuem forte potencial para compor o modelo de predição de inadimplência e serão analisadas com maior profundidade nas próximas etapas.


### Observação

A variável DAYS_EMPLOYED apresenta valores extremamente elevados, sugerindo a existência de códigos especiais ou registros que deverão ser investigados durante a etapa de Data Preparation.

## Cardinalidade das Variáveis

### Descoberta

Foi realizada uma análise da quantidade de valores distintos por variável.

Algumas variáveis apresentam baixa cardinalidade:

| Variável | Valores Únicos |
|-----------|---------------:|
| TARGET | 2 |
| NAME_CONTRACT_TYPE | 2 |
| FLAG_OWN_REALTY | 2 |
| FLAG_OWN_CAR | 2 |
| FLAG_WORK_PHONE | 2 |

Outras apresentam alta cardinalidade:

| Variável | Valores Únicos |
|-----------|---------------:|
| DAYS_REGISTRATION | 15.688 |
| DAYS_BIRTH | 17.460 |
| EXT_SOURCE_1 | 114.584 |
| EXT_SOURCE_2 | 119.831 |
| SK_ID_CURR | 307.511 |

### Interpretação Técnica

A base contém uma combinação de:

- Variáveis categóricas binárias;
- Variáveis contínuas;
- Variáveis de identificação.

As variáveis do tipo FLAG representam indicadores binários que poderão ser utilizadas diretamente pelos modelos.

Já as variáveis EXT_SOURCE apresentam elevada granularidade e potencialmente carregam informação relevante para previsão de risco.

### Impacto no Projeto

A análise de cardinalidade auxilia na identificação de:

- Variáveis de identificação;
- Variáveis binárias;
- Variáveis contínuas;
- Possíveis candidatos para transformação durante a fase de Data Preparation.

### Observação

A variável SK_ID_CURR atua como identificador único dos registros e será importante para integração com outras tabelas do dataset.

## Variáveis Categóricas

### Descoberta

A base possui 16 variáveis categóricas.

A quantidade de categorias observadas varia significativamente entre elas.

#### Variáveis Binárias

- NAME_CONTRACT_TYPE (2)
- FLAG_OWN_CAR (2)
- FLAG_OWN_REALTY (2)
- EMERGENCYSTATE_MODE (2)

#### Baixa Cardinalidade

- CODE_GENDER (3)
- HOUSETYPE_MODE (3)
- FONDKAPREMONT_MODE (4)
- NAME_EDUCATION_TYPE (5)
- NAME_FAMILY_STATUS (6)
- NAME_HOUSING_TYPE (6)

#### Média Cardinalidade

- WEEKDAY_APPR_PROCESS_START (7)
- NAME_TYPE_SUITE (7)
- WALLSMATERIAL_MODE (7)
- NAME_INCOME_TYPE (8)

#### Alta Cardinalidade

- OCCUPATION_TYPE (18)
- ORGANIZATION_TYPE (58)

### Interpretação Técnica

A maior parte das variáveis categóricas apresenta baixa cardinalidade, tornando seu tratamento relativamente simples durante a fase de preparação dos dados.

A variável ORGANIZATION_TYPE se destaca por possuir 58 categorias distintas, indicando elevado detalhamento sobre o ambiente profissional dos clientes.

### Impacto no Projeto

As variáveis categóricas poderão fornecer informações importantes sobre:

- perfil socioeconômico;
- vínculo profissional;
- composição familiar;
- características habitacionais.

Essas informações podem auxiliar na identificação de padrões associados ao risco de crédito.

## Scores Externos de Risco (EXT_SOURCE)

### Descoberta

A base possui três variáveis denominadas:

- EXT_SOURCE_1
- EXT_SOURCE_2
- EXT_SOURCE_3

Resumo estatístico:

| Variável | Registros Válidos | Média |
|-----------|-----------------:|-------:|
| EXT_SOURCE_1 | 134.133 | 0,502 |
| EXT_SOURCE_2 | 306.851 | 0,514 |
| EXT_SOURCE_3 | 246.546 | 0,511 |

### Interpretação Técnica

As três variáveis apresentam valores normalizados entre 0 e 1 e aparentemente representam algum tipo de score externo ou indicador de risco fornecido por fontes complementares ao cadastro principal.

Observa-se também diferenças relevantes na disponibilidade das informações:

- EXT_SOURCE_2 está presente em praticamente toda a base;
- EXT_SOURCE_3 apresenta quantidade moderada de valores ausentes;
- EXT_SOURCE_1 possui elevado volume de dados faltantes.

### Impacto no Projeto

Essas variáveis merecem atenção especial durante as próximas fases do projeto, pois representam informações externas ao processo de concessão de crédito e potencialmente possuem elevado valor preditivo para análise de inadimplência.

### Observação

Os significados exatos de EXT_SOURCE_1, EXT_SOURCE_2 e EXT_SOURCE_3 deverão ser investigados utilizando a documentação oficial disponibilizada no arquivo HomeCredit_columns_description.csv.



# Conclusão do Data Understanding

A análise inicial da tabela application_train.csv permitiu compreender a estrutura geral dos dados utilizados no projeto.

Foram identificados:

- 307.511 registros;
- 122 variáveis;
- variável alvo TARGET;
- desbalanceamento natural da base (8,07% de inadimplentes);
- predominância de variáveis numéricas;
- presença de variáveis categóricas relevantes para o contexto de crédito;
- elevada quantidade de valores ausentes em atributos imobiliários;
- possíveis anomalias em variáveis como DAYS_EMPLOYED;
- presença de scores externos de risco (EXT_SOURCE).

As descobertas realizadas nesta etapa servirão de base para a próxima fase do CRISP-DM, denominada Data Preparation, na qual serão realizadas atividades de limpeza, transformação e preparação dos dados para modelagem.