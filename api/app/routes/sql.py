from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db
from ..utils import admin_required

# define o router deste módulo
router = APIRouter(prefix="/sql", tags=["sql"])

class QueryIn(BaseModel):
    query: str
    limit: int | None = 500

@router.post("/run", dependencies=[Depends(admin_required)])
async def run_sql(payload: QueryIn, db: AsyncSession = Depends(get_db)):
    """
    Executa a query SQL recebida e retorna colunas e linhas.
    Se a query não tiver LIMIT e 'limit' vier no payload, aplica um LIMIT.
    """
    sql_text = payload.query.strip()
    if not sql_text.lower().startswith("select"):
        raise HTTPException(400, "Somente consultas SELECT são permitidas")
    if payload.limit and "limit" not in sql_text.lower():
        sql_text = f"{sql_text}\nLIMIT {int(payload.limit)}"

    result = await db.execute(text(sql_text))
    rows = result.fetchall()
    cols = result.keys()
    return {
        "columns": list(cols),
        "rows": [list(r) for r in rows],
    }
