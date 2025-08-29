import os
import sys
import pathlib
import pytest
from httpx import AsyncClient
from passlib.hash import bcrypt
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
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS app.user_account (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    username text UNIQUE NOT NULL,
                    password_hash text NOT NULL,
                    role text NOT NULL
                );
                """
            )
        )
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS app.site (
                    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                    code text UNIQUE NOT NULL,
                    name text NOT NULL
                );
                """
            )
        )
        hashed = bcrypt.hash("admin")
        await conn.execute(
            text(
                """
                INSERT INTO app.user_account (username, password_hash, role)
                VALUES (:u, :p, 'admin')
                ON CONFLICT (username) DO NOTHING
                """
            ),
            {"u": "admin", "p": hashed},
        )
        await conn.commit()
    yield
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS app CASCADE"))
        await conn.commit()


@pytest.mark.anyio
async def test_login_and_site_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/auth/login", json={"username": "admin", "password": "admin"}
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = await ac.post(
            "/api/sites/", json={"code": "S1", "name": "Site 1"}, headers=headers
        )
        assert resp.status_code == 200

        resp = await ac.get("/api/sites/", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert any(site["code"] == "S1" for site in data)
