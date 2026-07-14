# Model — CreditGuard AI

## Descrição do Projeto

O CreditGuard AI é um sistema de predição de inadimplência desenvolvido pela ProScore Analytics para apoiar instituições financeiras na concessão de crédito com maior segurança. O modelo utiliza dados financeiros, cadastrais e comportamentais do cliente para estimar a probabilidade de não pagamento antes da aprovação do crédito.

---

## Objetivo de Negócio

Instituições financeiras enfrentam o desafio permanente de equilibrar crescimento de carteira e controle de risco. A aprovação de clientes inadimplentes gera perdas financeiras diretas; critérios excessivamente restritivos bloqueiam boas oportunidades.

O objetivo é classificar cada solicitante em três níveis de risco — **BAIXO RISCO**, **MÉDIO RISCO** ou **ALTO RISCO** — antes da concessão, reduzindo a taxa de inadimplência da carteira sem comprometer o volume de aprovações.

| Classificação | Probabilidade | Ação recomendada |
|---|---|---|
| 🟢 BAIXO RISCO | < 30% | Aprovação automática recomendada |
| 🟡 MÉDIO RISCO | 30% – 69% | Análise complementar recomendada |
| 🔴 ALTO RISCO | ≥ 70% | Revisão manual obrigatória |

A métrica prioritária é o **Recall**: o custo de aprovar um inadimplente (perda financeira) supera o custo de negar um bom pagador (perda de receita).

---

## Metodologia

O projeto segue a metodologia **CRISP-DM**:

1. **Business Understanding** — definição do problema de risco de crédito e da métrica prioritária (Recall)
2. **Data Understanding** — análise exploratória do dataset Home Credit Default Risk (`exp_analysis.ipynb` em DataPipeline/)
3. **Data Preparation** — sanitização, tratamento de nulos, feature engineering e encoding (`data_preparation.ipynb` em DataPipeline/)
4. **Modeling** — treinamento comparativo de 5 modelos com `class_weight="balanced"` / `scale_pos_weight` para lidar com o desbalanceamento de classes (`train.py`)
5. **Evaluation** — avaliação de métricas ROC-AUC, Recall, Precision, F1 e análise de importância de features (`evaluation.ipynb`)
6. **Deployment** — serving via Streamlit containerizado com Docker Compose

**Dataset:** Home Credit Default Risk (Kaggle) — 307.511 registros, 185 features brutas (sem encoding), TARGET binário (0 = adimplente, 1 = inadimplente). Desbalanceamento: 91,93% adimplentes / 8,07% inadimplentes (razão ≈ 11,4:1).

---

## Comparação de Modelos (v3)

Cinco modelos foram treinados e comparados na mesma base de teste (`test_size=0.20`, `random_state=42`, `stratify=y`).

| Modelo | ROC-AUC | Recall | Precision | F1 | Tempo (s) |
|---|---|---|---|---|---|
| **LightGBM** | **0,7778** | **65,82%** | **18,90%** | **29,37%** | **7,2** |
| XGBoost | 0,7763 | 66,24% | 18,66% | 29,12% | 9,2 |
| Random Forest | 0,7470 | 50,01% | 20,01% | 28,58% | 36,6 |
| Regressão Logística | 0,6694 | 63,32% | 12,62% | 21,04% | 2.278 |
| Dummy | 0,5000 | 0,00% | 0,00% | 0,00% | 0,01 |

O LightGBM foi selecionado para produção por apresentar o maior ROC-AUC (0,7778) com tempo de treino competitivo (7,2 s). Usa crescimento folha-a-folha (`num_leaves=63`) com GOSS e EFB. O parâmetro `class_weight="balanced"` (LightGBM, RF, LR) e `scale_pos_weight` (XGBoost) compensam o desbalanceamento de classes.

---

## Modelo em Produção

**LightGBM v3** — `Model/artifacts/best_model.joblib`

| Métrica | Valor |
|---|---|
| ROC-AUC | 0,7778 |
| Recall | 65,82% |
| Precision | 18,90% |
| F1 | 29,37% |
| Average Precision | 27,68% |
| Features brutas | 185 |
| Features após encoding (ColumnTransformer) | 309 |
| Linhas de treino | 246.008 |
| Linhas de teste | 61.503 |

---

## Pré-processamento (ColumnTransformer v3)

O ColumnTransformer é ajustado **exclusivamente no X_train** para evitar data leakage.

| Tipo | Colunas | Transformação |
|---|---|---|
| Numéricas | 169 | `SimpleImputer(strategy="median")` |
| Categóricas | 16 | `SimpleImputer(strategy="most_frequent")` + `OneHotEncoder(handle_unknown="ignore")` |
| **Total encoded** | **309** | 169 numéricas + 140 dummies |

Artefato: `Model/artifacts/preprocessor.joblib`

---

## Artefatos

```
Model/artifacts/
├── best_model.joblib          ← LightGBM v3 em produção (ROC-AUC 0,7778)
├── preprocessor.joblib        ← ColumnTransformer v3 (fitted no X_train)
├── features.joblib            ← lista das 185 features brutas na ordem exata
├── all_models.joblib          ← 5 modelos treinados (Dummy, LR, RF, XGB, LGBM)
├── predictions_test.joblib    ← probabilidades e predições no conjunto de teste
├── comparacao_modelos.csv     ← tabela comparativa de métricas dos 5 modelos
└── metadata_modelo.json       ← métricas de produção (lidas pelo app dinamicamente)
```

**Não remover nem substituir** `best_model.joblib`, `preprocessor.joblib` e `features.joblib` — são os artefatos v3 validados em produção. A ordem das colunas em `features.joblib` é contrato com o ColumnTransformer.

---

## Como Treinar o Modelo

### Pré-requisitos

1. Dataset `Dados/abt.csv` gerado pelo pipeline de dados (ver `DataPipeline/`)
2. Dependências instaladas:

```bash
pip install -r requirements.txt
```

### Executar treinamento

A partir da **raiz do projeto**:

```bash
python Model/train.py
```

Saída esperada:
```
Treino: (246008, 309) | Teste: (61503, 309)
[LightGBM] → ROC-AUC: 0.7778  Recall: 0.6582  Precision: 0.1890  F1: 0.2937  Tempo: 7.2s
Melhor modelo: LightGBM
Artefatos salvos em Model/artifacts/
```

### Opções avançadas

```bash
# Lê ABT do MinIO e salva artefatos no MinIO (requer stack MLOps ativa)
python Model/train.py --minio

# Registra o modelo no PostgreSQL após o treino
python Model/train.py --db

# Ambos
python Model/train.py --minio --db
```

### Avaliar o modelo

```bash
jupyter lab Model/evaluation.ipynb
```

O notebook carrega os artefatos existentes (`all_models.joblib`, `predictions_test.joblib`), recria o split de teste deterministicamente (`random_state=42`) e calcula métricas, curvas ROC, matrizes de confusão e importância de features — **sem retreinar**.

---

## Serviço de Inferência

`Model/predict.py` expõe a função `predict(data: dict) -> dict`:

```python
import sys
sys.path.append(".")  # executar da raiz do projeto
from Model.predict import predict

resultado = predict({
    "AMT_INCOME_TOTAL": 360000.0,
    "AMT_CREDIT":       80000.0,
    "AMT_GOODS_PRICE":  80000.0,
    "CNT_CHILDREN":     0,
    "DAYS_BIRTH":       -(48 * 365),
    "DAYS_EMPLOYED":    -(15 * 365),
    "EXT_SOURCE_1":     0.88,
    "EXT_SOURCE_2":     0.92,
    "EXT_SOURCE_3":     0.90,
})
# {"prediction": 0, "probability": ~0.07}  → BAIXO RISCO
```

O serviço:
1. Chama `_enrich_input()` para calcular as features derivadas (mesma lógica de `create_application_features()` em `data_sanitization.py`)
2. Inicializa DataFrame com todas as **185 features brutas** como `None`
3. Preenche os campos fornecidos — ausentes chegam como `None` ao ColumnTransformer e são imputados com mediana do treino
4. Aplica `preprocessor.transform()` → 309 features encoded
5. Retorna `best_model.predict_proba()` como `{"prediction": 0|1, "probability": float}`

**Cenários validados em produção:**

| Cenário | Probabilidade | Classificação |
|---|---|---|
| Renda 360k · Crédito 80k · Idade 48 · Emprego 15a · Scores 0,88/0,92/0,90 | ~7% | 🟢 BAIXO RISCO |
| Renda 72k · Crédito 180k · Idade 30 · Emprego 2a · Scores 0,45/0,48/0,52 | ~53% | 🟡 MÉDIO RISCO |
| Renda 28,8k · Crédito 450k · Idade 23 · Emprego 0a · Scores 0,05/0,08/0,06 | ~89% | 🔴 ALTO RISCO |
