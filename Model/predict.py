import joblib
import pandas as pd


MODEL_PATH = "artifacts/xgb_balanced_model.joblib"


def load_model():
    return joblib.load(MODEL_PATH)


def predict(data):
    model = load_model()

    df = pd.DataFrame([data])

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]

    return {
        "prediction": int(prediction),
        "probability": float(probability)
    }