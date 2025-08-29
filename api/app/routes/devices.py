from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db
from ..schemas import DeviceIn, DeviceOut
from ..utils import admin_required, auth_required

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=DeviceOut, dependencies=[Depends(admin_required)])
async def create_device(data: DeviceIn, db: AsyncSession = Depends(get_db)):
 q = text("""
  INSERT INTO app.device(site_id,device_id,display_name,model,manufacturer)
  VALUES (:site_id,:device_id,:display_name,:model,:manufacturer)
  RETURNING id, site_id, device_id, display_name, model, manufacturer
 """)
 res = await db.execute(q, data.model_dump())
 await db.commit()
 return res.mappings().first()

@router.get("/", response_model=list[DeviceOut], dependencies=[Depends(auth_required)])
async def list_devices(db: AsyncSession = Depends(get_db)):
 q = text("SELECT id,site_id,device_id,display_name,model,manufacturer FROM app.device ORDER BY display_name")
 res = await db.execute(q)
 return [dict(r) for r in res.mappings().all()]
