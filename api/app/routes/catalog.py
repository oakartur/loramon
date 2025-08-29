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
    application: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    if application:
        q = text("""
            SELECT d.device_id AS value,
                   COALESCE(d.device_name, d.device_id) AS label
            FROM app.device_catalog d
            WHERE d.device_id IN (
                SELECT DISTINCT u.device_name
                FROM raw.uplink u
                WHERE u.application_name = :app
                  AND COALESCE(u.device_name, '') <> ''
            )
            ORDER BY label
        """)
        rows = (await db.execute(q, {"app": application})).all()
    else:
        q = text("""
            SELECT d.device_id AS value,
                   COALESCE(d.device_name, d.device_id) AS label
            FROM app.device_catalog d
            ORDER BY label
        """)
        rows = (await db.execute(q)).all()

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
