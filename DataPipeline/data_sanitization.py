import pandas as pd
import numpy as np
import yaml
from pathlib import Path


def _load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_raw_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)


def safe_divide(a: pd.Series, b: pd.Series) -> pd.Series:
    return a / b.replace(0, np.nan)


def create_application_features(df: pd.DataFrame) -> pd.DataFrame:
    """Razões financeiras e variáveis temporais a partir de application_train.csv."""
    out = df.copy()

    out["CREDIT_INCOME_RATIO"] = safe_divide(out["AMT_CREDIT"], out["AMT_INCOME_TOTAL"])
    out["ANNUITY_INCOME_RATIO"] = safe_divide(out["AMT_ANNUITY"], out["AMT_INCOME_TOTAL"])
    out["CREDIT_ANNUITY_RATIO"] = safe_divide(out["AMT_CREDIT"], out["AMT_ANNUITY"])
    out["CREDIT_GOODS_RATIO"] = safe_divide(out["AMT_CREDIT"], out["AMT_GOODS_PRICE"])
    out["DOWN_PAYMENT_VALUE"] = out["AMT_GOODS_PRICE"] - out["AMT_CREDIT"]
    out["AGE_YEARS"] = -out["DAYS_BIRTH"] / 365.25

    # DAYS_EMPLOYED = 365243 é código especial (aposentado/sem emprego), não erro.
    employed_days = out["DAYS_EMPLOYED"].replace(365243, np.nan)
    out["EMPLOYED_YEARS"] = -employed_days / 365.25
    out["EMPLOYED_AGE_RATIO"] = safe_divide(out["EMPLOYED_YEARS"], out["AGE_YEARS"])

    out.replace([np.inf, -np.inf], np.nan, inplace=True)
    return out


def create_bureau_features(df: pd.DataFrame) -> pd.DataFrame:
    """Indicadores e razões financeiras a partir de bureau.csv (nível crédito)."""
    out = df.copy()

    out["DEBT_CREDIT_RATIO"] = safe_divide(out["AMT_CREDIT_SUM_DEBT"], out["AMT_CREDIT_SUM"])
    out["OVERDUE_CREDIT_RATIO"] = safe_divide(out["AMT_CREDIT_SUM_OVERDUE"], out["AMT_CREDIT_SUM"])
    out["IS_ACTIVE"] = out["CREDIT_ACTIVE"].eq("Active").astype(int)
    out["IS_CLOSED"] = out["CREDIT_ACTIVE"].eq("Closed").astype(int)
    out["IS_BAD_DEBT"] = out["CREDIT_ACTIVE"].eq("Bad debt").astype(int)

    out.replace([np.inf, -np.inf], np.nan, inplace=True)
    return out


_BUREAU_AGG_MAP = {
    "SK_ID_BUREAU": ["count"],
    "DAYS_CREDIT": ["min", "max", "mean"],
    "CREDIT_DAY_OVERDUE": ["max", "mean"],
    "DAYS_CREDIT_ENDDATE": ["min", "max", "mean"],
    "DAYS_ENDDATE_FACT": ["min", "max", "mean"],
    "AMT_CREDIT_MAX_OVERDUE": ["max", "mean"],
    "CNT_CREDIT_PROLONG": ["sum", "mean"],
    "AMT_CREDIT_SUM": ["sum", "mean", "max"],
    "AMT_CREDIT_SUM_DEBT": ["sum", "mean", "max"],
    "AMT_CREDIT_SUM_LIMIT": ["sum", "mean"],
    "AMT_CREDIT_SUM_OVERDUE": ["sum", "mean", "max"],
    "DAYS_CREDIT_UPDATE": ["min", "max", "mean"],
    "AMT_ANNUITY": ["sum", "mean", "max"],
    "DEBT_CREDIT_RATIO": ["mean", "max"],
    "OVERDUE_CREDIT_RATIO": ["mean", "max"],
    "IS_ACTIVE": ["sum", "mean"],
    "IS_CLOSED": ["sum", "mean"],
    "IS_BAD_DEBT": ["sum", "mean"],
}


def aggregate_bureau(bureau_features: pd.DataFrame) -> pd.DataFrame:
    """Resume vários créditos por cliente (SK_ID_CURR) em uma linha:
    agregações numéricas + contagem por status + contagem pelos 10 tipos mais comuns."""
    agg_map = {
        col: funcs
        for col, funcs in _BUREAU_AGG_MAP.items()
        if col in bureau_features.columns
    }

    bureau_agg = bureau_features.groupby("SK_ID_CURR").agg(agg_map)
    bureau_agg.columns = [
        "BUREAU_" + "_".join(col).upper()
        for col in bureau_agg.columns.to_flat_index()
    ]
    bureau_agg = bureau_agg.reset_index()

    status_counts = pd.crosstab(bureau_features["SK_ID_CURR"], bureau_features["CREDIT_ACTIVE"])
    status_counts.columns = [
        "BUREAU_STATUS_" + str(col).upper().replace(" ", "_") + "_COUNT"
        for col in status_counts.columns
    ]
    status_counts = status_counts.reset_index()

    top_credit_types = bureau_features["CREDIT_TYPE"].value_counts().head(10).index
    type_filtered = bureau_features.loc[
        bureau_features["CREDIT_TYPE"].isin(top_credit_types),
        ["SK_ID_CURR", "CREDIT_TYPE"],
    ]
    type_counts = pd.crosstab(type_filtered["SK_ID_CURR"], type_filtered["CREDIT_TYPE"])
    type_counts.columns = [
        "BUREAU_TYPE_" + str(col).upper().replace(" ", "_").replace("/", "_") + "_COUNT"
        for col in type_counts.columns
    ]
    type_counts = type_counts.reset_index()

    bureau_customer = (
        bureau_agg
        .merge(status_counts, on="SK_ID_CURR", how="left")
        .merge(type_counts, on="SK_ID_CURR", how="left")
    )
    return bureau_customer


def run_sanitization(
    config_path: str = "DataPipeline/config.yaml",
    use_minio: bool = False,
) -> pd.DataFrame:
    cfg = _load_config(config_path)

    if use_minio:
        from utils.storage import load_csv, save_csv
        mc = cfg["minio"]
        application = load_csv(mc["buckets"]["raw_data"], mc["objects"]["raw_data"])
        bureau = load_csv(mc["buckets"]["raw_data"], mc["objects"]["bureau_data"])
    else:
        application = load_raw_data(cfg["paths"]["raw_data"])
        bureau = load_raw_data(cfg["paths"]["bureau_data"])

    print(f"application_train: {application.shape} | bureau: {bureau.shape}")

    application_features = create_application_features(application)
    bureau_features = create_bureau_features(bureau)
    bureau_customer = aggregate_bureau(bureau_features)

    df = application_features.merge(
        bureau_customer, on="SK_ID_CURR", how="left", validate="one_to_one"
    )
    assert len(df) == len(application_features), "Merge alterou o número de linhas."

    df = df.drop(columns=["SK_ID_CURR"])

    if use_minio:
        save_csv(df, mc["buckets"]["processed_data"], mc["objects"]["clean_data"])
        print(f"clean_data.csv → MinIO: {df.shape}")
    else:
        Path(cfg["paths"]["clean_data"]).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cfg["paths"]["clean_data"], index=False)
        print(f"clean_data.csv salvo: {df.shape}")

    return df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--minio", action="store_true", help="Lê/escreve via MinIO")
    args = parser.parse_args()
    run_sanitization(use_minio=args.minio)
