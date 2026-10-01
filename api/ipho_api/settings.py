"""Runtime configuration from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _path(env: str, default: Path) -> Path:
    value = os.environ.get(env)
    return Path(value) if value else default


LAKE_PATH = _path("LAKE_PATH", ROOT / "data" / "lake")
WAREHOUSE_PATH = _path("WAREHOUSE_PATH", ROOT / "data" / "warehouse" / "ipho.duckdb")
SOURCE_DIR = _path("SOURCE_DIR", ROOT / "data" / "source")
DBT_PROJECT = _path("DBT_PROJECT", ROOT / "transform")
INGEST_SOURCE = os.environ.get("INGEST_SOURCE", "csv")

# Running pipeline stages from the browser is a local/demo convenience. It is
# off unless explicitly enabled, and never exposed in a production deployment.
PIPELINE_CONTROL = os.environ.get("ENABLE_PIPELINE_CONTROL", "false").lower() == "true"
SQL_ROW_LIMIT = int(os.environ.get("SQL_ROW_LIMIT", "1000"))
