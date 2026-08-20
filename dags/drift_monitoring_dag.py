"""DAG de monitoramento de data drift — CreditGuard AI.

Executa semanalmente. Compara a distribuição das features críticas em produção
(tabela predictions, últimos 7 dias) contra a distribuição do conjunto de treino
(Dados/abt.csv) via KS-test. Se KS-statistic > 0.1 em qualquer feature crítica,
aciona automaticamente a DAG creditguard_pipeline para retreinamento.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "creditguard",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

CRITICAL_FEATURES = [
    ("EXT_SOURCE_1", "ext_source_1"),
    ("EXT_SOURCE_2", "ext_source_2"),
    ("EXT_SOURCE_3", "ext_source_3"),
    ("AMT_CREDIT",   "amt_credit"),
    ("DAYS_BIRTH",   "days_birth"),
]
KS_THRESHOLD = 0.1
MIN_PREDICTIONS = 30


def check_data_drift(**context):
    """Executa KS-test comparando produção (7 dias) vs referência de treino."""
    import json
    import os
    import sys
    sys.path.insert(0, "/opt/airflow")

    import psycopg2
    from scipy import stats

    airflow_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow")
    abt_path = os.path.join(airflow_home, "Dados", "abt.csv")
    reference = {}

    if os.path.exists(abt_path):
        import pandas as pd
        df_ref = pd.read_csv(
            abt_path,
            usecols=[feat for feat, _ in CRITICAL_FEATURES],
            nrows=10000,
        )
        for feat_upper, _ in CRITICAL_FEATURES:
            if feat_upper in df_ref.columns:
                reference[feat_upper] = df_ref[feat_upper].dropna().tolist()
        print(f"[DRIFT] Referência: {abt_path} — {len(df_ref)} linhas carregadas")
    else:
        print(f"[DRIFT] Referência não encontrada em {abt_path} — encerrando.")
        context["ti"].xcom_push(key="drift_detected", value=False)
        return

    try:
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "postgres"),
            dbname=os.environ.get("POSTGRES_DB", "creditguard"),
            user=os.environ.get("POSTGRES_USER", "creditguard"),
            password=os.environ.get("POSTGRES_PASSWORD", "creditguard"),
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT ext_source_1, ext_source_2, ext_source_3, amt_credit, days_birth
            FROM predictions
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DRIFT] Erro ao conectar ao PostgreSQL: {e}")
        context["ti"].xcom_push(key="drift_detected", value=False)
        return

    if len(rows) < MIN_PREDICTIONS:
        print(f"[DRIFT] Apenas {len(rows)} predições — mínimo {MIN_PREDICTIONS}. Ignorando.")
        context["ti"].xcom_push(key="drift_detected", value=False)
        return

    prod = {
        "EXT_SOURCE_1": [r[0] for r in rows if r[0] is not None],
        "EXT_SOURCE_2": [r[1] for r in rows if r[1] is not None],
        "EXT_SOURCE_3": [r[2] for r in rows if r[2] is not None],
        "AMT_CREDIT":   [r[3] for r in rows if r[3] is not None],
        "DAYS_BIRTH":   [r[4] for r in rows if r[4] is not None],
    }

    report = {}
    drift_detected = False

    for feat_upper, _ in CRITICAL_FEATURES:
        ref_vals = reference.get(feat_upper, [])
        prod_vals = prod.get(feat_upper, [])
        if len(ref_vals) < 10 or len(prod_vals) < 10:
            print(f"[DRIFT] {feat_upper}: dados insuficientes (ref={len(ref_vals)}, prod={len(prod_vals)})")
            continue

        ks_stat, p_value = stats.ks_2samp(ref_vals, prod_vals)
        drifted = ks_stat > KS_THRESHOLD

        report[feat_upper] = {
            "ks_statistic": round(float(ks_stat), 4),
            "p_value": round(float(p_value), 4),
            "drift": drifted,
            "n_prod": len(prod_vals),
            "n_ref": len(ref_vals),
        }

        status = "DRIFT" if drifted else "OK"
        print(f"[DRIFT] {status} {feat_upper}: KS={ks_stat:.4f} p={p_value:.4f}")

        if drifted:
            drift_detected = True

    context["ti"].xcom_push(key="drift_report", value=report)
    context["ti"].xcom_push(key="drift_detected", value=drift_detected)

    print(f"\n[DRIFT] drift_detected={drift_detected}")
    print(json.dumps(report, indent=2))


def trigger_retraining_if_drift(**context):
    """Aciona creditguard_pipeline automaticamente se drift foi confirmado."""
    drift_detected = context["ti"].xcom_pull(
        key="drift_detected", task_ids="check_data_drift"
    )

    if not drift_detected:
        print("[DRIFT] Sem drift detectado — retreinamento não necessário.")
        return

    print("[DRIFT] Drift confirmado — acionando DAG creditguard_pipeline...")
    run_id = f"drift_trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        from airflow.api.client.local_client import Client
        c = Client(None, None)
        c.trigger_dag(dag_id="creditguard_pipeline", run_id=run_id)
        print(f"[DRIFT] DAG creditguard_pipeline acionada: run_id={run_id}")
    except Exception as e:
        print(f"[DRIFT] Erro ao acionar DAG de retreinamento: {e}")
        raise


with DAG(
    dag_id="creditguard_drift_monitoring",
    default_args=default_args,
    description="Monitoramento semanal de data drift — KS-test + retreinamento automático",
    schedule="@weekly",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["mlops", "monitoring", "drift"],
) as dag:

    t_check = PythonOperator(
        task_id="check_data_drift",
        python_callable=check_data_drift,
    )

    t_retrain = PythonOperator(
        task_id="trigger_retraining_if_drift",
        python_callable=trigger_retraining_if_drift,
    )

    t_check >> t_retrain
