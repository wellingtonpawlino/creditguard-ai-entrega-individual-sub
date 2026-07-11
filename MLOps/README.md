# MLOps — CreditGuard AI

Documentação da infraestrutura MLOps implementada no projeto ProScore Analytics — CreditGuard AI.

---

## Visão Geral

A camada MLOps do projeto é composta por cinco componentes integrados, orquestrados via `docker-compose.yml` na raiz do projeto:

```
Airflow (orquestração)
    ↓
DataPipeline → Model/artifacts → Streamlit (app)
                    ↓
               MinIO (armazenamento)
               PostgreSQL (persistência)
```

---

## Componentes Implementados

### 1. Streamlit — Interface de Predição (`app/app.py`)

Interface web que expõe o modelo ao usuário final.

- Porta: `8501`
- Coleta 8 atributos do cliente (renda, crédito, idade, scores externos etc.)
- Chama `Model/predict.py` e exibe o resultado: **ALTO RISCO** ou **BAIXO RISCO** com probabilidade de inadimplência
- Após cada predição, registra o resultado no PostgreSQL via `utils/db.py`
- Lê a versão do modelo da variável de ambiente `MODEL_VERSION`

---

### 2. MinIO — Armazenamento de Artefatos (`utils/storage.py`)

Armazenamento de objetos compatível com S3, usado para versionar artefatos do modelo.

- Console: `http://localhost:9101`
- API: `http://localhost:9100`
- Credenciais padrão: `minioadmin / minioadmin`

**Buckets criados automaticamente pelo `minio-init`:**

| Bucket | Conteúdo |
|---|---|
| `raw-data` | Dataset bruto (application_train.csv) |
| `processed-data` | ABT gerada pelo DataPipeline |
| `model-artifacts` | Modelo serializado e lista de features |

**Artefatos versionados por `MODEL_VERSION` (padrão: `v1`):**

```
model-artifacts/
└── v1/
    ├── xgb_balanced_model.joblib
    └── features.joblib
```

O `predict.py` tenta carregar os artefatos do MinIO primeiro; na ausência de conexão, faz fallback para o sistema de arquivos local (`Model/artifacts/`).

---

### 3. PostgreSQL — Persistência (`utils/db.py`, `infra/init.sql`)

Banco de dados relacional para rastreabilidade de predições e registro de modelos.

- Porta: `5433` (mapeada externamente)
- Banco: `creditguard` (aplicação) + `airflow` (metadados do Airflow)
- Usuário/senha: `creditguard / creditguard`

**Tabela `predictions` — log de predições em produção:**

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | SERIAL | Identificador único |
| `created_at` | TIMESTAMP | Data/hora da predição |
| `amt_income_total` | FLOAT | Renda informada |
| `amt_credit` | FLOAT | Valor do crédito solicitado |
| `amt_annuity` | FLOAT | Valor da prestação |
| `cnt_children` | INTEGER | Número de filhos |
| `days_birth` | INTEGER | Idade em dias (negativo) |
| `ext_source_1/2/3` | FLOAT | Scores externos |
| `prediction` | INTEGER | 0 = Adimplente, 1 = Inadimplente |
| `probability` | FLOAT | Probabilidade de inadimplência |
| `model_version` | VARCHAR | Versão do modelo utilizada |

**Tabela `model_registry` — registro de versões do modelo:**

| Coluna | Tipo | Descrição |
|---|---|---|
| `version` | VARCHAR | Identificador da versão (ex: `v1`) |
| `roc_auc` | FLOAT | ROC-AUC no conjunto de teste |
| `recall` | FLOAT | Recall no conjunto de teste |
| `precision_score` | FLOAT | Precision no conjunto de teste |
| `f1` | FLOAT | F1-Score no conjunto de teste |
| `accuracy` | FLOAT | Acurácia no conjunto de teste |
| `is_active` | BOOLEAN | Indica se é o modelo em produção |
| `artifact_bucket` | VARCHAR | Bucket MinIO do artefato |
| `artifact_path` | VARCHAR | Caminho do artefato no bucket |

---

### 4. Apache Airflow — Orquestração (`dags/creditguard_pipeline.py`)

Orquestrador do pipeline de dados e treinamento.

- Webserver: `http://localhost:8082` (usuário: `admin` / senha: `admin`)
- Executor: `LocalExecutor`
- Versão: `2.10.0`
- Metadados armazenados no PostgreSQL (`airflow` database)

---

### 5. DAG `creditguard_pipeline`

Pipeline completo de retreinamento, acionado manualmente (`schedule=None`).

```
extract_data → data_sanitization → abt_transform → train_model
```

| Task | Função | Descrição |
|---|---|---|
| `extract_data` | `check_raw_data()` | Valida presença do CSV bruto em `Dados/raw/` |
| `data_sanitization` | `run_sanitization()` | Limpeza e tratamento dos dados brutos |
| `abt_transform` | `run_transform()` | Construção da ABT com encoding e feature engineering |
| `train_model` | `run_training()` | Treina o XGBoost Balanced e salva os artefatos |

---

## Como Subir o Stack Completo

```bash
docker-compose up --build
```

| Serviço | URL |
|---|---|
| Streamlit (app) | http://localhost:8501 |
| Airflow Webserver | http://localhost:8082 |
| MinIO Console | http://localhost:9101 |
| PostgreSQL | localhost:5433 |

---

## Modelo em Produção

| Métrica | Valor |
|---|---|
| Algoritmo | XGBoost com `scale_pos_weight` |
| ROC-AUC | 0.7509 |
| Recall | 0.6568 |
| Gini | 0.5019 |
| KS | 0.3694 |
| Features | 119 (pós-encoding) |
| Versão ativa | v1 |

O Recall é a métrica prioritária: o custo de aprovar um inadimplente supera o custo de negar um bom pagador.
