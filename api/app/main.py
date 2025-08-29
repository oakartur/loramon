import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import catalog, sql, metrics, auth, sites, floorplans, devices, sensors, placements, thresholds, timeseries

app = FastAPI(title="LoraMon API")


app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"], # rede interna; ajuste depois
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
app.include_router(metrics.router)
app.include_router(sql.router)
app.include_router(catalog.router)

@app.get("/-/health")
def health():
 return {"ok": True}
