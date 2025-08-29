from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("/applications")
async def applications(db: AsyncSession = Depends(get_db)):
    q = text("""
        SELECT application_name AS value, application_name AS label
        FROM raw.uplink
        WHERE COALESCE(application_name, '') <> ''
        GROUP BY application_name
        ORDER BY application_name
    """)
    rows = (await db.execute(q)).all()
    return [{"value": v, "label": l} for (v, l) in rows]

@router.get("/devices")
async def devices(
    minutes: int = Query(default=60, gt=0),
    db: AsyncSession = Depends(get_db),
):
    q = text(
        """
        SELECT m.device_id AS value,
               COALESCE(dc.device_name, m.device_id) AS label
        FROM (
            SELECT DISTINCT device_id
            FROM ingest.measurement
            WHERE time > now() - (:minutes * INTERVAL '1 minute')
        ) m
        LEFT JOIN app.device_catalog dc ON dc.device_id = m.device_id
        ORDER BY label
        """
    )
    rows = (await db.execute(q, {"minutes": minutes})).all()
    return [{"value": v, "label": l} for (v, l) in rows]

@router.get("/metrics")
async def metrics(db: AsyncSession = Depends(get_db)):
    q = text("""
        SELECT DISTINCT metric AS value, metric AS label
        FROM ingest.measurement
        ORDER BY 1
    """)
    rows = (await db.execute(q)).all()
    return [{"value": v, "label": l} for (v, l) in rows]
