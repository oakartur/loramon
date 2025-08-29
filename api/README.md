# API Usage

## Starting containers

Build and start services:

```bash
docker compose build
docker compose up -d
```

Check database connectivity:

```bash
curl -f http://localhost:8000/health/db
```

## Inspecting `ingest.measurement`

Use SQL queries to explore recent data:

```sql
-- Measurements per metric in the last hour
SELECT metric, COUNT(*)
FROM ingest.measurement
WHERE "time" >= now() - interval '1 hour'
GROUP BY metric
ORDER BY metric;

-- Latest samples for a device and metric
SELECT "time", value
FROM ingest.measurement
WHERE device_id = 'my-device'
  AND metric    = 'temperature'
ORDER BY "time" DESC
LIMIT 5;
```

## Catalog endpoints

List devices from a specific application:

```bash
curl -s "http://localhost:8000/api/catalog/devices?application=my-app"
http GET :8000/api/catalog/devices application==my-app
```

List available metrics:

```bash
curl -s http://localhost:8000/api/catalog/metrics
http GET :8000/api/catalog/metrics
```

## Metrics endpoints

Overview of active sensors in the last two hours:

```bash
curl -s "http://localhost:8000/api/metrics/overview?minutes=120"
http GET :8000/api/metrics/overview minutes==120
```

Time series for a device and metric over the last day with 1-minute buckets:

```bash
curl -s "http://localhost:8000/api/metrics/series?device=dev123&metric=temperature&minutes=1440&step=60"
http GET :8000/api/metrics/series device==dev123 metric==temperature minutes==1440 step==60
```

