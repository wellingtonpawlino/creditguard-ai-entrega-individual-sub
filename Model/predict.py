import io
import math
import os
import sys
import joblib
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PREPROCESSOR_PATH = "Model/artifacts/preprocessor.joblib"
MODEL_PATH        = "Model/artifacts/best_model.joblib"
FEATURES_PATH     = "Model/artifacts/features.joblib"

_preprocessor = None
_model        = None
_features     = None


def _log(msg):
    sys.stderr.write(f"[PREDICT] {msg}\n")
    sys.stderr.flush()


def _load_from_minio(object_name: str):
    try:
        from utils.storage import get_client
        version = os.environ.get("MODEL_VERSION", "v3")
        bucket = "model-artifacts"
        response = get_client().get_object(bucket, f"{version}/{object_name}")
        data = response.read()
        return joblib.load(io.BytesIO(data))
    except Exception as e:
        _log(f"minio: falhou ({type(e).__name__}: {e}) — usando fallback local")
        return None


def load_preprocessor():
    global _preprocessor
    if _preprocessor is None:
        obj = _load_from_minio("preprocessor.joblib")
        _preprocessor = obj if obj is not None else joblib.load(PREPROCESSOR_PATH)
        _log("load_preprocessor: ok")
    return _preprocessor


def load_model():
    global _model
    if _model is None:
        obj = _load_from_minio("best_model.joblib")
        _model = obj if obj is not None else joblib.load(MODEL_PATH)
        _log(f"load_model: ok — {type(_model)}")
    return _model


def load_features():
    global _features
    if _features is None:
        obj = _load_from_minio("features.joblib")
        _features = obj if obj is not None else joblib.load(FEATURES_PATH)
        _log(f"load_features: {len(_features)} colunas")
    return _features


def _safe_div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def _enrich_input(data: dict) -> dict:
    """Replica a engenharia de atributos de data_sanitization.py para o input do formulário.
    Features de bureau ficam ausentes e são imputadas pelo ColumnTransformer (mediana de treino)."""
    out = dict(data)

    out["CREDIT_INCOME_RATIO"] = _safe_div(out.get("AMT_CREDIT"), out.get("AMT_INCOME_TOTAL"))
    out["ANNUITY_INCOME_RATIO"] = _safe_div(out.get("AMT_ANNUITY"), out.get("AMT_INCOME_TOTAL"))
    out["CREDIT_ANNUITY_RATIO"] = _safe_div(out.get("AMT_CREDIT"), out.get("AMT_ANNUITY"))
    out["CREDIT_GOODS_RATIO"] = _safe_div(out.get("AMT_CREDIT"), out.get("AMT_GOODS_PRICE"))

    amt_goods = out.get("AMT_GOODS_PRICE")
    amt_credit = out.get("AMT_CREDIT")
    if amt_goods is not None and amt_credit is not None:
        out["DOWN_PAYMENT_VALUE"] = amt_goods - amt_credit

    days_birth = out.get("DAYS_BIRTH")
    if days_birth is not None:
        out["AGE_YEARS"] = -days_birth / 365.25

    days_emp = out.get("DAYS_EMPLOYED")
    if days_emp is not None:
        if days_emp == 365243:
            # Sentinela do dataset original: cliente sem vínculo empregatício ativo.
            # Reproduz o comportamento de data_sanitization.py (valor → NaN).
            out["EMPLOYED_YEARS"] = math.nan
            out["EMPLOYED_AGE_RATIO"] = math.nan
        else:
            out["EMPLOYED_YEARS"] = -days_emp / 365.25
            if out.get("AGE_YEARS") is not None:
                out["EMPLOYED_AGE_RATIO"] = _safe_div(out["EMPLOYED_YEARS"], out["AGE_YEARS"])

    return out


def predict(data: dict) -> dict:
    _log("predict: inicio")

    preprocessor = load_preprocessor()
    model = load_model()
    features = load_features()

    enriched = _enrich_input(data)
    _log(f"predict: {sum(v is not None for v in enriched.values())} features com valor")

    # DataFrame com todas as features brutas esperadas pelo preprocessor.
    # Colunas ausentes (ex: bureau) ficam None → imputadas com mediana do treino.
    df_input = pd.DataFrame([{col: enriched.get(col) for col in features}])

    X_processed = preprocessor.transform(df_input)

    prediction = int(model.predict(X_processed)[0])
    probability = float(model.predict_proba(X_processed)[0][1])

    _log(f"predict: pred={prediction} proba={probability:.4f}")
    return {"prediction": prediction, "probability": probability}
