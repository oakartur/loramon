import os
import sys
import pathlib
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import text

# Ensure project root on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

# Configure database URL before importing the app
os.environ.setdefault(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/loramon_test"
)

from app.main import app  # noqa: E402
from app.database import engine  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    """Create minimal schemas and insert a synthetic measurement."""
    async with engine.begin() as conn:
        # Schemas
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS ingest"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        # Tables
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS ingest.measurement (
                    time timestamptz NOT NULL,
                    device_id text NOT NULL,
                    sensor_id text NOT NULL,
                    metric text NOT NULL,
                    value double precision NOT NULL,
                    PRIMARY KEY (time, device_id, metric)
                );
                """
            )
        )
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS app.device_catalog (
                    device_id text PRIMARY KEY,
                    device_name text NOT NULL
                );
                """
            )
        )
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS app.sensor_threshold (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid()
                );
                """
            )
        )
        # Insert catalog device
        await conn.execute(
            text(
                "INSERT INTO app.device_catalog (device_id, device_name) VALUES (:d, :n)"
            ),
            {"d": "dev1", "n": "Device 1"},
        )
        # Insert measurement
        now = datetime.now(timezone.utc)
        await conn.execute(
            text(
                """
                INSERT INTO ingest.measurement (time, device_id, sensor_id, metric, value)
                VALUES (:t, :d, :s, :m, :v)
                """
            ),
            {"t": now, "d": "dev1", "s": "s1", "m": "temp", "v": 42.0},
        )
        await conn.commit()
    try:
        yield
    finally:
        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA IF EXISTS ingest CASCADE"))
            await conn.execute(text("DROP SCHEMA IF EXISTS app CASCADE"))
            await conn.commit()


@pytest.mark.anyio
async def test_catalog_and_metrics_endpoints():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/api/catalog/devices")
        assert resp.status_code == 200
        devices = resp.json()
        assert any(d["value"] == "dev1" for d in devices)

        resp = await ac.get("/api/catalog/metrics")
        assert resp.status_code == 200
        metrics = resp.json()
        assert any(m["value"] == "temp" for m in metrics)

        resp = await ac.get("/api/metrics/overview")
        assert resp.status_code == 200
        overview = resp.json()
        assert overview["sensors_ativos"] >= 1
        assert "ultima_atualizacao" in overview

        resp = await ac.get(
            "/api/metrics/series",
            params={"device": "dev1", "metric": "temp"},
        )
        assert resp.status_code == 200
        series = resp.json()
        assert isinstance(series, list) and len(series) > 0
        assert "value" in series[0]
