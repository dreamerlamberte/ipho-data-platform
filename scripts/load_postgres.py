"""Load the synthetic CSVs into the Postgres source replica (docker compose).

Uses COPY, so it loads ~65k rows in well under a second. Tables are truncated
first, so it's safe to re-run.
"""

from __future__ import annotations

import os
from pathlib import Path

import psycopg

ORDER = {
    "public": ["medicine", "batch", "distribution_event", "distribution", "returns",
               "restock_log"],
    "clinic": ["patients", "visits", "dispensing_records", "dispensing_items"],
}
DIRS = {"public": "inventory", "clinic": "clinic"}


def main() -> None:
    src = Path(os.environ.get("SOURCE_DIR", "data/source"))
    with psycopg.connect(os.environ["SOURCE_PG_DSN"]) as conn, conn.cursor() as cur:
        all_tables = [f'"{s}"."{t}"' for s, ts in ORDER.items() for t in ts]
        cur.execute(f"TRUNCATE {', '.join(all_tables)} CASCADE")
        for schema, tables in ORDER.items():
            for table in tables:
                path = src / DIRS[schema] / f"{table}.csv"
                header = path.open(encoding="utf-8").readline().strip()
                sql = (f'COPY "{schema}"."{table}" ({header}) FROM STDIN '
                       "WITH (FORMAT csv, HEADER true, NULL '')")
                with path.open("rb") as f, cur.copy(sql) as copy:
                    while chunk := f.read(1 << 16):
                        copy.write(chunk)
                print(f"  loaded {schema}.{table}")
    print("Source replica loaded.")


if __name__ == "__main__":
    main()
