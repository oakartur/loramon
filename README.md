# LoraMon

Plataforma interna para visualizar sensores LoRaWAN ingeridos em PostgreSQL/TimescaleDB.

## Subir
1. Copie `.env.example` para `.env` e ajuste credenciais do banco e `SECRET_KEY`.
2. Aplique migração: `psql "$DATABASE_URL_SYNC" -f db/migrations/001_init.sql`.
3. `docker compose build && docker compose up -d`.
4. Web: `http://<vm>`; API docs: `http://<vm>:8000/docs`.

## Notas
- ETL transforma `raw.uplink.payload` → `ingest.measurement`.
- CAGGs (5m/1h) e retenção (90d) para performance.
- Floorplans: upload PDF → render PNG com zoom/pan.
- Pooling (10s) para últimos valores/alertas.
