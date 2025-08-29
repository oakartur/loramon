from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db
from ..schemas import ThresholdIn, ThresholdOut
from ..utils import admin_required, auth_required


router = APIRouter(prefix="/thresholds", tags=["thresholds"])


@router.post("/", response_model=ThresholdOut, dependencies=[Depends(admin_required)])
async def upsert_threshold(data: ThresholdIn, db: AsyncSession = Depends(get_db)):
 q = text("""
  INSERT INTO app.sensor_threshold(sensor_id,strategy,min_value,max_value,window_n,k_std,severity,enabled)
  VALUES (:sensor_id,:strategy,:min_value,:max_value,:window_n,:k_std,:severity,:enabled)
  ON CONFLICT (sensor_id) DO UPDATE SET
  strategy=EXCLUDED.strategy,
  min_value=EXCLUDED.min_value,
  max_value=EXCLUDED.max_value,
  window_n=EXCLUDED.window_n,
  k_std=EXCLUDED.k_std,
  severity=EXCLUDED.severity,
  enabled=EXCLUDED.enabled
  RETURNING id, sensor_id, strategy, min_value, max_value, window_n, k_std, severity, enabled
 """)
 res = await db.execute(q, data.model_dump())
 await db.commit()
 return res.mappings().first()


@router.get("/by-sensor/{sensor_id}", response_model=list[ThresholdOut], dependencies=[Depends(auth_required)])
async def list_by_sensor(sensor_id: str, db: AsyncSession = Depends(get_db)):
 q = text("SELECT id,sensor_id,strategy,min_value,max_value,window_n,k_std,severity,enabled FROM app.sensor_threshold WHERE sensor_id=:s")
 res = await db.execute(q, {"s": sensor_id})
 return [dict(r) for r in res.mappings().all()]
