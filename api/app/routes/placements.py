from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db
from ..schemas import PlacementIn, PlacementOut
from ..utils import admin_required, auth_required


router = APIRouter(prefix="/placements", tags=["placements"])


@router.post("/", response_model=PlacementOut, dependencies=[Depends(admin_required)])
async def upsert_placement(data: PlacementIn, db: AsyncSession = Depends(get_db)):
 q = text("""
  INSERT INTO app.sensor_placement(floorplan_id,sensor_id,x_rel,y_rel,rotation_deg)
  VALUES (:floorplan_id,:sensor_id,:x_rel,:y_rel,:rotation_deg)
  ON CONFLICT (floorplan_id, sensor_id) DO UPDATE
  SET x_rel=EXCLUDED.x_rel, y_rel=EXCLUDED.y_rel, rotation_deg=EXCLUDED.rotation_deg
  RETURNING id, floorplan_id, sensor_id, x_rel, y_rel, rotation_deg
 """)
 res = await db.execute(q, data.model_dump())
 await db.commit()
 return res.mappings().first()


@router.get("/by-floor/{floorplan_id}", response_model=list[PlacementOut], dependencies=[Depends(auth_required)])
async def list_by_floor(floorplan_id: str, db: AsyncSession = Depends(get_db)):
 q = text("""
  SELECT id, floorplan_id, sensor_id, x_rel, y_rel, rotation_deg
  FROM app.sensor_placement WHERE floorplan_id = :f
 """)
 res = await db.execute(q, {"f": floorplan_id})
 return [dict(r) for r in res.mappings().all()]
