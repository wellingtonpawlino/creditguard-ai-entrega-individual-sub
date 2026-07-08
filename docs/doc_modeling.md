
# Modeling

## Modelo Baseline

Algoritmo:

- Logistic Regression

Justificativa:

A Regressão Logística é amplamente utilizada em problemas de Credit Scoring devido à sua simplicidade, interpretabilidade e capacidade de fornecer probabilidades de inadimplência.

Objetivo:

Estabelecer uma linha de base de desempenho para comparação com modelos mais complexos.



## Modelo Baseline - Logistic Regression

### Resultado

- Accuracy: 91,92%
- Precision: 66,67%
- Recall: 0,04%
- F1-Score: 0,08%
- ROC-AUC: 0,693

### Interpretação

Apesar da elevada Accuracy, o modelo apresentou Recall muito baixo para a classe de inadimplentes.

Esse comportamento era esperado devido ao forte desbalanceamento da base, onde apenas 8,07% dos clientes pertencem à classe positiva (inadimplência).

A métrica ROC-AUC apresentou resultado de 0,693, indicando que o modelo possui capacidade de discriminação superior ao acaso e estabelece uma linha de base válida para comparação com modelos futuros.

### Conclusão

O modelo baseline demonstrou potencial preditivo, porém necessita estratégias adicionais para melhorar a identificação de clientes inadimplentes.


## Avaliação do Modelo Baseline

### Matriz de Confusão

[[56537     1]
 [ 4963     2]]

### Interpretação

O modelo apresentou elevada Accuracy devido ao desbalanceamento da base.

Entretanto, a identificação da classe inadimplente foi extremamente limitada.

Dos 4.965 clientes inadimplentes presentes no conjunto de teste, apenas 2 foram corretamente identificados.

### Conclusão

O modelo baseline estabelece uma referência inicial de desempenho, porém não é adequado para uso operacional sem estratégias adicionais para melhoria da detecção de inadimplentes.