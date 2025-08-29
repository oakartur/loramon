# etl.py
import os
import time
import traceback
import logging
from typing import Any, Dict, Iterable, List, Optional, Tuple

import psycopg
from psycopg.rows import dict_row

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
DSN = os.getenv("DATABASE_URL_SYNC")
if not DSN:
    raise RuntimeError("DATABASE_URL_SYNC não definido no ambiente.")

BATCH = int(os.getenv("ETL_BATCH", "5000"))
SLEEP_SEC = float(os.getenv("ETL_SLEEP", "2.0"))

# -----------------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------------
Num = Optional[float]
ParsedMetric = Tuple[str, float, Optional[str]]  # (metric, value, unit)


def _to_float(x: Any) -> Num:
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x.strip())
        except Exception:
            return None
    return None


def _dig(payload: Any, path_tokens: List[str]) -> Any:
    cur = payload
    for p in path_tokens:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def parse_payload(payload: Dict[str, Any], mapping_rows: Optional[Iterable[Dict[str, Any]]]) -> List[ParsedMetric]:
    """
    Se mapping_rows for fornecido, usa colunas:
      - json_path: ex. {object,internal_sensors_temperature}
      - metric: nome da métrica resultante
      - unit: unidade (opcional)
      - device_profile (opcional)
    Caso contrário, exporta apenas pares numéricos diretos nível-1.
    """
    out: List[ParsedMetric] = []

    if mapping_rows:
        for m in mapping_rows:
            jp = (m.get("json_path") or "").strip()
            metric = (m.get("metric") or "").strip()
            unit = (m.get("unit") or None)
            if not jp or not metric:
                continue

            jp = jp.strip("{}").strip()
            tokens = [t.strip() for t in jp.split(",") if t.strip()]
            val = _dig(payload, tokens)
            f = _to_float(val)
            if f is not None:
                out.append((metric, f, unit))
    else:
        for k, v in payload.items():
            f = _to_float(v)
            if f is not None:
                out.append((k, f, None))

    return out


# -----------------------------------------------------------------------------
# Checkpoint helpers
# -----------------------------------------------------------------------------
def ensure_checkpoint_row(cur) -> None:
    """Garante que ingest.etl_checkpoint tenha ao menos 1 linha."""
    cur.execute("SELECT id FROM ingest.etl_checkpoint LIMIT 1")
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO ingest.etl_checkpoint(id) VALUES (0)")


def get_checkpoint(cur) -> int:
    cur.execute("SELECT id FROM ingest.etl_checkpoint LIMIT 1 FOR UPDATE")
    row = cur.fetchone()
    return int(row["id"]) if row and row.get("id") is not None else 0


def set_checkpoint(cur, new_id: int) -> None:
    cur.execute("UPDATE ingest.etl_checkpoint SET id = %s", (new_id,))


# -----------------------------------------------------------------------------
# Loop principal
# -----------------------------------------------------------------------------
def run_once() -> None:
    logger.info("Connecting to database")
    with psycopg.connect(DSN, autocommit=False) as conn:
        logger.info("Database connection established")
        with conn.cursor(row_factory=dict_row) as cur:

            # 1) Tenta carregar mapping; se falhar, ROLLBACK e segue sem mapping
            try:
                cur.execute("SELECT * FROM app.metric_map WHERE COALESCE(enabled, TRUE)")
                all_mapping = cur.fetchall()
                conn.commit()  # fecha a transação iniciada por esse SELECT
            except Exception as e:
                print("ETL warn: metric_map indisponível; usando mapeamento livre:", repr(e))
                conn.rollback()
                all_mapping = []

            # 2) Nova transação: checkpoint + leitura do RAW
            try:
                ensure_checkpoint_row(cur)
                last_id = get_checkpoint(cur)

                cur.execute(
                    """
                    SELECT id, application_name, device_profile, device_name, ts, payload
                    FROM raw.uplink
                    WHERE id > %s
                    ORDER BY id
                    LIMIT %s
                    """,
                    (last_id, BATCH),
                )
                rows = cur.fetchall()
                logger.info("Fetched %d rows from raw.uplink after id %d", len(rows), last_id)
            except Exception as e:
                # Se algo deu errado aqui (ex. tabela não existe), zera a transação e tenta depois
                conn.rollback()
                print("ETL error ao ler checkpoint/raw.uplink:", repr(e))
                time.sleep(SLEEP_SEC)
                return

            if not rows:
                conn.commit()
                logger.info("No new rows found; sleeping %.1f seconds", SLEEP_SEC)
                time.sleep(SLEEP_SEC)
                return

            # 3) Monta inserts a partir do lote
            max_id = last_id
            inserts: List[Tuple[Any, str, str, str, float, Optional[str]]] = []

            for r in rows:
                max_id = max(max_id, int(r["id"]))
                payload: Dict[str, Any] = r["payload"] or {}
                dprof = r.get("device_profile")

                if all_mapping:
                    mapping_rows = [
                        m for m in all_mapping
                        if (m.get("device_profile") in (None, "", dprof))
                    ]
                else:
                    mapping_rows = None

                parsed = parse_payload(payload, mapping_rows)
                if not parsed:
                    continue

                device_id = r.get("device_name") or ""
                for metric, value, unit in parsed:
                    inserts.append((
                        r["ts"],      # time
                        device_id,    # device_id
                        metric,       # sensor_id
                        metric,       # metric
                        value,        # value
                        unit,         # unit
                    ))

            # 4) Aplica inserts + checkpoint e COMMIT
            if inserts:
                cur.executemany(
                    """
                    INSERT INTO ingest.measurement (time, device_id, sensor_id, metric, value, unit)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    inserts,
                )

            set_checkpoint(cur, max_id)
            conn.commit()


def main() -> None:
    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            print("Encerrando por KeyboardInterrupt.")
            break
        except Exception as e:
            print("ETL error:", repr(e))
            traceback.print_exc()
            time.sleep(3.0)


if __name__ == "__main__":
    main()
