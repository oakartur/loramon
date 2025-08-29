from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def choose_source_and_query(db: AsyncSession, device_id: str, metric: str, t_from: str, t_to: str):
 # Decide entre cagg_1h, cagg_5m ou bruto baseado no intervalo
 # Simples: >7d → 1h; >1d → 5m; senão bruto
 q = text("SELECT EXTRACT(EPOCH FROM ($2::timestamptz - $1::timestamptz)) AS sec")
 res = await db.execute(q, {"1": t_from, "2": t_to})
 sec = res.scalar_one()
 if sec > 7*24*3600:
  src = "ingest.cagg_1h"
  tcol = "bucket"
  vcol = "avg_value"
 elif sec > 24*3600:
  src = "ingest.cagg_5m"
  tcol = "bucket"
  vcol = "avg_value"
 else:
  src = "ingest.measurement"
  tcol = "time"
  vcol = "value"
 sql = text(f"""
  SELECT {tcol} AS t, {vcol} AS v
  FROM {src}
  WHERE device_id = :device_id AND metric = :metric
  AND {tcol} BETWEEN :t_from AND :t_to
  ORDER BY t ASC
 """)
 return await db.execute(sql, {
  "device_id": device_id,
  "metric": metric,
  "t_from": t_from,
  "t_to": t_to,
 })

async def latest_by_floorplan(db: AsyncSession, floorplan_id: str):
 sql = text("""
 WITH latest AS (
  SELECT DISTINCT ON (device_id, metric)
   device_id, metric, value, time
  FROM ingest.measurement
  ORDER BY device_id, metric, time DESC
 )
 SELECT s.id AS sensor_uuid, s.display_name, s.icon, s.unit_ui,
  l.value, l.time
 FROM app.sensor s
 JOIN app.device d ON d.id = s.device_id
 JOIN app.sensor_placement sp ON sp.sensor_id = s.id
 LEFT JOIN latest l ON l.device_id = d.device_id AND l.metric = s.sensor_key
 WHERE sp.floorplan_id = :floorplan_id;
 """)
 return await db.execute(sql, {"floorplan_id": floorplan_id})
