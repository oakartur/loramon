from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db
from ..schemas import SiteIn, SiteOut
from ..utils import admin_required, auth_required


router = APIRouter(prefix="/sites", tags=["sites"])


@router.post("/", response_model=SiteOut, dependencies=[Depends(admin_required)])
async def create_site(data: SiteIn, db: AsyncSession = Depends(get_db)):
 q = text("INSERT INTO app.site(code,name) VALUES (:c,:n) RETURNING id,code,name")
 res = await db.execute(q, {"c": data.code, "n": data.name})
 row = res.mappings().first()
 await db.commit()
 return row


@router.get("/", response_model=list[SiteOut], dependencies=[Depends(auth_required)])
async def list_sites(db: AsyncSession = Depends(get_db)):
 q = text("SELECT id,code,name FROM app.site ORDER BY name")
 res = await db.execute(q)
 return [dict(r) for r in res.mappings().all()]
