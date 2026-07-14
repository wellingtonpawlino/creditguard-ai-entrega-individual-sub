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
│   ├── raw/bureau.csv              ← histórico de bureau (baixar do Kaggle)
│   ├── clean_data.csv              ← gerado por data_sanitization.py
│   └── abt.csv                     ← gerado por abt_transform.py
├── DataPipeline/
│   ├── data_sanitization.py        ← feature engineering (application + bureau) e merge
│   ├── abt_transform.py            ← validação e persistência da ABT
│   ├── exp_analysis.ipynb          ← análise exploratória
│   └── config.yaml                 ← paths das fontes de dados
├── Model/
│   ├── train.py                    ← comparação de 5 modelos + ColumnTransformer
│   ├── predict.py                  ← serviço de inferência
│   ├── evaluation.ipynb            ← avaliação de métricas e curvas (5 modelos)
│   ├── config.yaml                 ← hiperparâmetros e paths de artefatos
│   └── artifacts/
│       ├── preprocessor.joblib     ← ColumnTransformer ajustado no treino
│       ├── best_model.joblib       ← melhor modelo por ROC-AUC
│       ├── features.joblib         ← nomes das features brutas (pré-encoding)
│       ├── comparacao_modelos.csv  ← tabela comparativa dos 5 modelos
│       └── metadata_modelo.json    ← métricas e metadados do modelo eleito
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

Extraia os arquivos em `Dados/raw/`. O pipeline utiliza **dois** arquivos:

| Arquivo | Descrição |
|---|---|
| `application_train.csv` | Dados cadastrais e financeiros dos 307.511 clientes |
| `bureau.csv` | Histórico de créditos anteriores reportados ao bureau |

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o pipeline de dados

Os comandos abaixo devem ser executados a partir da raiz do projeto.

```bash
# Etapa 1 — feature engineering: gera Dados/clean_data.csv
#   - Razões financeiras (CREDIT_INCOME_RATIO, ANNUITY_INCOME_RATIO, etc.)
#   - Variáveis temporais (AGE_YEARS, EMPLOYED_YEARS, EMPLOYED_AGE_RATIO)
#   - Agregações de bureau por cliente (contagens, somas, médias, razões de dívida)
python DataPipeline/data_sanitization.py

# Etapa 2 — validação: gera Dados/abt.csv (307.511 linhas, ~60 features brutas)
python DataPipeline/abt_transform.py
```

### 3. Treinar o modelo

```bash
# Compara 5 modelos e salva os artefatos do melhor em Model/artifacts/
python Model/train.py
```

Artefatos gerados:

| Arquivo | Descrição |
|---|---|
| `preprocessor.joblib` | ColumnTransformer (SimpleImputer + OneHotEncoder), ajustado só no treino |
| `best_model.joblib` | Modelo eleito por ROC-AUC |
| `features.joblib` | Lista de features brutas esperadas na inferência |
| `comparacao_modelos.csv` | Tabela comparativa dos 5 modelos |
| `metadata_modelo.json` | Métricas e metadados do modelo eleito |

Métricas obtidas no treinamento completo (307.511 registros, split 80/20):

| Modelo | ROC-AUC | Recall | Precision | Acurácia |
|---|---|---|---|---|
| Dummy | ~0,50 | — | — | ~91,9% |
| Regressão Logística | ~0,72 | — | — | — |
| Random Forest | ~0,74 | — | — | — |
| XGBoost | ~0,76 | — | — | — |
| **LightGBM** | **0,7778** | **65,82%** | **18,90%** | **74,44%** |

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

| Campo | Feature | Exemplo |
|---|---|---|
| Renda Anual do Cliente (R$) | `AMT_INCOME_TOTAL` | 150.000 |
| Valor do Crédito Solicitado (R$) | `AMT_CREDIT` | 300.000 |
| Valor da Parcela Anual (R$) | `AMT_ANNUITY` | 25.000 |
| Valor de Entrada (R$) | Calcula `AMT_GOODS_PRICE = AMT_CREDIT + Entrada` | 50.000 |
| Idade do Cliente | Convertida para `DAYS_BIRTH = -(idade × 365)` | 35 |
| Tempo no Emprego Atual (anos) | Convertido para `DAYS_EMPLOYED = -(anos × 365)` | 5 |
| Número de Filhos | `CNT_CHILDREN` | 0 |
| Score Bureau 1 (0,00 – 1,00) | `EXT_SOURCE_1` — 3º maior preditor | 0,50 |
| Score Bureau 2 (0,00 – 1,00) | `EXT_SOURCE_2` — 2º maior preditor | 0,50 |
| Score Bureau 3 (0,00 – 1,00) | `EXT_SOURCE_3` — maior preditor do modelo | 0,50 |

3. Clique em **Analisar Cliente**
4. O modelo retorna:
   - **Probabilidade de inadimplência** (em %)
   - **Classificação em 3 níveis de risco:**

| Classificação | Faixa | Ação recomendada |
|---|---|---|
| 🟢 BAIXO RISCO | < 30% | Aprovação automática recomendada |
| 🟡 MÉDIO RISCO | 30% – 69% | Análise complementar recomendada |
| 🔴 ALTO RISCO | ≥ 70% | Revisão manual obrigatória |

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
| `MODEL_VERSION` | `v2` | Versão do modelo buscada no MinIO |
| `MINIO_ENDPOINT` | `minio:9000` | Endereço do MinIO (interno ao Docker) |
| `POSTGRES_HOST` | `postgres` | Host do banco de dados |
| `OMP_NUM_THREADS` | `1` | Limita threads OpenMP — garante estabilidade do LightGBM em container |