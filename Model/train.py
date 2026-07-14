import json
import time
import warnings
import pandas as pd
import yaml
import joblib
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

warnings.filterwarnings("ignore")


def _load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_abt(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)


def split_features_target(df: pd.DataFrame, target_col: str = "TARGET"):
    return df.drop(columns=[target_col]), df[target_col].astype(int)


def split_train_test(X, y, test_size: float, random_state: int):
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def build_preprocessor(X_train: pd.DataFrame) -> ColumnTransformer:
    categorical_cols = X_train.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = X_train.select_dtypes(exclude=["object", "category"]).columns.tolist()

    numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
    ])

    return ColumnTransformer([
        ("num", numeric_pipeline, numeric_cols),
        ("cat", categorical_pipeline, categorical_cols),
    ])


def _build_models(cfg: dict, scale_pos_weight: float) -> list:
    m = cfg["models"]
    return [
        ("Dummy", DummyClassifier(**m["dummy"])),
        ("Regressão Logística", LogisticRegression(**m["logistic_regression"])),
        ("Random Forest", RandomForestClassifier(**m["random_forest"])),
        ("XGBoost", XGBClassifier(
            **m["xgboost"],
            scale_pos_weight=scale_pos_weight,
            objective="binary:logistic",
            eval_metric="auc",
            verbosity=0,
        )),
        ("LightGBM", LGBMClassifier(**m["lightgbm"], verbosity=-1)),
    ]


def train_and_compare_models(X_train, y_train, X_test, y_test, cfg: dict):
    neg = int((y_train == 0).sum())
    pos = int((y_train == 1).sum())
    scale_pos_weight = neg / pos

    results = []
    trained_models = {}

    for name, model in _build_models(cfg, scale_pos_weight):
        print(f"Treinando {name}...")
        t0 = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - t0

        proba = model.predict_proba(X_test)[:, 1]
        pred = model.predict(X_test)

        row = {
            "Modelo": name,
            "ROC_AUC": float(roc_auc_score(y_test, proba)),
            "Average_Precision": float(average_precision_score(y_test, proba)),
            "Precision_Classe_1": float(precision_score(y_test, pred, zero_division=0)),
            "Recall_Classe_1": float(recall_score(y_test, pred, zero_division=0)),
            "F1_Classe_1": float(f1_score(y_test, pred, zero_division=0)),
            "Tempo_Treinamento_Segundos": round(elapsed, 2),
        }
        results.append(row)
        trained_models[name] = model
        print(f"  ROC-AUC: {row['ROC_AUC']:.4f}  Recall: {row['Recall_Classe_1']:.4f}")

    comparison_df = (
        pd.DataFrame(results)
        .sort_values("ROC_AUC", ascending=False)
        .reset_index(drop=True)
    )
    return comparison_df, trained_models


def save_artifacts(
    preprocessor,
    best_model,
    best_model_name: str,
    comparison_df: pd.DataFrame,
    best_row,
    feature_names: list,
    X_train,
    X_test,
    cfg: dict,
    use_minio: bool = False,
) -> None:
    if use_minio:
        from utils.storage import save_joblib
        mc = cfg["minio"]
        bucket = mc["bucket"]
        version = mc["version"]
        save_joblib(preprocessor, bucket, f"{version}/{mc['objects']['preprocessor']}")
        save_joblib(best_model, bucket, f"{version}/{mc['objects']['model']}")
        save_joblib(feature_names, bucket, f"{version}/{mc['objects']['features']}")
        print(f"Artefatos → MinIO ({bucket}/{version}/)")
    else:
        arts = cfg["artifacts"]
        Path(arts["model"]).parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(preprocessor, arts["preprocessor"])
        joblib.dump(best_model, arts["model"])
        joblib.dump(feature_names, arts["features"])
        comparison_df.to_csv(arts["comparison"], index=False)

        metadata = {
            "melhor_modelo": best_model_name,
            "roc_auc": float(best_row["ROC_AUC"]),
            "average_precision": float(best_row["Average_Precision"]),
            "precision_classe_1": float(best_row["Precision_Classe_1"]),
            "recall_classe_1": float(best_row["Recall_Classe_1"]),
            "f1_classe_1": float(best_row["F1_Classe_1"]),
            "n_features_encoded": len(preprocessor.get_feature_names_out()),
            "random_state": cfg["split"]["random_state"],
            "linhas_treino": len(X_train),
            "linhas_teste": len(X_test),
        }
        with open(arts["metadata"], "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)

        print(f"\nArtefatos salvos em Model/artifacts/:")
        print(f"  preprocessor.joblib")
        print(f"  best_model.joblib  ({best_model_name})")
        print(f"  features.joblib    ({len(feature_names)} features brutas)")
        print(f"  comparacao_modelos.csv")
        print(f"  metadata_modelo.json")


def run_training(
    pipeline_config_path: str = "DataPipeline/config.yaml",
    model_config_path: str = "Model/config.yaml",
    use_minio: bool = False,
    use_db: bool = False,
) -> dict:
    pipeline_cfg = _load_config(pipeline_config_path)
    model_cfg = _load_config(model_config_path)

    if use_minio:
        from utils.storage import load_csv
        mc = pipeline_cfg["minio"]
        df = load_csv(mc["buckets"]["processed_data"], mc["objects"]["abt"])
    else:
        df = load_abt(pipeline_cfg["paths"]["abt"])

    X, y = split_features_target(df)
    X_train, X_test, y_train, y_test = split_train_test(
        X, y,
        test_size=model_cfg["split"]["test_size"],
        random_state=model_cfg["split"]["random_state"],
    )
    print(f"Treino: {X_train.shape} | Teste: {X_test.shape}")

    print("Ajustando pré-processador (ColumnTransformer)...")
    preprocessor = build_preprocessor(X_train)
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    print(f"Features após encoding: {X_train_proc.shape[1]}")

    comparison_df, trained_models = train_and_compare_models(
        X_train_proc, y_train, X_test_proc, y_test, model_cfg
    )

    print("\nComparação de modelos (por ROC-AUC):")
    cols = ["Modelo", "ROC_AUC", "Recall_Classe_1", "Precision_Classe_1", "Tempo_Treinamento_Segundos"]
    print(comparison_df[cols].to_string(index=False))

    best_row = comparison_df.iloc[0]
    best_model_name = best_row["Modelo"]
    best_model = trained_models[best_model_name]
    print(f"\nMelhor modelo: {best_model_name} (ROC-AUC = {best_row['ROC_AUC']:.4f})")

    save_artifacts(
        preprocessor, best_model, best_model_name, comparison_df, best_row,
        X_train.columns.tolist(), X_train, X_test, model_cfg, use_minio=use_minio,
    )

    if use_db:
        from utils.db import register_model
        mc = model_cfg.get("minio", {})
        version = mc.get("version", "v3")
        register_model(
            version=version,
            metrics={
                "roc_auc": float(best_row["ROC_AUC"]),
                "recall": float(best_row["Recall_Classe_1"]),
                "precision": float(best_row["Precision_Classe_1"]),
            },
            description=best_model_name,
            artifact_bucket=mc.get("bucket", "model-artifacts"),
            artifact_path=f"{version}/{mc.get('objects', {}).get('model', 'best_model.joblib')}",
        )
        print(f"Modelo registrado no PostgreSQL: versão {version}")

    return {
        "roc_auc": float(best_row["ROC_AUC"]),
        "recall": float(best_row["Recall_Classe_1"]),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--minio", action="store_true", help="Lê/escreve via MinIO")
    parser.add_argument("--db", action="store_true", help="Registra o modelo no PostgreSQL")
    args = parser.parse_args()
    run_training(use_minio=args.minio, use_db=args.db)
