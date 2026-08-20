#!/bin/bash
# Script de inicialização do PostgreSQL para o CreditGuard AI.
# Executado uma única vez pelo docker-entrypoint quando o volume está vazio.
# Arquivos .sh em /docker-entrypoint-initdb.d/ rodam com o usuário postgres.
set -e

# Cria o banco de dados do Airflow (metadados do serviço de orquestração).
# psql --dbname postgres garante que o CREATE DATABASE rode fora de qualquer
# transação (restrição do PostgreSQL).
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-'EOSQL'
    SELECT 'CREATE DATABASE airflow'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec
EOSQL

# Cria as tabelas do CreditGuard no banco 'creditguard' (POSTGRES_DB).
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-'EOSQL'
    CREATE TABLE IF NOT EXISTS predictions (
        id               SERIAL PRIMARY KEY,
        created_at       TIMESTAMP DEFAULT NOW(),

        amt_income_total FLOAT,
        amt_credit       FLOAT,
        amt_annuity      FLOAT,
        amt_goods_price  FLOAT,
        cnt_children     INTEGER,
        days_birth       INTEGER,
        days_employed    INTEGER,
        ext_source_1     FLOAT,
        ext_source_2     FLOAT,
        ext_source_3     FLOAT,

        prediction       INTEGER NOT NULL CHECK (prediction IN (0, 1)),
        probability      FLOAT   NOT NULL,

        model_version    VARCHAR(20)
    );

    CREATE INDEX IF NOT EXISTS idx_predictions_created_at
        ON predictions (created_at DESC);

    -- Migração não-destrutiva: ADD COLUMN IF NOT EXISTS é idempotente no PostgreSQL 9.6+
    ALTER TABLE predictions ADD COLUMN IF NOT EXISTS amt_goods_price FLOAT;
    ALTER TABLE predictions ADD COLUMN IF NOT EXISTS days_employed   INTEGER;

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
EOSQL
