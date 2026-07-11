import io
import os

import joblib
import pandas as pd
from minio import Minio


def get_client() -> Minio:
    return Minio(
        os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
        secure=False,
    )


def load_csv(bucket: str, object_name: str) -> pd.DataFrame:
    response = get_client().get_object(bucket, object_name)
    return pd.read_csv(io.BytesIO(response.read()))


def save_csv(df: pd.DataFrame, bucket: str, object_name: str) -> None:
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    size = buf.tell()
    buf.seek(0)
    get_client().put_object(bucket, object_name, buf, length=size, content_type="text/csv")


def load_joblib(bucket: str, object_name: str):
    response = get_client().get_object(bucket, object_name)
    return joblib.load(io.BytesIO(response.read()))


def save_joblib(obj, bucket: str, object_name: str) -> None:
    buf = io.BytesIO()
    joblib.dump(obj, buf)
    size = buf.tell()
    buf.seek(0)
    get_client().put_object(
        bucket, object_name, buf, length=size, content_type="application/octet-stream"
    )
