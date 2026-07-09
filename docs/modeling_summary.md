# Modeling Summary

## Projeto

**ProScore Analytics**

## Solução

**CreditGuard AI**

## Objetivo

Prever a probabilidade de inadimplência de clientes antes da concessão de crédito utilizando técnicas de Machine Learning.

---

# Contexto

Durante a etapa de Data Preparation foi construída uma ABT (*Analytical Base Table*) contendo atributos considerados relevantes para análise de risco de crédito.

## Características da ABT

- 307.511 registros
- 30 variáveis
- 0 valores nulos
- Variável alvo: `TARGET`

### TARGET

**TARGET = 0**

Cliente adimplente.

**TARGET = 1**

Cliente inadimplente.

### Distribuição

- Adimplentes: 91,93%
- Inadimplentes: 8,07%

A base apresenta forte desbalanceamento, característica comum em problemas de risco de crédito.

---

# Objetivo da Modelagem

Construir modelos capazes de identificar clientes com maior probabilidade de inadimplência.

## Métricas Utilizadas

- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC

A avaliação dos modelos considerou múltiplas métricas de classificação.

Devido ao forte desbalanceamento da variável TARGET (8,07% de inadimplentes), a métrica **Recall** recebeu atenção especial durante a análise, pois representa a capacidade do modelo em identificar clientes potencialmente inadimplentes.

A métrica **ROC-AUC** foi utilizada para avaliar a capacidade geral de discriminação dos modelos.

---

# Modelo 01 - Logistic Regression (Baseline)

## Objetivo

Estabelecer uma linha de base para comparação com modelos futuros.

## Resultados

| Métrica | Valor |
|----------|--------:|
| Accuracy | 91,92% |
| Precision | 66,67% |
| Recall | 0,04% |
| F1-Score | 0,08% |
| ROC-AUC | 0,693 |

## Matriz de Confusão

```text
[[56537     1]
 [ 4963     2]]


Modelo Candidato para Produção
Até o momento, o modelo XGBoost Balanced apresentou o melhor equilíbrio entre capacidade de discriminação e identificação de clientes inadimplentes.
Resultados obtidos:

Recall: 65,68%
ROC-AUC: 0,751

Considerando o objetivo do CreditGuard AI de reduzir a concessão de crédito para clientes com alta probabilidade de inadimplência, a métrica Recall foi priorizada na tomada de decisão.
Dessa forma, o XGBoost Balanced é atualmente o principal candidato para implantação em produção, permanecendo sujeito à comparação final com os modelos Random Forest e LightGBM ainda em avaliação pela equipe.