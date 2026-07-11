# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Visão Geral do Projeto

**ProScore Analytics — CreditGuard AI** é um sistema de predição de inadimplência para concessão de crédito em instituições financeiras. O projeto segue a metodologia **CRISP-DM** e usa o dataset público **Home Credit Default Risk** (Kaggle) como base de treinamento.

O objetivo central é prever a probabilidade de um cliente não honrar um empréstimo, classificando-o como **ALTO RISCO** ou **BAIXO RISCO** antes da concessão do crédito.

**Status atual:** ~55–60% concluído. Data Preparation e Modelagem estão finalizadas. Avaliação final e MLOps estão em andamento.

---

## Arquitetura da Solução

O sistema é dividido em três camadas independentes que se comunicam por meio de arquivos serializados:

```
DataPipeline/          →        Model/artifacts/         →         app/
(Jupyter Notebooks)           (arquivos .joblib)             (Streamlit)
Preparação dos dados       Modelo e lista de features       Interface web
```

### Camada 1 — DataPipeline

Responsável por todo o pré-processamento dos dados brutos até a ABT (Analytical Base Table) pronta para modelagem.

- Entrada: CSVs brutos em `Dados/raw/` (não versionados no git)
- Saída: ABT limpa em `Dados/abt.csv`
- Execução: via Jupyter Notebooks (`data_preparation.ipynb`)

### Camada 2 — Model

Responsável pelo treinamento e pela inferência.

- `Model/predict.py`: serviço de inferência. Carrega o modelo e a lista de features via `joblib`, monta o DataFrame com todas as features zeradas e preenche apenas as colunas fornecidas pelo caller.
- `Model/artifacts/xgb_balanced_model.joblib`: modelo XGBoost serializado (candidato a produção).
- `Model/artifacts/features.joblib`: lista das 30 features na ordem exata esperada pelo modelo.
- `Model/train.py`: placeholder para retreinamento (ainda não implementado).

### Camada 3 — App

Interface Streamlit que expõe o serviço de predição ao usuário final.

- `app/app.py`: importa `predict` de `Model/predict.py` via `sys.path.append("/app")`.
- Coleta 8 atributos do cliente, chama `predict()` e exibe a classificação com a probabilidade de inadimplência.
- A conversão de idade para `DAYS_BIRTH` é feita diretamente no app: `DAYS_BIRTH = -(idade * 365)`.

---

## Estrutura de Diretórios

```
proscore-creditguard-ai/
├── app/
│   ├── app.py                  # Interface Streamlit (ponto de entrada da aplicação)
│   ├── Dockerfile              # Imagem Python 3.12-slim, porta 8501
│   └── requirements.txt        # Dependências mínimas da app (streamlit, pandas, joblib, xgboost, scikit-learn, numpy)
├── Model/
│   ├── artifacts/
│   │   ├── xgb_balanced_model.joblib   # Modelo candidato a produção
│   │   └── features.joblib             # Lista de features na ordem correta
│   ├── predict.py              # Serviço de inferência (função predict())
│   ├── train.py                # Placeholder para retreinamento
│   ├── evaluation.ipynb        # Avaliação de modelos
│   └── config.yaml             # Placeholder de configuração
├── DataPipeline/
│   ├── data_preparation.ipynb  # Pipeline completo de preparação dos dados e construção da ABT
│   ├── exp_analysis.ipynb      # Análise exploratória
│   ├── abt_transform.py        # Placeholder
│   └── data_sanitization.py    # Placeholder
├── Dados/
│   ├── raw/                    # CSVs brutos do Home Credit (ignorados pelo git)
│   ├── clean_data.csv          # Dados após sanitização (ignorado pelo git)
│   └── abt.csv                 # ABT final pronta para modelagem (ignorado pelo git)
├── docs/                       # Documentação técnica das decisões do projeto
│   ├── data_preparation.md     # Investigações e decisões de tratamento de dados
│   ├── modeling_summary.md     # Resultados e comparativo de modelos
│   └── ...
├── MLOps/                      # Placeholder para infraestrutura MLOps (não implementado)
├── docker-compose.yml          # Sobe o serviço creditguard-app na porta 8501
└── requirements.txt            # Dependências completas para desenvolvimento (notebooks + ML)
```

---

## Fluxo de Dados

### Treinamento (offline)

```
Dados/raw/ (CSVs Home Credit)
    ↓  DataPipeline/data_preparation.ipynb
Investigações de qualidade → Tratamentos → Encoding → ABT V1 Final
    ↓
Dados/abt.csv (307.511 registros × 119 features + TARGET, 0 nulos)
    ↓  Model/evaluation.ipynb (treino + comparação de modelos)
Model/artifacts/xgb_balanced_model.joblib
Model/artifacts/features.joblib
```

### Inferência (online)

```
Usuário preenche formulário no Streamlit (8 atributos)
    ↓  app/app.py converte idade → DAYS_BIRTH
predict({"AMT_INCOME_TOTAL": ..., "EXT_SOURCE_1": ..., ...})
    ↓  Model/predict.py
load_features() → DataFrame com 30 colunas zeradas
Preenche apenas os campos fornecidos
load_model().predict() + predict_proba()
    ↓
{"prediction": 0|1, "probability": float}
    ↓  app/app.py
Exibe: ALTO RISCO / BAIXO RISCO + probabilidade + recomendação
```

---

## Como Executar Localmente

### Via Docker (recomendado)

```bash
docker-compose up --build
# Acesse: http://localhost:8501
```

O `docker-compose.yml` monta o contexto na raiz do projeto, copia tudo para `/app` dentro do container e executa `streamlit run app/app.py --server.address=0.0.0.0`.

### Execução manual

```bash
# Instalar dependências da app
pip install -r app/requirements.txt

# Rodar a aplicação
streamlit run app/app.py --server.address=0.0.0.0
```

### Ambiente de desenvolvimento (notebooks)

```bash
# Instalar dependências completas (inclui Jupyter, matplotlib, seaborn, scipy etc.)
pip install -r requirements.txt

# Abrir JupyterLab
jupyter lab
```

---

## Como Realizar Testes

Não existe suíte de testes automatizados no momento.

**Validação do serviço de predição** — teste manual direto em Python:

```python
import sys
sys.path.append(".")  # executar a partir da raiz do projeto
from Model.predict import predict

resultado = predict({
    "AMT_INCOME_TOTAL": 150000.0,
    "AMT_CREDIT": 300000.0,
    "AMT_ANNUITY": 25000.0,
    "CNT_CHILDREN": 0,
    "DAYS_BIRTH": -(35 * 365),
    "EXT_SOURCE_1": 0.50,
    "EXT_SOURCE_2": 0.50,
    "EXT_SOURCE_3": 0.50,
})
print(resultado)  # {"prediction": int, "probability": float}
```

**Avaliação do modelo** — executar `Model/evaluation.ipynb` com o ambiente de desenvolvimento instalado.

**Pipeline de dados** — executar `DataPipeline/data_preparation.ipynb` com os CSVs brutos em `Dados/raw/`.

---

## Decisões de Dados Não Óbvias

Estas decisões estão documentadas em `docs/data_preparation.md` e devem ser respeitadas em qualquer retrabalho:

| Variável | Decisão |
|---|---|
| `DAYS_EMPLOYED = 365243` | **Não é erro.** É um código especial presente em 18% da base. Clientes com esse valor têm taxa de inadimplência diferente (5,4% vs 8,66%). Deve ser preservado. |
| `EXT_SOURCE_1` (56,38% nulo) | A ausência em si é preditiva. Foram criadas flags `EXT_SOURCE_1_MISSING` e `EXT_SOURCE_3_MISSING` para preservar essa informação. |
| Variáveis Bureau (ex: `AMT_REQ_CREDIT_BUREAU_*`) | Nulos representam ausência de consulta, não dado faltante. Substituídos por `0`. |
| `OCCUPATION_TYPE` (~31% nulo) | Nulos preenchidos com a categoria `"UNKNOWN"` antes do encoding. |
| Variáveis imobiliárias (>68% nulo) | Avaliadas e mantidas com indicadores de ausência; remoção descartada pois a ausência é preditiva. |

---

## Modelo

| Modelo | ROC-AUC | Recall | Observação |
|---|---|---|---|
| Logistic Regression (baseline) | 0,693 | 0,04% | Recall praticamente nulo — inútil para o problema |
| **XGBoost Balanced** | **0,751** | **65,68%** | **Candidato a produção** |

O Recall é a métrica prioritária porque o custo de aprovar um inadimplente supera o custo de negar um bom pagador. O parâmetro `scale_pos_weight` do XGBoost é usado para lidar com o desbalanceamento (91,93% adimplentes / 8,07% inadimplentes).

Modelos ainda em avaliação: Random Forest e LightGBM.

---

## Convenções de Código

- **Python puro** em `Model/predict.py` e `app/app.py`; notebooks Jupyter para exploração e avaliação.
- O serviço `predict()` recebe um `dict` com nomes de colunas exatamente como estão em `features.joblib`. Qualquer chave desconhecida é ignorada silenciosamente.
- O modelo é carregado a cada chamada de `predict()` (sem cache em memória). Para uso em produção com alta carga, considere carregar o modelo uma vez no início da aplicação.
- `DAYS_BIRTH` é sempre negativo no dataset original (representa dias antes da data de referência). O app converte `idade * 365` para negativo antes de chamar `predict()`.

---

## Padrões de Desenvolvimento

- **Não remover os arquivos `.joblib` de `Model/artifacts/`** — são os artefatos do modelo candidato a produção.
- **Não alterar a ordem das features** em `features.joblib` — o XGBoost depende da ordem das colunas.
- Qualquer novo tratamento de dados deve ser documentado em `docs/data_preparation.md` seguindo o padrão: Problema → Evidências → Interpretação → Decisão → Status.
- Novos modelos devem ser comparados contra o XGBoost Balanced usando as métricas ROC-AUC e Recall na mesma base de teste.
- Os dados brutos em `Dados/raw/` não são versionados (`.gitignore`). Para reproduzir o pipeline, baixar o dataset Home Credit Default Risk do Kaggle.

---

## Instruções para Agentes Claude

- O ponto de entrada da aplicação é `app/app.py`. O ponto de entrada da inferência é `Model/predict.py`.
- Ao editar o serviço de predição, garantir que o DataFrame seja inicializado com **todas as features** de `features.joblib` zeradas antes de preencher os valores fornecidos — isso evita erros de shape com o modelo.
- O contexto do Docker começa na **raiz do projeto** (não dentro de `app/`). Por isso `app/Dockerfile` usa `COPY . .` e o CMD referencia `app/app.py`.
- A documentação de decisões técnicas fica em `docs/`. Consulte `docs/data_preparation.md` antes de modificar o pipeline de dados e `docs/modeling_summary.md` antes de alterar a lógica de modelagem.
- `MLOps/` é um placeholder vazio — não há nada implementado lá ainda.
- Ao sugerir melhorias de MLOps, considerar: cache do modelo em memória no Streamlit (`@st.cache_resource`), logging de predições, monitoramento de drift de dados.
