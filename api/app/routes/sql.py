from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db

# define o router deste módulo
router = APIRouter(prefix="/sql", tags=["sql"])

class QueryIn(BaseModel):
    query: str
    limit: int | None = 500

@router.post("/run")
async def run_sql(payload: QueryIn, db: AsyncSession = Depends(get_db)):
    """
    Executa a query SQL recebida e retorna colunas e linhas.
    Se a query não tiver LIMIT e 'limit' vier no payload, aplica um LIMIT.
    """
    sql_text = payload.query.strip()
    if payload.limit and "limit" not in sql_text.lower():
        sql_text = f"{sql_text}\nLIMIT {int(payload.limit)}"

    result = await db.execute(text(sql_text))
    rows = result.fetchall()
    cols = result.keys()
    return {
        "columns": list(cols),
        "rows": [list(r) for r in rows],
    }
