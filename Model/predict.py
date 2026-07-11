import io
import os
import sys
import joblib
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

MODEL_PATH = "Model/artifacts/xgb_balanced_model.joblib"
FEATURES_PATH = "Model/artifacts/features.joblib"

_model = None
_features = None


def _load_from_minio(object_name: str):
    try:
        from utils.storage import get_client
        version = os.environ.get("MODEL_VERSION", "v1")
        bucket = "model-artifacts"
        response = get_client().get_object(bucket, f"{version}/{object_name}")
        return joblib.load(io.BytesIO(response.read()))
    except Exception:
        return None


def load_model():
    global _model
    if _model is None:
        obj = _load_from_minio("xgb_balanced_model.joblib")
        _model = obj if obj is not None else joblib.load(MODEL_PATH)
    return _model


def load_features():
    global _features
    if _features is None:
        obj = _load_from_minio("features.joblib")
        _features = obj if obj is not None else joblib.load(FEATURES_PATH)
    return _features


def predict(data):
    model = load_model()
    features = load_features()

    df = pd.DataFrame(0.0, index=[0], columns=features)

    for key, value in data.items():
        if key in df.columns:
            df.at[0, key] = value

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]

    return {
        "prediction": int(prediction),
        "probability": float(probability)
    }
