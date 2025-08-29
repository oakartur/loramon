#!/usr/bin/env bash
set -euo pipefail

DB_NAME="databridge"
API_ROLE="loramon"
TIMESCALE_JOB_INTERVAL="1 min"
PSQL="sudo -u postgres psql -X -v ON_ERROR_STOP=1 -d $DB_NAME"

echo "==[F0] Procurando tabelas com payload jsonb = possível fonte bruta =="
$PSQL -c "
SELECT table_schema, table_name
FROM information_schema.columns
WHERE column_name='payload' AND data_type='jsonb'
ORDER BY 1,2;
"

# Preferimos ingest.readings; se não houver, pegamos a primeira com payload
PAYLOAD_SRC=$($PSQL -tA -c "
WITH pref AS (
  SELECT 'ingest' AS table_schema, 'readings' AS table_name
  WHERE EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='ingest' AND table_name='readings'
      AND column_name='payload' AND data_type='jsonb'
  )
),
fallback AS (
  SELECT table_schema, table_name
  FROM information_schema.columns
  WHERE column_name='payload' AND data_type='jsonb'
  GROUP BY table_schema, table_name
  ORDER BY table_schema, table_name
  LIMIT 1
)
SELECT table_schema||'.'||table_name
FROM (SELECT * FROM pref UNION ALL SELECT * FROM fallback) s
LIMIT 1;
")

if [[ -z "${PAYLOAD_SRC}" ]]; then
  echo ">> [F0] Nenhuma fonte com payload jsonb encontrada. F2 criará estrutura vazia."
else
  echo ">> [F0] Fonte com payload: ${PAYLOAD_SRC}"
fi

SRC_SCHEMA="${PAYLOAD_SRC%%.*}"
SRC_TABLE="${PAYLOAD_SRC##*.}"

# Coleta lista de colunas da fonte (se existir)
COLS=$($PSQL -tA -c "
SELECT string_agg(column_name, ',')
FROM information_schema.columns
WHERE table_schema='${SRC_SCHEMA}' AND table_name='${SRC_TABLE}';
" || echo "")

has_col () {
  local needle="$1"
  [[ ",$COLS," == *",$needle,"* ]]
}

# Descobre coluna de device_id mais provável
DEVICE_ID_COL=""
for c in device_id dev_id dev_eui deveui deviceid device; do
  if has_col "$c"; then DEVICE_ID_COL="$c"; break; fi
done

# Descobre coluna de tempo mais provável
TIME_COL=""
for c in time ts timestamp received_at created_at inserted_at observed_at; do
  if has_col "$c"; then TIME_COL="$c"; break; fi
done

# Expressões (se colunas não existirem, derivamos do JSON)
if [[ -n "${DEVICE_ID_COL}" ]]; then
  DEVICE_ID_EXPR="r.\"${DEVICE_ID_COL}\""
else
  DEVICE_ID_EXPR="COALESCE(
    r.payload->>'device_id',
    r.payload->>'deviceId',
    r.payload->'end_device_ids'->>'device_id',
    r.payload->>'dev_eui',
    r.payload->>'devEui',
    r.payload->>'DevEui',
    r.payload->'tags'->>'device_id',
    r.payload->'deviceInfo'->>'deviceName'
  )"
fi

if [[ -n "${TIME_COL}" ]]; then
  TIME_EXPR="r.\"${TIME_COL}\""
else
  TIME_EXPR="now()"
fi

echo ">> [F0] DEVICE_ID_EXPR: ${DEVICE_ID_EXPR}"
echo ">> [F0] TIME_EXPR:      ${TIME_EXPR}"

echo "==[Compat opcional] Criando colunas de compat no CAgg (evita 500 até trocar backend)=="
$PSQL <<'SQL'
-- CAgg: evitar 500 de coluna inexistente m.payload / m.device_name
ALTER TABLE ingest.measurement ADD COLUMN IF NOT EXISTS payload jsonb;
ALTER TABLE ingest.measurement ADD COLUMN IF NOT EXISTS device_name text;
-- preenche device_name a partir do device_id (idempotente e leve)
UPDATE ingest.measurement SET device_name = device_id WHERE device_name IS NULL;
SQL

echo "==[F1] Camada semântica: catálogo de dispositivos + view measurement_api =="
$PSQL <<'SQL'
CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE IF NOT EXISTS app.device_catalog (
  device_id   text PRIMARY KEY,
  device_name text NOT NULL
);

-- semente inicial pelo CAgg (se vazio, semearemos pela F2 depois)
INSERT INTO app.device_catalog (device_id, device_name)
SELECT DISTINCT device_id, device_id
FROM ingest.measurement
ON CONFLICT (device_id) DO NOTHING;

GRANT USAGE ON SCHEMA app TO public;
GRANT SELECT ON app.device_catalog TO public;

CREATE OR REPLACE VIEW app.measurement_api AS
SELECT
  m.time,
  m.device_id,
  COALESCE(dc.device_name, m.device_id) AS device_name,
  m.sensor_id,
  m.metric,
  m.value,
  m.unit,
  m.quality
FROM ingest.measurement m
LEFT JOIN app.device_catalog dc USING (device_id);

GRANT SELECT ON app.measurement_api TO public;
SQL

# Restringe ao role da API (remova se quiser manter 'public')
$PSQL -c "REVOKE SELECT ON app.device_catalog FROM public; GRANT SELECT ON app.device_catalog TO ${API_ROLE};" || true
$PSQL -c "REVOKE SELECT ON app.measurement_api FROM public; GRANT SELECT ON app.measurement_api TO ${API_ROLE};" || true
$PSQL -c "GRANT USAGE ON SCHEMA app TO ${API_ROLE};" || true

echo "==[F2] Catálogo materializado de chaves de payload (sem varrer CAgg)=="
if [[ -n "${PAYLOAD_SRC}" ]]; then
  echo ">> Usando fonte: ${SRC_SCHEMA}.${SRC_TABLE}"
  $PSQL <<SQL
DROP MATERIALIZED VIEW IF EXISTS app.payload_key_catalog CASCADE;

CREATE MATERIALIZED VIEW app.payload_key_catalog AS
WITH src AS (
  SELECT
    ${DEVICE_ID_EXPR} AS device_id,
    ${TIME_EXPR}      AS time,
    jsonb_object_keys(r.payload) AS key
  FROM ${SRC_SCHEMA}.${SRC_TABLE} r
  WHERE r.payload IS NOT NULL
)
SELECT
  device_id,
  key,
  MIN(time) AS first_seen,
  MAX(time) AS last_seen,
  COUNT(*)  AS occurrences
FROM src
WHERE device_id IS NOT NULL AND key IS NOT NULL
GROUP BY device_id, key
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uq_payload_key_catalog
  ON app.payload_key_catalog (device_id, key);

GRANT SELECT ON app.payload_key_catalog TO ${API_ROLE};

-- primeira carga
REFRESH MATERIALIZED VIEW CONCURRENTLY app.payload_key_catalog;

-- semeia catálogo de devices com o que veio da MV
INSERT INTO app.device_catalog (device_id, device_name)
SELECT DISTINCT device_id, device_id
FROM app.payload_key_catalog
ON CONFLICT (device_id) DO NOTHING;
SQL

  echo ">> [F2] Tentando agendar refresh periódico (Timescale) ..."
  $PSQL <<SQL
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname='timescaledb') THEN
    CREATE OR REPLACE FUNCTION app.refresh_payload_key_catalog(job_id int, config jsonb)
    RETURNS void LANGUAGE plpgsql AS \$INNER\$
    BEGIN
      REFRESH MATERIALIZED VIEW CONCURRENTLY app.payload_key_catalog;
    END;
    \$INNER\$;

    IF NOT EXISTS (
      SELECT 1 FROM timescaledb_information.jobs
      WHERE proc_schema='app' AND proc_name='refresh_payload_key_catalog'
    ) THEN
      PERFORM add_job('app.refresh_payload_key_catalog', '${TIMESCALE_JOB_INTERVAL}');
      RAISE NOTICE 'Timescale job criado (app.refresh_payload_key_catalog) cada ${TIMESCALE_JOB_INTERVAL}';
    ELSE
      RAISE NOTICE 'Timescale job já existe — nada a fazer.';
    END IF;
  ELSE
    RAISE NOTICE 'TimescaleDB não encontrado; use cron para REFRESH MATERIALIZED VIEW CONCURRENTLY app.payload_key_catalog;';
  END IF;
END$$;
SQL

else
  echo ">> [F2] Sem fonte com payload; criando estrutura vazia para não quebrar a API."
  $PSQL <<'SQL'
DROP MATERIALIZED VIEW IF EXISTS app.payload_key_catalog CASCADE;

CREATE MATERIALIZED VIEW app.payload_key_catalog AS
SELECT
  NULL::text AS device_id,
  NULL::text AS key,
  NULL::timestamptz AS first_seen,
  NULL::timestamptz AS last_seen,
  0::bigint AS occurrences
WHERE false
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uq_payload_key_catalog
  ON app.payload_key_catalog (device_id, key);

GRANT SELECT ON app.payload_key_catalog TO public;
SQL
  $PSQL -c "REVOKE SELECT ON app.payload_key_catalog FROM public; GRANT SELECT ON app.payload_key_catalog TO ${API_ROLE};" || true
fi

echo "==[Verificações com role da API]=="
$PSQL -c "SET ROLE ${API_ROLE}; SELECT * FROM app.measurement_api LIMIT 1;" || true
$PSQL -c "SET ROLE ${API_ROLE}; SELECT * FROM app.payload_key_catalog LIMIT 5;" || true
echo "==[DONE]=="

cat <<'EOSQL'

Altere as queries do backend para:

-- /api/catalog/devices
SELECT DISTINCT device_name
FROM app.measurement_api
WHERE device_name IS NOT NULL
ORDER BY 1;

-- /api/catalog/metrics (todas as chaves)
SELECT DISTINCT key
FROM app.payload_key_catalog
ORDER BY 1
LIMIT 10000;

-- /api/catalog/metrics por dispositivo (opcional)
SELECT key
FROM app.payload_key_catalog
WHERE device_id = :device_id
ORDER BY 1
LIMIT 10000;

EOSQL
