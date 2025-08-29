import logging
import os
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .deps import get_db
from .routes import catalog, sql, metrics, auth, sites, floorplans, devices, sensors, placements, thresholds, timeseries


logger = logging.getLogger(__name__)

app = FastAPI(title="LoraMon API")


origins = os.getenv("ALLOW_ORIGINS", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api")
app.include_router(sites.router, prefix="/api")
app.include_router(floorplans.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(sensors.router, prefix="/api")
app.include_router(placements.router, prefix="/api")
app.include_router(thresholds.router, prefix="/api")
app.include_router(timeseries.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(sql.router, prefix="/api")
app.include_router(catalog.router, prefix="/api")

@app.get("/-/health")
def health():
 return {"ok": True}


@app.get("/api/-/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    """Verifica a conectividade com o banco de dados."""
    try:
        result = await db.execute(
            text(
                "SELECT current_database() AS database, current_user AS user, now() AS now"
            )
        )
        row = result.mappings().one()
        return {
            "database": row["database"],
            "user": row["user"],
            "now": row["now"].isoformat(),
        }
    except Exception as exc:  # pragma: no cover - log unexpected errors
        logger.exception("Database health check failed")
        raise HTTPException(status_code=503, detail="Database connection error") from exc
