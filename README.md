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
│   ├── train.py                    ← treinamento do modelo XGBoost
│   ├── predict.py                  ← serviço de inferência
│   ├── evaluation.ipynb            ← avaliação de métricas e curvas
│   ├── config.yaml                 ← hiperparâmetros e paths de artefatos
│   └── artifacts/
│       ├── xgb_balanced_model.joblib
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
# Treina o XGBoost Balanced e salva os artefatos em Model/artifacts/
python Model/train.py
```

Métricas esperadas ao final do treinamento:

| Métrica | Valor esperado |
|---|---|
| ROC-AUC | ~0.751 |
| Recall  | ~0.657 |

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