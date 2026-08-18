# MLOps/app — CreditGuard AI

Interface Streamlit do serviço de predição, com ações automatizadas por faixa de risco.

---

## O que faz

Expõe o modelo LightGBM v3 como aplicação web interativa. O usuário preenche 8 atributos do cliente e recebe imediatamente a probabilidade de inadimplência e a classificação de risco. Após cada predição, ações automatizadas são disparadas conforme o nível de risco:

| Classificação | Probabilidade | Ação automatizada |
|---|---|---|
| BAIXO RISCO | < 30% | Webhook de aprovação disparado ao CRM/ERP |
| MÉDIO RISCO | 30% – 69% | Agente de IA (Claude) gera parecer complementar |
| ALTO RISCO | ≥ 70% | Analista notificado via Slack ou e-mail |

Cada predição é registrada automaticamente na tabela `predictions` do PostgreSQL.

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/)
- Artefatos do modelo presentes em `Model/artifacts/` (já incluídos no repositório)

---

## Execução via Docker (recomendado)

A partir da **raiz do projeto**:

```bash
# Stack completa: app + MinIO + PostgreSQL + Airflow
docker-compose up --build

# Apenas o serviço de predição (sem Airflow)
docker-compose up --build creditguard-app minio postgres minio-init
```

A partir de **MLOps/**:

```bash
cd MLOps
docker-compose up --build
```

Acesse em `http://localhost:8501`.

---

## Execução local (sem Docker)

```bash
# A partir da raiz do projeto
pip install -r MLOps/app/requirements.txt
streamlit run MLOps/app/app.py --server.address=0.0.0.0
```

Neste modo o MinIO e o PostgreSQL não estão disponíveis. O modelo é carregado do fallback local (`Model/artifacts/`) e o log de predições é silenciosamente ignorado.

---

## Campos do formulário

| Campo | Feature interna | Exemplo |
|---|---|---|
| Renda Anual (R$) | `AMT_INCOME_TOTAL` | 150.000 |
| Valor do Crédito (R$) | `AMT_CREDIT` | 300.000 |
| Número de Filhos | `CNT_CHILDREN` | 0 |
| Idade (anos) | `DAYS_BIRTH = -(idade × 365)` | 35 |
| Tempo no Emprego Atual (anos) | `DAYS_EMPLOYED = -(anos × 365)` | 5 |
| Score Bureau 1 (0,00 – 1,00) | `EXT_SOURCE_1` | 0,50 |
| Score Bureau 2 (0,00 – 1,00) | `EXT_SOURCE_2` | 0,50 |
| Score Bureau 3 (0,00 – 1,00) | `EXT_SOURCE_3` | 0,50 |

`AMT_GOODS_PRICE` é fixado igual a `AMT_CREDIT` internamente.

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `MODEL_VERSION` | `v3` | Versão do artefato buscada no MinIO |
| `MINIO_ENDPOINT` | `minio:9000` | Endereço interno do MinIO |
| `MINIO_ACCESS_KEY` | `minioadmin` | Credencial MinIO |
| `MINIO_SECRET_KEY` | `minioadmin` | Credencial MinIO |
| `POSTGRES_HOST` | `postgres` | Host do banco de dados |
| `POSTGRES_DB` | `creditguard` | Nome do banco |
| `POSTGRES_USER` | `creditguard` | Usuário do banco |
| `POSTGRES_PASSWORD` | `creditguard` | Senha do banco |
| `OMP_NUM_THREADS` | `1` | Limita threads do LightGBM em container |
| `ANTHROPIC_API_KEY` | _(vazio)_ | Chave da API Anthropic para o agente de MÉDIO RISCO |
| `SLACK_WEBHOOK_URL` | _(vazio)_ | URL do Slack Incoming Webhook para ALTO RISCO |
| `CRM_WEBHOOK_URL` | _(vazio)_ | URL do webhook CRM/ERP para BAIXO RISCO |
| `SMTP_HOST` | _(vazio)_ | Host SMTP para notificação por e-mail (alternativo ao Slack) |
| `SMTP_FROM` | `creditguard@local` | Remetente do e-mail |
| `ANALISTA_EMAIL` | `analista@local` | Destinatário do alerta de ALTO RISCO |

Se `ANTHROPIC_API_KEY` não estiver configurada, o agente de IA exibe uma mensagem explicativa sem falhar. Se `SLACK_WEBHOOK_URL` e `SMTP_HOST` estiverem ausentes, a notificação de ALTO RISCO é logada como aviso sem interromper o fluxo.

---

## Verificando logs e predições registradas

```bash
# Logs em tempo real do container da aplicação
docker logs -f creditguard-ai

# Últimas 10 predições registradas no PostgreSQL
docker exec -it creditguard-postgres psql -U creditguard -d creditguard \
  -c "SELECT created_at, prediction, probability, model_version FROM predictions ORDER BY created_at DESC LIMIT 10;"
```

---

## Dependências principais

| Pacote | Versão | Motivo do pin |
|---|---|---|
| `scikit-learn` | `==1.7.0` | Compatibilidade com `preprocessor.joblib` gerado no treino |
| `lightgbm` | latest | Modelo em produção |
| `streamlit` | latest | Interface web |
| `httpx` | latest | Webhook CRM e Slack (ações automatizadas) |
| `anthropic` | latest | Agente de IA para MÉDIO RISCO |
| `minio` | latest | Carregamento de artefatos com fallback |
| `psycopg2-binary` | latest | Log de predições no PostgreSQL |
