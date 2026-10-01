"""Extract source tables into the bronze layer of the lake.

Bronze is append-only, immutable, and all-string: every run writes a new
Parquet file per table under a Hive-style partition, plus lineage columns.
Typing, parsing and de-duplication happen in dbt (silver), so a schema change
or a malformed value upstream can never make ingestion lose data.

    data/lake/bronze/<system>/<table>/ingest_date=YYYY-MM-DD/<run_id>.parquet

Sources:
  csv       data/source/<system>/<table>.csv   (synthetic data, default)
  postgres  live Supabase/Postgres via SOURCE_PG_DSN. `inventory` maps to the
            `public` schema and `clinic` to the `clinic` schema, matching the
            real IPHO Supabase project.

Usage:  python -m ipho_ingest.extract --source csv
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import yaml

from ipho_ingest.pii import apply_policy

PG_SCHEMA = {"inventory": "public", "clinic": "clinic"}
HERE = Path(__file__).resolve().parent


def _rows_to_table(header: list[str], rows: list[list[str]]) -> pa.Table:
    cols = list(zip(*rows, strict=False)) if rows else [[] for _ in header]
    return pa.table({h: pa.array(c, pa.string()) for h, c in zip(header, cols, strict=False)})


def read_csv(source_dir: Path, system: str, table: str) -> pa.Table:
    with (source_dir / system / f"{table}.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        return _rows_to_table(header, list(reader))


def read_postgres(conn, system: str, table: str) -> pa.Table:
    buf = io.StringIO()
    sql = f'COPY (SELECT * FROM "{PG_SCHEMA[system]}"."{table}") TO STDOUT WITH CSV HEADER'
    with conn.cursor() as cur, cur.copy(sql) as copy:
        for chunk in copy:
            buf.write(bytes(chunk).decode("utf-8"))
    buf.seek(0)
    reader = csv.reader(buf)
    header = next(reader)
    return _rows_to_table(header, list(reader))


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract IPHO sources into bronze Parquet")
    ap.add_argument("--source", choices=["csv", "postgres"], default="csv")
    ap.add_argument("--source-dir", type=Path, default=Path("data/source"))
    ap.add_argument("--lake", type=Path, default=Path(os.environ.get("LAKE_PATH", "data/lake")))
    ap.add_argument("--policy", type=Path, default=HERE.parent / "pii_policy.yml")
    args = ap.parse_args()

    salt = os.environ.get("PII_HASH_SALT", "")
    if not salt:
        raise SystemExit("PII_HASH_SALT is not set — refusing to ingest without a hashing key.")

    policy = yaml.safe_load(args.policy.read_text())["tables"]
    run_id = uuid.uuid4().hex[:12]
    now = datetime.now(UTC)
    conn = None
    if args.source == "postgres":
        import psycopg

        conn = psycopg.connect(os.environ["SOURCE_PG_DSN"])

    manifest = {"run_id": run_id, "ingested_at": now.isoformat(), "source": args.source,
                "tables": {}}
    try:
        for system, tables in policy.items():
            for table, columns in tables.items():
                data = (read_postgres(conn, system, table) if conn
                        else read_csv(args.source_dir, system, table))
                data = apply_policy(data, columns or {}, salt.encode())
                n = data.num_rows
                origin = f"{args.source}:{system}.{table}"
                data = (data
                        .append_column("_ingested_at", pa.array([now.isoformat()] * n))
                        .append_column("_run_id", pa.array([run_id] * n))
                        .append_column("_source", pa.array([origin] * n)))

                out = args.lake / "bronze" / system / table / f"ingest_date={now:%Y-%m-%d}"
                out.mkdir(parents=True, exist_ok=True)
                pq.write_table(data, out / f"{run_id}.parquet", compression="zstd")
                manifest["tables"][f"{system}.{table}"] = n
                print(f"  bronze/{system}/{table:<20} {n:>7,} rows")
    finally:
        if conn:
            conn.close()

    runs = args.lake / "_manifests"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / f"{now:%Y%m%dT%H%M%S}_{run_id}.json").write_text(json.dumps(manifest, indent=2))
    print(f"Ingest run {run_id} complete.")


if __name__ == "__main__":
    main()
