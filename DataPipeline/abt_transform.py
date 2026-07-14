"""
DataPipeline/abt_transform.py
==============================
Parte B do notebook oficial — seções 12 a 16:
  docs/HomeCredit_Comparacao_Completa_Modelos_Explicado.ipynb

Responsabilidade deste módulo
------------------------------
Carregar clean_data.csv (saída de data_sanitization.py), validar integridade
e persisti-lo como abt.csv — arquivo de entrada para Model/train.py.

Por que este módulo é um pass-through
--------------------------------------
O notebook oficial executa as etapas abaixo na Parte B. Por decisão de design,
cada etapa foi alocada no módulo mais adequado para evitar data leakage:

  Seção 12 — Merge application + bureau → ABT 307.511 × 185 features
      Implementado em: DataPipeline/data_sanitization.py → run_sanitization()
      Saída: clean_data.csv  (185 features brutas + TARGET, sem encoding)

  Seção 13 — X = abt.drop(["SK_ID_CURR", "TARGET"])  ·  y = abt["TARGET"]
      Implementado em: Model/train.py
      Resultado: X (307.511 × 185)  ·  y (307.511,)

  Seção 14 — train_test_split(test_size=0.20, random_state=42, stratify=y)
      Implementado em: Model/train.py
      Resultado: X_train (246.008 × 185)  ·  X_test (61.503 × 185)

  Seção 15 — ColumnTransformer
      Numéricas (169): SimpleImputer(strategy="median")
      Categóricas (16): SimpleImputer(strategy="most_frequent")
                        + OneHotEncoder(handle_unknown="ignore")
      Implementado em: Model/train.py
      Ajustado APENAS em X_train — evita data leakage entre treino e teste

  Seção 16 — preprocessor.fit_transform(X_train) → (246.008 × 309)
              preprocessor.transform(X_test)      → (61.503  × 309)
      Implementado em: Model/train.py
      Artefato gerado: Model/artifacts/preprocessor.joblib

Fluxo completo
--------------
  application_train.csv  ──┐
                            ├─► data_sanitization.py ─► clean_data.csv
  bureau.csv             ──┘                                │
                                                            ▼
                                                    abt_transform.py
                                                    (este módulo)
                                                            │
                                                            ▼
                                                        abt.csv
                                                            │
                                                            ▼
                                                     Model/train.py
                                              (split + ColumnTransformer
                                               + treinamento dos 5 modelos)

Shape esperado de clean_data.csv / abt.csv
------------------------------------------
  Linhas  : 307.511
  Colunas : 186  (185 features brutas sem encoding + TARGET)
  TARGET  : 0 = adimplente (91,93%)  ·  1 = inadimplente (8,07%)
"""

import pandas as pd
import yaml
from pathlib import Path

_EXPECTED_ROWS = 307_511
_EXPECTED_COLS = 186      # 185 features + TARGET


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

    # Validações de integridade
    assert "TARGET" in df.columns, "TARGET não encontrado em clean_data.csv."
    assert df.shape[0] > 0, "clean_data.csv está vazio."
    assert df.shape[0] == _EXPECTED_ROWS, (
        f"Número de linhas inesperado: {df.shape[0]} (esperado {_EXPECTED_ROWS}). "
        "Verifique se data_sanitization.py foi executado com a base completa."
    )
    assert df.shape[1] == _EXPECTED_COLS, (
        f"Número de colunas inesperado: {df.shape[1]} (esperado {_EXPECTED_COLS}). "
        "clean_data.csv deve conter 185 features brutas + TARGET, sem encoding."
    )

    print(f"abt_transform | linhas: {df.shape[0]:,}  colunas: {df.shape[1]}")
    print("  → Encoding e imputação em Model/train.py (ColumnTransformer fitado no X_train)")

    if use_minio:
        save_csv(df, mc["buckets"]["processed_data"], mc["objects"]["abt"])
        print(f"abt.csv → MinIO: {df.shape}")
    else:
        Path(cfg["paths"]["abt"]).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cfg["paths"]["abt"], index=False)
        print(f"abt.csv salvo em: {cfg['paths']['abt']}")

    return df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Pass-through: valida clean_data.csv e persiste como abt.csv."
    )
    parser.add_argument("--minio", action="store_true", help="Lê/escreve via MinIO")
    args = parser.parse_args()
    run_transform(use_minio=args.minio)
