# ProScore Analytics

## CreditGuard AI

Sistema Inteligente de Predição de Inadimplência para Concessão de Crédito

---

## Sobre o Projeto

O CreditGuard AI é uma solução desenvolvida pela ProScore Analytics com o objetivo de apoiar instituições financeiras na análise de risco de crédito através de técnicas de Machine Learning.

A solução busca identificar clientes com maior probabilidade de inadimplência antes da concessão de crédito, contribuindo para decisões mais seguras, redução de perdas financeiras e melhoria da qualidade da carteira de crédito.

---

## Problema de Negócio

Instituições financeiras enfrentam desafios constantes na concessão de crédito.

A aprovação de clientes com elevado risco de inadimplência pode gerar perdas financeiras significativas, enquanto critérios excessivamente restritivos podem impedir oportunidades de negócio.

O desafio consiste em encontrar o equilíbrio entre crescimento e controle de risco.

---

## Objetivo

Desenvolver um modelo de Machine Learning capaz de prever a probabilidade de inadimplência de clientes utilizando dados financeiros, cadastrais e comportamentais.

---

## Dataset

Home Credit Default Risk

https://www.kaggle.com/competitions/home-credit-default-risk

---

## Metodologia

O projeto segue a metodologia CRISP-DM:

1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modeling
5. Evaluation
6. Deployment

---

## Estrutura do Projeto

```
proscore-creditguard-ai/
├── Dados/
│   ├── raw/application_train.csv   ← dataset bruto (baixar do Kaggle)
│   ├── clean_data.csv              ← gerado por data_sanitization.py
│   └── abt.csv                     ← gerado por abt_transform.py
├── DataPipeline/
│   ├── data_sanitization.py        ← limpeza e construção da ABT limpa
│   ├── abt_transform.py            ← encoding e geração do ABT final
│   ├── exp_analysis.ipynb          ← análise exploratória
│   └── config.yaml                 ← paths e parâmetros do pipeline
├── Model/
│   ├── train.py                    ← treinamento do modelo LightGBM
│   ├── predict.py                  ← serviço de inferência
│   ├── evaluation.ipynb            ← avaliação de métricas e curvas
│   ├── config.yaml                 ← hiperparâmetros e paths de artefatos
│   └── artifacts/
│       ├── lgbm_balanced_model.joblib
│       ├── features.joblib
│       └── medianas.joblib
├── app/
│   ├── app.py                      ← interface Streamlit
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── requirements.txt
```

---

## Instruções de Treinamento

### Pré-requisito: obter os dados

Baixe o dataset **Home Credit Default Risk** do Kaggle:

```
https://www.kaggle.com/competitions/home-credit-default-risk/data
```

Extraia os arquivos em `Dados/raw/`. O pipeline utiliza `application_train.csv`.

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o pipeline de dados

Os comandos abaixo devem ser executados a partir da raiz do projeto.

```bash
# Etapa 1 — sanitização: gera Dados/clean_data.csv e Model/artifacts/medianas.joblib
python DataPipeline/data_sanitization.py

# Etapa 2 — transformação: gera Dados/abt.csv (307511 linhas × 120 colunas)
python DataPipeline/abt_transform.py
```

### 3. Treinar o modelo

```bash
# Treina o LightGBM Balanced e salva os artefatos em Model/artifacts/
python Model/train.py
```

Saída gerada: `Model/artifacts/lgbm_balanced_model.joblib` e `Model/artifacts/features.joblib`.

Métricas obtidas no treinamento completo (307.511 registros, split 80/20):

| Métrica | LightGBM Balanced (v2) | XGBoost Balanced (v1) |
|---|---|---|
| ROC-AUC | **0,7524** | 0,7509 |
| Recall  | **0,6606** | 0,6568 |
| Gini    | **0,5049** | 0,5019 |
| KS      | **0,3736** | 0,3694 |
| Tempo   | **2,89 s** | 4,00 s |

### 4. Avaliar o modelo

Abra e execute `Model/evaluation.ipynb` no Jupyter:

```bash
jupyter lab Model/evaluation.ipynb
```

### 5. Executar a aplicação web

```bash
docker-compose up --build
```

Acesse em `http://localhost:8501`.

---

## Como Executar o Serviço de Predição

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/) instalados
- Os artefatos do modelo já treinados em `Model/artifacts/` (incluídos no repositório)

### Subindo o stack completo

```bash
# A partir da raiz do projeto
docker-compose up --build
```

Serviços disponíveis após a inicialização:

| Serviço | URL | Credenciais |
|---|---|---|
| **Aplicação de predição (Streamlit)** | http://localhost:8501 | — |
| Airflow (orquestração) | http://localhost:8082 | admin / admin |
| MinIO Console (artefatos) | http://localhost:9101 | minioadmin / minioadmin |
| PostgreSQL (logs) | localhost:5433 | creditguard / creditguard |

### Usando o serviço de predição

1. Acesse `http://localhost:8501` no navegador
2. Preencha os atributos do cliente no formulário:

| Campo | Descrição | Exemplo |
|---|---|---|
| Renda Total do Cliente | `AMT_INCOME_TOTAL` em R$ | 150.000 |
| Valor do Crédito | `AMT_CREDIT` solicitado | 300.000 |
| Valor da Anuidade | `AMT_ANNUITY` (prestação anual) | 25.000 |
| Número de Filhos | `CNT_CHILDREN` | 0 |
| Idade | Convertida internamente para `DAYS_BIRTH` | 35 |
| EXT_SOURCE_1/2/3 | Scores externos de bureau (0 a 1) | 0.50 |

3. Clique em **Analisar Cliente**
4. O modelo retorna:
   - **Probabilidade de inadimplência** (em %)
   - **Classificação: ALTO RISCO** (prediction = 1) ou **BAIXO RISCO** (prediction = 0)
   - **Ação recomendada** (revisão manual ou aprovação automática)

Cada predição é registrada automaticamente na tabela `predictions` do PostgreSQL com timestamp, inputs, resultado e versão do modelo.

### Subindo apenas a aplicação (sem Airflow)

Se o objetivo for apenas testar a predição sem o stack de orquestração:

```bash
docker-compose up --build creditguard-app minio postgres minio-init
```

### Execução local sem Docker

```bash
# Instalar dependências mínimas da aplicação
pip install -r app/requirements.txt

# Rodar a partir da raiz do projeto
streamlit run app/app.py --server.address=0.0.0.0
```

> Neste modo, o MinIO e o PostgreSQL não estarão disponíveis. O modelo é carregado do fallback local (`Model/artifacts/`) e o log de predições é silenciosamente ignorado.

### Verificando os logs do container

```bash
# Logs em tempo real da aplicação
docker logs -f creditguard-ai

# Verificar predições registradas no PostgreSQL
docker exec -it creditguard-postgres psql -U creditguard -d creditguard \
  -c "SELECT created_at, prediction, probability, model_version FROM predictions ORDER BY created_at DESC LIMIT 10;"
```

### Variáveis de ambiente relevantes

| Variável | Padrão | Descrição |
|---|---|---|
| `MODEL_VERSION` | `v1` | Versão do modelo buscada no MinIO |
| `MINIO_ENDPOINT` | `minio:9000` | Endereço do MinIO (interno ao Docker) |
| `POSTGRES_HOST` | `postgres` | Host do banco de dados |
| `OMP_NUM_THREADS` | `1` | Threads OpenMP do XGBoost (estabilidade em container) |