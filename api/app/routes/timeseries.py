from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db
from ..utils import auth_required
from ..schemas import TimeseriesQuery
from ..services.timeseries import choose_source_and_query, latest_by_floorplan


router = APIRouter(prefix="/timeseries", tags=["timeseries"])


@router.post("/query", dependencies=[Depends(auth_required)])
async def ts_query(q: TimeseriesQuery, db: AsyncSession = Depends(get_db)):
 res = await choose_source_and_query(db, q.device_id, q.metric, q.t_from, q.t_to)
 return [{"t": str(r[0]), "v": float(r[1])} for r in res.all()]


@router.get("/latest/floor/{floorplan_id}", dependencies=[Depends(auth_required)])
async def latest_for_floor(floorplan_id: str, db: AsyncSession = Depends(get_db)):
 res = await latest_by_floorplan(db, floorplan_id)
 return [dict(r) for r in res.mappings().all()]
