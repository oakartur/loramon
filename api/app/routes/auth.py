from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..deps import get_db
from ..schemas import LoginIn, TokenOut
from ..security import create_token
from passlib.hash import bcrypt


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
 q = text("SELECT username, password_hash, role FROM app.user_account WHERE username = :u")
 res = await db.execute(q, {"u": data.username})
 row = res.mappings().first()
 if not row or not bcrypt.verify(data.password, row["password_hash"]):
  raise HTTPException(status_code=401, detail="Credenciais inválidas")
 token = create_token(sub=row["username"], role=row["role"])
 return TokenOut(access_token=token)
