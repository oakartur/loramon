from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db
from ..schemas import SensorIn, SensorOut
from ..utils import admin_required, auth_required


router = APIRouter(prefix="/sensors", tags=["sensors"])


@router.post("/", response_model=SensorOut, dependencies=[Depends(admin_required)])
async def create_sensor(data: SensorIn, db: AsyncSession = Depends(get_db)):
 q = text("""
  INSERT INTO app.sensor(device_id,sensor_key,display_name,icon,unit_ui)
  VALUES (:device_id,:sensor_key,:display_name,:icon,:unit_ui)
  RETURNING id, device_id, sensor_key, display_name, icon, unit_ui
 """)
 res = await db.execute(q, data.model_dump())
 await db.commit()
 return res.mappings().first()


@router.get("/", response_model=list[SensorOut], dependencies=[Depends(auth_required)])
async def list_sensors(db: AsyncSession = Depends(get_db)):
 q = text("SELECT id,device_id,sensor_key,display_name,icon,unit_ui FROM app.sensor ORDER BY display_name")
 res = await db.execute(q)
 return [dict(r) for r in res.mappings().all()]
