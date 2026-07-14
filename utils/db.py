import os
import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        dbname=os.environ.get("POSTGRES_DB", "creditguard"),
        user=os.environ.get("POSTGRES_USER", "creditguard"),
        password=os.environ.get("POSTGRES_PASSWORD", "creditguard"),
    )


def log_prediction(inputs: dict, result: dict, model_version: str = "v3") -> None:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO predictions (
                amt_income_total, amt_credit, amt_annuity, amt_goods_price,
                cnt_children, days_birth, days_employed,
                ext_source_1, ext_source_2, ext_source_3,
                prediction, probability, model_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                inputs.get("AMT_INCOME_TOTAL"),
                inputs.get("AMT_CREDIT"),
                inputs.get("AMT_ANNUITY"),
                inputs.get("AMT_GOODS_PRICE"),
                inputs.get("CNT_CHILDREN"),
                inputs.get("DAYS_BIRTH"),
                inputs.get("DAYS_EMPLOYED"),
                inputs.get("EXT_SOURCE_1"),
                inputs.get("EXT_SOURCE_2"),
                inputs.get("EXT_SOURCE_3"),
                result.get("prediction"),
                result.get("probability"),
                model_version,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass


def register_model(
    version: str,
    metrics: dict,
    description: str = "",
    artifact_bucket: str = "",
    artifact_path: str = "",
) -> None:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO model_registry (
                version, description,
                roc_auc, recall, precision_score, f1, accuracy,
                is_active, artifact_bucket, artifact_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (version) DO UPDATE SET
                description     = EXCLUDED.description,
                roc_auc         = EXCLUDED.roc_auc,
                recall          = EXCLUDED.recall,
                precision_score = EXCLUDED.precision_score,
                f1              = EXCLUDED.f1,
                accuracy        = EXCLUDED.accuracy,
                artifact_bucket = EXCLUDED.artifact_bucket,
                artifact_path   = EXCLUDED.artifact_path
            """,
            (
                version,
                description,
                metrics.get("roc_auc"),
                metrics.get("recall"),
                metrics.get("precision"),
                metrics.get("f1"),
                metrics.get("accuracy"),
                False,
                artifact_bucket,
                artifact_path,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass
