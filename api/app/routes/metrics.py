from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/overview")
async def overview(
    minutes: int = 60,
    db: AsyncSession = Depends(get_db),
):
    # evita :mins::interval – usa multiplicação por interval
    q = text(
        """
        WITH w AS (
          SELECT now() - (:mins * interval '1 minute') AS t0
        )
        SELECT
          -- sensores ativos na janela
          (SELECT COUNT(DISTINCT sensor_id)
             FROM ingest.measurement
            WHERE "time" >= (SELECT t0 FROM w)
          ) AS sensors_ativos,

          -- última atualização NA MESMA JANELA
          (SELECT COALESCE(MAX("time"), (SELECT t0 FROM w))
             FROM ingest.measurement
            WHERE "time" >= (SELECT t0 FROM w)
          ) AS ultima_atualizacao,

          -- total de alertas
          (SELECT COUNT(*) FROM app.sensor_threshold) AS total_alertas_config
    """
    )
    row = (await db.execute(q, {"mins": minutes})).mappings().one()
    last_update = row["ultima_atualizacao"]
    return {
        "sensors_ativos": row["sensors_ativos"],
        "ultima_atualizacao": last_update.isoformat(),
        "total_alertas_config": row["total_alertas_config"],
        "active_sensors": row["sensors_ativos"],
        "last_update": last_update.isoformat(),
        "alerts_configured": row["total_alertas_config"],
    }


@router.get("/series")
async def series(
    device: str,
    metric: str,
    minutes: int = 60,
    step: int = Query(300, ge=1, description="tamanho do bucket (s)"),
    db: AsyncSession = Depends(get_db),
):
    # nota: usa "time" e device_id corretos, sem CAST com ::
    q = text(
        """
        SELECT
          FLOOR(EXTRACT(EPOCH FROM m."time") / :step) * :step AS bucket,
          AVG(m.value)                                       AS value
        FROM ingest.measurement m
        WHERE m.device_id = :device
          AND m.metric   = :metric
          AND m."time"  >= now() - (:mins * interval '1 minute')
        GROUP BY 1
        ORDER BY 1
    """
    )
    rows = (
        await db.execute(
            q,
            {
                "device": device,
                "metric": metric,
                "mins": minutes,
                "step": step,
            },
        )
    ).all()
    return [{"ts": int(b), "value": v} for (b, v) in rows]
