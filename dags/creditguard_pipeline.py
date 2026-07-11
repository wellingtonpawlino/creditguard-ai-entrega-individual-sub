import sys
sys.path.insert(0, "/opt/airflow")

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def check_raw_data():
    from pathlib import Path
    p = Path("Dados/raw/application_train.csv")
    if not p.exists():
        raise FileNotFoundError(
            f"Raw data não encontrado em {p.resolve()}. "
            "Baixe o dataset Home Credit Default Risk do Kaggle e extraia em Dados/raw/."
        )
    size_mb = p.stat().st_size / 1e6
    print(f"Raw data OK: {p}  ({size_mb:.1f} MB)")


def sanitize():
    from DataPipeline.data_sanitization import run_sanitization
    run_sanitization()


def transform():
    from DataPipeline.abt_transform import run_transform
    run_transform()


def train():
    from Model.train import run_training
    run_training()


with DAG(
    dag_id="creditguard_pipeline",
    description="Pipeline completo: sanitização → ABT → treino do modelo",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["creditguard"],
) as dag:

    t1 = PythonOperator(
        task_id="extract_data",
        python_callable=check_raw_data,
    )

    t2 = PythonOperator(
        task_id="data_sanitization",
        python_callable=sanitize,
    )

    t3 = PythonOperator(
        task_id="abt_transform",
        python_callable=transform,
    )

    t4 = PythonOperator(
        task_id="train_model",
        python_callable=train,
    )

    t1 >> t2 >> t3 >> t4
