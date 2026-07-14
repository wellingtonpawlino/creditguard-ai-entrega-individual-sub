import pandas as pd
import yaml
from pathlib import Path


def _load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_clean_data(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)


def run_transform(
    config_path: str = "DataPipeline/config.yaml",
    use_minio: bool = False,
) -> pd.DataFrame:
    cfg = _load_config(config_path)

    if use_minio:
        from utils.storage import load_csv, save_csv
        mc = cfg["minio"]
        df = load_csv(mc["buckets"]["processed_data"], mc["objects"]["clean_data"])
    else:
        df = load_clean_data(cfg["paths"]["clean_data"])

    assert "TARGET" in df.columns, "TARGET não encontrado em clean_data.csv."
    assert df.shape[0] > 0, "clean_data.csv está vazio."

    # Encoding e imputação são realizados pelo ColumnTransformer em Model/train.py,
    # ajustado exclusivamente nos dados de treino para evitar data leakage.
    # Este passo valida o clean_data e o persiste como abt.

    if use_minio:
        save_csv(df, mc["buckets"]["processed_data"], mc["objects"]["abt"])
        print(f"abt.csv → MinIO: {df.shape}")
    else:
        Path(cfg["paths"]["abt"]).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cfg["paths"]["abt"], index=False)
        print(f"abt.csv salvo: {df.shape}")

    return df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--minio", action="store_true", help="Lê/escreve via MinIO")
    args = parser.parse_args()
    run_transform(use_minio=args.minio)
