# Comparação de Modelos

## Modelo 01 - Logistic Regression (Baseline)

### Resultados

- Accuracy: 91,92%
- Precision: 66,67%
- Recall: 0,04%
- F1-Score: 0,08%
- ROC-AUC: 0,693

### Matriz de Confusão

[[56537     1]
 [ 4963     2]]

### Interpretação

O modelo apresentou elevada Accuracy devido ao forte desbalanceamento da base.

Apesar disso, identificou apenas 2 clientes inadimplentes entre 4.965 presentes no conjunto de teste.

Na prática, o modelo classificou praticamente todos os clientes como adimplentes.

### Conclusão

O desempenho foi insuficiente para o objetivo de negócio, pois a capacidade de identificar clientes inadimplentes foi extremamente baixa.

---

## Modelo 02 - Logistic Regression (Balanced)

### Estratégia

Foi utilizado:

class_weight='balanced'

Objetivo:

Reduzir o impacto do desbalanceamento da variável alvo durante o treinamento.

### Resultados

- Accuracy: 64,62%
- Precision: 13,97%
- Recall: 65,58%
- F1-Score: 23,03%
- ROC-AUC: 0,705

### Matriz de Confusão

[[36486 20052]
 [ 1709  3256]]

### Interpretação

O modelo passou a identificar corretamente uma quantidade significativa de clientes inadimplentes.

Clientes inadimplentes corretamente identificados:

- 3.256

Clientes inadimplentes identificados pelo baseline:

- 2

O Recall aumentou significativamente:

- Baseline: 0,04%
- Balanced: 65,58%

### Conclusão

Apesar da redução da Accuracy, o modelo balanceado mostrou-se mais aderente ao objetivo de negócio, pois aumentou significativamente a capacidade de identificar clientes com risco de inadimplência.

---

## Conclusão Geral

A comparação demonstrou que a Accuracy não é uma métrica adequada para avaliação isolada deste problema.

O modelo baseline apresentou elevada Accuracy, mas falhou em identificar clientes inadimplentes.

O balanceamento das classes resultou em uma melhora expressiva no Recall e em um aumento do ROC-AUC, tornando o modelo mais alinhado ao propósito da solução CreditGuard AI.

### Melhor Modelo Até o Momento

Logistic Regression (Balanced)

Motivos:

- Melhor capacidade de identificar inadimplentes;
- Melhor Recall;
- Melhor ROC-AUC;
- Maior aderência ao problema de negócio.


## Conclusão da Comparação

O baseline apresentou 91,92% de Accuracy, porém identificou apenas 2 clientes inadimplentes no conjunto de teste.

Ao utilizar balanceamento das classes, a Accuracy foi reduzida para 64,62%, porém o Recall aumentou de 0,04% para 65,58%, permitindo identificar 3.256 clientes inadimplentes.

Como o principal objetivo do negócio é reduzir o risco de crédito e aumentar a capacidade de identificação de clientes inadimplentes, o modelo balanceado apresentou desempenho superior ao modelo baseline.

## Próxima Iteração de Modelagem

Após a avaliação da Regressão Logística tradicional e da versão balanceada, será realizado o teste de algoritmos mais robustos.

Próximo modelo:

- XGBoost (Extreme Gradient Boosting)

Objetivo:

Avaliar se técnicas de boosting conseguem melhorar a capacidade de discriminação dos clientes inadimplentes, mantendo ou elevando o desempenho observado nas métricas de ROC-AUC e Recall.