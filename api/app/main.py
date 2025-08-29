import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import catalog, sql, metrics, auth, sites, floorplans, devices, sensors, placements, thresholds, timeseries

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
