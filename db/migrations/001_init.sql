-- Schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS ingest;
CREATE SCHEMA IF NOT EXISTS app;


-- RAW: tabela que você já tem (ajuste o nome se necessário)
-- Se já existir, pule esta criação. Mantemos apenas índices.
-- CREATE TABLE raw.uplink(
-- id bigint,
-- application_name text,
-- device_profile text,
-- device_name text,
-- ts timestamptz,
-- payload jsonb
-- );


-- Índices úteis no raw
CREATE INDEX IF NOT EXISTS uplink_ts_desc ON raw.uplink (ts DESC);
CREATE INDEX IF NOT EXISTS uplink_device_ts_desc ON raw.uplink (device_name, ts DESC);
CREATE INDEX IF NOT EXISTS uplink_payload_gin ON raw.uplink USING GIN (payload jsonb_path_ops);


-- Ingest: série temporal
CREATE TABLE IF NOT EXISTS ingest.measurement (
 time timestamptz NOT NULL,
 device_id text NOT NULL,
 sensor_id text NOT NULL,
 metric text NOT NULL,
 value double precision NOT NULL,
 unit text NULL,
 quality jsonb NULL,
 PRIMARY KEY (time, device_id, metric)
);
SELECT create_hypertable('ingest.measurement','time', if_not_exists => TRUE);


CREATE INDEX IF NOT EXISTS idx_meas_device_time ON ingest.measurement (device_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_meas_metric_time ON ingest.measurement (metric, time DESC);


-- Retenção e compressão
SELECT add_retention_policy('ingest.measurement', INTERVAL '90 days');
ALTER TABLE ingest.measurement SET (
 timescaledb.compress,
 timescaledb.compress_segmentby = 'device_id,metric'
);
SELECT add_compression_policy('ingest.measurement', INTERVAL '7 days');


-- CAGGs
CREATE MATERIALIZED VIEW IF NOT EXISTS ingest.cagg_5m
WITH (timescaledb.continuous) AS
SELECT time_bucket('5 minutes', time) AS bucket,
 device_id, sensor_id, metric,
 avg(value) AS avg_value, min(value) AS min_value, max(value) AS max_value,
 count(*) AS n
FROM ingest.measurement
GROUP BY 1,2,3,4;


SELECT add_continuous_aggregate_policy('ingest.cagg_5m',
 start_offset => INTERVAL '90 days',
 end_offset => INTERVAL '5 minutes',
 schedule_interval => INTERVAL '5 minutes');
ALTER MATERIALIZED VIEW ingest.cagg_5m SET (timescaledb.materialized_only=false);


CREATE MATERIALIZED VIEW IF NOT EXISTS ingest.cagg_1h
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', time) AS bucket,
 device_id, sensor_id, metric,
 avg(value) AS avg_value, min(value) AS min_value, max(value) AS max_value,
 count(*) AS n
FROM ingest.measurement
GROUP BY 1,2,3,4;

SELECT add_continuous_aggregate_policy('ingest.cagg_1h',
 start_offset => INTERVAL '180 days',
 end_offset => INTERVAL '1 hour',
 schedule_interval => INTERVAL '1 hour');
ALTER MATERIALIZED VIEW ingest.cagg_1h SET (timescaledb.materialized_only=false);

-- Checkpoint do ETL
CREATE TABLE IF NOT EXISTS ingest.etl_checkpoint (
 id bigint PRIMARY KEY
);
INSERT INTO ingest.etl_checkpoint(id) VALUES (0)
ON CONFLICT DO NOTHING;

-- Mapeamento opcional de métricas (extrair campos específicos do JSON)
CREATE TABLE IF NOT EXISTS app.metric_map (
 id bigserial PRIMARY KEY,
 application text NULL,
 device_profile text NULL,
 json_path text NOT NULL, -- ex.: '{object,decoded,temperature}'
 metric text NOT NULL, -- ex.: 'temperature_C'
 unit text NOT NULL, -- ex.: '°C'
 enabled boolean NOT NULL DEFAULT true
);

-- RBAC e metadados do app
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- para gen_random_uuid()


CREATE TABLE IF NOT EXISTS app.user_account (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 username text UNIQUE NOT NULL,
 password_hash text NOT NULL,
 role text NOT NULL CHECK (role IN ('admin','user')),
 created_at timestamptz NOT NULL DEFAULT now()
);

-- admin:admin (troque depois!)
INSERT INTO app.user_account(username, password_hash, role)
VALUES ('admin', crypt('admin', gen_salt('bf')), 'admin')
ON CONFLICT (username) DO NOTHING;


CREATE TABLE IF NOT EXISTS app.site (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 code text UNIQUE NOT NULL,
 name text NOT NULL
);

CREATE TABLE IF NOT EXISTS app.floorplan (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 site_id uuid NOT NULL REFERENCES app.site(id) ON DELETE CASCADE,
 name text NOT NULL,
 file_path text NOT NULL,
 page_index int NOT NULL DEFAULT 0,
 width_px int NULL,
 height_px int NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS app.device (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 site_id uuid NOT NULL REFERENCES app.site(id) ON DELETE CASCADE,
 device_id text UNIQUE NOT NULL,
 display_name text NOT NULL,
 model text NULL,
 manufacturer text NULL
);

CREATE TABLE IF NOT EXISTS app.sensor (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 device_id uuid NOT NULL REFERENCES app.device(id) ON DELETE CASCADE,
 sensor_key text NOT NULL,
 display_name text NOT NULL,
 icon text NOT NULL,
 unit_ui text NOT NULL
);


CREATE TABLE IF NOT EXISTS app.sensor_placement (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 floorplan_id uuid NOT NULL REFERENCES app.floorplan(id) ON DELETE CASCADE,
 sensor_id uuid NOT NULL REFERENCES app.sensor(id) ON DELETE CASCADE,
 x_rel double precision NOT NULL CHECK (x_rel >= 0 AND x_rel <= 1),
 y_rel double precision NOT NULL CHECK (y_rel >= 0 AND y_rel <= 1),
 rotation_deg double precision NULL,
 UNIQUE (floorplan_id, sensor_id)
);


CREATE TABLE IF NOT EXISTS app.sensor_threshold (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 sensor_id uuid NOT NULL REFERENCES app.sensor(id) ON DELETE CASCADE,
 strategy text NOT NULL CHECK (strategy IN ('abs_range','moving_mean_std')),
 min_value double precision NULL,
 max_value double precision NULL,
 window_n int NULL,
 k_std double precision NULL,
 severity text NOT NULL DEFAULT 'major',
 enabled boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT now()
);
