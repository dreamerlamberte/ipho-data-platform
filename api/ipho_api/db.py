"""Read-only access to the DuckDB warehouse.

Each request opens and closes its own read-only connection instead of holding
one open, so a dbt build (which needs the write lock) can run alongside the API.
"""

from __future__ import annotations

import math
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import duckdb
from fastapi import HTTPException

from ipho_api.settings import WAREHOUSE_PATH


def _clean(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, datetime | date):
        return value.isoformat()
    return value


def _connect(sandboxed: bool = False) -> duckdb.DuckDBPyConnection:
    if not WAREHOUSE_PATH.exists():
        raise HTTPException(503, "Warehouse not built yet. Run the pipeline first.")
    config = {"enable_external_access": False} if sandboxed else {}
    try:
        return duckdb.connect(str(WAREHOUSE_PATH), read_only=True, config=config)
    except duckdb.IOException as exc:  # write lock held by a running dbt build
        raise HTTPException(503, "Warehouse is being rebuilt. Try again in a moment.") from exc


def rows(sql: str, params: list | tuple = (), sandboxed: bool = False) -> list[dict]:
    with _connect(sandboxed) as conn:
        cur = conn.execute(sql, list(params))
        cols = [d[0] for d in cur.description]
        return [{c: _clean(v) for c, v in zip(cols, r, strict=True)} for r in cur.fetchall()]


def one(sql: str, params: list | tuple = ()) -> dict:
    result = rows(sql, params)
    return result[0] if result else {}


def columns_and_rows(sql: str, limit: int) -> tuple[list[str], list[list]]:
    """User-written SQL: read-only, no file/network access, row-capped."""
    wrapped = f"select * from ({sql.strip().rstrip(';')}) as q limit {int(limit) + 1}"
    with _connect(sandboxed=True) as conn:
        cur = conn.execute(wrapped)
        cols = [d[0] for d in cur.description]
        return cols, [[_clean(v) for v in r] for r in cur.fetchall()]
