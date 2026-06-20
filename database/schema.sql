-- =============================================================
-- Machine Failure Prediction — Fase 2
-- Schema do banco de dados (Supabase / PostgreSQL)
-- Autor: Silas Luiz Bom Fim
-- Versão: 2.0
-- =============================================================

-- Tabela principal: histórico de predições
-- Cada linha representa uma consulta feita à API
CREATE TABLE IF NOT EXISTS predictions (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    -- Dados de entrada da máquina
    machine_type        VARCHAR(1)    NOT NULL CHECK (machine_type IN ('L', 'M', 'H')),
    temperatura_ar      FLOAT         NOT NULL,
    temperatura_processo FLOAT        NOT NULL,
    velocidade_rotacao  FLOAT         NOT NULL,
    torque              FLOAT         NOT NULL,
    desgaste_ferramenta FLOAT         NOT NULL,

    -- Resultado da predição
    prediction          INTEGER       NOT NULL CHECK (prediction IN (0, 1)),
    probability_failure FLOAT         NOT NULL CHECK (probability_failure >= 0 AND probability_failure <= 1),
    risk_level          VARCHAR(8)    NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),

    -- Contexto da consulta
    source              VARCHAR(20)   NOT NULL DEFAULT 'single' CHECK (source IN ('single', 'batch')),
    batch_id            UUID          NULL  -- agrupa registros de uma mesma análise em lote
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_predictions_created_at  ON predictions (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_risk_level  ON predictions (risk_level);
CREATE INDEX IF NOT EXISTS idx_predictions_batch_id    ON predictions (batch_id) WHERE batch_id IS NOT NULL;

-- =============================================================
-- Descrição dos campos
-- =============================================================
COMMENT ON TABLE  predictions                    IS 'Histórico de todas as predições feitas pela API';
COMMENT ON COLUMN predictions.id                 IS 'Identificador único da predição (UUID gerado automaticamente)';
COMMENT ON COLUMN predictions.created_at         IS 'Data e hora da consulta (UTC)';
COMMENT ON COLUMN predictions.machine_type       IS 'Tipo do produto: L (Low), M (Medium), H (High)';
COMMENT ON COLUMN predictions.temperatura_ar     IS 'Temperatura do ar em Kelvin (290–320 K)';
COMMENT ON COLUMN predictions.temperatura_processo IS 'Temperatura do processo em Kelvin (300–320 K)';
COMMENT ON COLUMN predictions.velocidade_rotacao IS 'Velocidade de rotação em RPM (1000–3000)';
COMMENT ON COLUMN predictions.torque             IS 'Torque em Newton-metro (0–100 Nm)';
COMMENT ON COLUMN predictions.desgaste_ferramenta IS 'Desgaste acumulado da ferramenta em minutos (0–300)';
COMMENT ON COLUMN predictions.prediction         IS 'Resultado da predição: 0 = normal, 1 = falha';
COMMENT ON COLUMN predictions.probability_failure IS 'Probabilidade de falha entre 0 e 1';
COMMENT ON COLUMN predictions.risk_level         IS 'Nível de risco: LOW / MEDIUM / HIGH / CRITICAL';
COMMENT ON COLUMN predictions.source             IS 'Origem da consulta: single (individual) ou batch (lote)';
COMMENT ON COLUMN predictions.batch_id           IS 'UUID que agrupa todas as máquinas de uma análise em lote';
