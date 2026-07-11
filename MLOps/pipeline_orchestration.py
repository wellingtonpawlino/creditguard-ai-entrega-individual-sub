"""
Pipeline de dados e treinamento — CreditGuard AI
=================================================

Executor manual do pipeline completo. Chama os módulos de sanitização,
transformação e treinamento em sequência, reutilizando a mesma lógica
executada pelo Apache Airflow em produção.

Orquestração em produção
------------------------
A orquestração principal em produção é realizada pelo Apache Airflow
através da DAG definida em dags/creditguard_pipeline.py.
O Airflow expõe interface web em http://localhost:8082 e permite
monitoramento, logs por task e retry automático.

Uso manual
----------
Execute a partir de qualquer diretório:

    python MLOps/pipeline_orchestration.py

Pré-requisito: dataset bruto presente em Dados/raw/application_train.csv
(baixar em https://www.kaggle.com/competitions/home-credit-default-risk)
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    print("=== CreditGuard AI — Pipeline Completo ===\n")

    print("[1/3] Sanitização dos dados...")
    from DataPipeline.data_sanitization import run_sanitization
    run_sanitization()

    print("\n[2/3] Transformação e construção da ABT...")
    from DataPipeline.abt_transform import run_transform
    run_transform()

    print("\n[3/3] Treinamento do modelo...")
    from Model.train import run_training
    run_training()

    print("\n=== Pipeline concluído com sucesso. ===")


if __name__ == "__main__":
    main()
