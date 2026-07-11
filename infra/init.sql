CREATE TABLE IF NOT EXISTS predictions (
    id               SERIAL PRIMARY KEY,
    created_at       TIMESTAMP DEFAULT NOW(),

    amt_income_total FLOAT,
    amt_credit       FLOAT,
    amt_annuity      FLOAT,
    cnt_children     INTEGER,
    days_birth       INTEGER,
    ext_source_1     FLOAT,
    ext_source_2     FLOAT,
    ext_source_3     FLOAT,

    prediction       INTEGER,
    probability      FLOAT,

    model_version    VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS model_registry (
    id               SERIAL PRIMARY KEY,
    registered_at    TIMESTAMP DEFAULT NOW(),
    version          VARCHAR(20) UNIQUE,
    description      TEXT,

    roc_auc          FLOAT,
    recall           FLOAT,
    precision_score  FLOAT,
    f1               FLOAT,
    accuracy         FLOAT,

    is_active        BOOLEAN DEFAULT FALSE,

    artifact_bucket  VARCHAR(100),
    artifact_path    VARCHAR(200)
);
