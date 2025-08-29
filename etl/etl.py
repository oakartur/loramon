# etl.py
import argparse
import json
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

BATCH = int(os.getenv("ETL_BATCH", "5000"))
SLEEP_SEC = float(os.getenv("ETL_SLEEP", "2.0"))

# -----------------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------------
Num = Optional[float]
ParsedMetric = Tuple[str, float, Optional[str], str]  # (metric, value, unit, label)
Failure = Tuple[str, str, str]  # (metric, json_path, reason)


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
        elif isinstance(cur, list):
            try:
                idx = int(p)
            except ValueError:
                return None
            if 0 <= idx < len(cur):
                cur = cur[idx]
            else:
                return None
        else:
            return None
    return cur


def parse_payload(
    payload: Dict[str, Any],
    mapping_rows: Optional[Iterable[Dict[str, Any]]],
) -> Tuple[List[ParsedMetric], List[Failure]]:
    """
    Se mapping_rows for fornecido, usa colunas:
      - json_path: ex. {object,internal_sensors_temperature}
      - metric: nome da métrica resultante
      - unit: unidade (opcional)
      - label: nome do sensor (opcional)
      - device_profile (opcional)
    Caso contrário, exporta apenas pares numéricos diretos nível-1.
    Retorna lista de métricas extraídas e lista de falhas (metric, json_path, razão).
    """
    out: List[ParsedMetric] = []
    fails: List[Failure] = []

    if mapping_rows:
        for m in mapping_rows:
            jp = (m.get("json_path") or "").strip()
            metric = (m.get("metric") or "").strip()
            unit = (m.get("unit") or None)
            label = (m.get("label") or metric).strip()
            if not jp or not metric:
                continue

            jp = jp.strip("{}").strip()
            tokens = [t.strip() for t in jp.split(",") if t.strip()]
            val = _dig(payload, tokens)
            if val is None:
                fails.append((metric, jp, "json_path not found"))
                continue
            f = _to_float(val)
            if f is None:
                fails.append((metric, jp, "decode error"))
                continue
            out.append((metric, f, unit, label))
    else:
        for k, v in payload.items():
            f = _to_float(v)
            if f is not None:
                out.append((k, f, None, k))

    return out, fails


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
    if not DSN:
        raise RuntimeError("DATABASE_URL_SYNC não definido no ambiente.")
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
            metric_counts: Dict[str, int] = {}
            failures_batch: List[Tuple[int, Failure]] = []
            example_failure: Optional[Tuple[int, Dict[str, Any], List[Failure]]] = None

            id_min = int(rows[0]["id"])
            id_max = int(rows[-1]["id"])

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

                parsed, fails = parse_payload(payload, mapping_rows)
                if fails:
                    for f in fails:
                        failures_batch.append((int(r["id"]), f))
                    example_failure = (int(r["id"]), payload, fails)
                if not parsed:
                    if mapping_rows:
                        logger.debug(
                            "row %s discarded: %s",
                            r["id"],
                            ", ".join(reason for _, _, reason in fails) or "no metrics extracted",
                        )
                    else:
                        logger.debug("row %s discarded: no metric_map matched", r["id"])
                    continue

                device_id = r.get("device_name") or ""
                for metric, value, unit, label in parsed:
                    inserts.append((
                        r["ts"],      # time
                        device_id,    # device_id
                        label,        # sensor_id
                        metric,       # metric
                        value,        # value
                        unit,         # unit
                    ))
                    metric_counts[metric] = metric_counts.get(metric, 0) + 1

            if example_failure:
                fid, fpayload, ffails = example_failure
                logger.debug(
                    "example failing payload id %s: paths=%s payload=%s",
                    fid,
                    ffails,
                    json.dumps(fpayload, ensure_ascii=False)[:1000],
                )

            # 4) Aplica inserts + checkpoint e COMMIT
            inserted_count = 0
            if inserts:
                cur.executemany(
                    """
                    INSERT INTO ingest.measurement (time, device_id, sensor_id, metric, value, unit)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    inserts,
                )
                inserted_count = cur.rowcount

            if inserted_count > 0:
                set_checkpoint(cur, max_id)
                conn.commit()
                logger.info("inserted_count=%d", inserted_count)
                logger.debug(
                    "batch %s-%s rows=%d points=%d per_metric=%s",
                    id_min,
                    id_max,
                    len(rows),
                    sum(metric_counts.values()),
                    metric_counts,
                )
            else:
                if failures_batch:
                    conn.rollback()
                    logger.warning(
                        "batch %s-%s produced 0 inserts due to extraction failures; checkpoint not advanced",
                        id_min,
                        id_max,
                    )
                else:
                    set_checkpoint(cur, max_id)
                    conn.commit()
                    logger.info(
                        "batch %s-%s: no metrics matched; checkpoint advanced", id_min, id_max
                    )


def dry_run(limit: int, from_id: Optional[int] = None) -> None:
    if not DSN:
        raise RuntimeError("DATABASE_URL_SYNC não definido no ambiente.")
    with psycopg.connect(DSN, autocommit=True) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            try:
                cur.execute(
                    "SELECT * FROM app.metric_map WHERE COALESCE(enabled, TRUE)"
                )
                all_mapping = cur.fetchall()
            except Exception as e:
                logger.warning("metric_map indisponível: %s", repr(e))
                all_mapping = []

            if from_id is not None:
                cur.execute(
                    """
                    SELECT id, device_profile, device_name, ts, payload
                    FROM raw.uplink
                    WHERE id >= %s
                    ORDER BY id
                    LIMIT %s
                    """,
                    (from_id, limit),
                )
                rows = cur.fetchall()
            else:
                cur.execute(
                    """
                    SELECT id, device_profile, device_name, ts, payload
                    FROM raw.uplink
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()[::-1]

            for r in rows:
                payload: Dict[str, Any] = r["payload"] or {}
                dprof = r.get("device_profile")
                if all_mapping:
                    mapping_rows = [
                        m for m in all_mapping
                        if (m.get("device_profile") in (None, "", dprof))
                    ]
                else:
                    mapping_rows = None

                parsed, fails = parse_payload(payload, mapping_rows)
                print(f"row id={r['id']} ts={r['ts']}")
                if mapping_rows:
                    for m in mapping_rows:
                        jp = (m.get("json_path") or "").strip()
                        metric = (m.get("metric") or "").strip()
                        val = _dig(payload, [t.strip() for t in jp.strip("{}").split(",") if t.strip()])
                        display = val if _to_float(val) is not None else "MISSING"
                        print(f"  {metric} -> {jp} -> {display}")
                else:
                    for k, v in payload.items():
                        display = v if _to_float(v) is not None else "MISSING"
                        print(f"  {k} -> {k} -> {display}")
                if fails:
                    print(f"  failures: {fails}")


def main() -> None:
    parser = argparse.ArgumentParser(description="LoraMon ETL")
    parser.add_argument("--once", action="store_true", help="Processa apenas um ciclo e sai")
    parser.add_argument("--limit", type=int, default=None, help="Modo dry-run: lê os últimos N registros")
    parser.add_argument("--from-id", type=int, default=None, help="Modo dry-run: começa a partir deste id")
    parser.add_argument("--verbose", action="store_true", help="Logs em nível DEBUG")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if args.limit:
        dry_run(args.limit, args.from_id)
        return

    if args.once:
        run_once()
        return

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
