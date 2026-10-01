"""IPHO Data Platform API — read-only JSON over the gold layer.

    uv run uvicorn ipho_api.main:app --app-dir api --reload --port 8000
"""

from __future__ import annotations

import json
from typing import Literal

import duckdb
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from ipho_api import db
from ipho_api.pipeline import STAGES, job
from ipho_api.settings import (
    DBT_PROJECT,
    LAKE_PATH,
    PIPELINE_CONTROL,
    SQL_ROW_LIMIT,
    WAREHOUSE_PATH,
)

app = FastAPI(title="IPHO Data Platform API", version="0.1.0",
              description="Read-only access to the IPHO gold layer. All data is synthetic.")

EXPIRY_ORDER = """case expiry_bucket when 'expired' then 0 when '≤ 90 days' then 1
                  when '91–180 days' then 2 when '> 180 days' then 3 else 4 end"""


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "warehouse_ready": WAREHOUSE_PATH.exists(),
            "pipeline_control": PIPELINE_CONTROL}


# ── Overview ────────────────────────────────────────────────────────────────

@app.get("/api/overview")
def overview() -> dict:
    end = db.one("select max(visit_date) as d from gold.fct_consultations")["d"]
    stock = db.one("""
        select sum(value_on_hand_php) filter (where expiry_bucket <> 'expired') as usable_value,
               sum(value_on_hand_php) filter (where expiry_bucket = 'expired')  as expired_value,
               sum(value_on_hand_php) filter (where expiry_bucket = '≤ 90 days') as expiring_90
        from gold.rpt_expiry_risk""")
    visits = db.one("""
        select count(*) filter (where visit_date >  cast(? as date) - interval 30 day) as last_30,
               count(*) filter (where visit_date <= cast(? as date) - interval 30 day
                                  and visit_date >  cast(? as date) - interval 60 day) as prior_30
        from gold.fct_consultations""", (end, end, end))
    stockouts = db.one("""
        select count(distinct medicine_id) as n from gold.fct_medicine_daily_stock
        where closing_qty <= 0
          and date_day > (select max(date_day) from gold.fct_medicine_daily_stock) - interval 90 day
    """)["n"]
    weekly = db.rows("""
        select cast(date_trunc('week', visit_date) as date) as week, count(*) as visits
        from gold.fct_consultations
        group by 1
        having week + interval 6 day <= cast(? as date)   -- complete weeks only
        order by 1""", (end,))
    top = db.rows("""
        select diagnosis_name, count(*) as visits from gold.fct_consultations
        where visit_date > cast(? as date) - interval 90 day
        group by 1 order by 2 desc limit 8""", (end,))
    buckets = db.rows(f"""
        select expiry_bucket as bucket, count(*) as batches, sum(qty_on_hand) as units,
               sum(value_on_hand_php) as value
        from gold.rpt_expiry_risk group by 1 order by {EXPIRY_ORDER}""")
    return {"data_through": end, "stock": stock, "visits": visits, "stockouts_90d": stockouts,
            "weekly_visits": weekly, "top_diagnoses": top, "expiry_buckets": buckets}


# ── Inventory ───────────────────────────────────────────────────────────────

@app.get("/api/medicines")
def medicines() -> list[dict]:
    return db.rows("select medicine_id, medicine_name, therapeutic_class, unit_of_measure "
                   "from gold.dim_medicine order by medicine_name")


@app.get("/api/inventory/{medicine_id}")
def inventory(medicine_id: str) -> dict:
    med = db.one("select * from gold.dim_medicine where medicine_id = ?", (medicine_id,))
    if not med:
        raise HTTPException(404, "Unknown medicine")
    daily = db.rows("select date_day, closing_qty, qty_issued from gold.fct_medicine_daily_stock "
                    "where medicine_id = ? order by date_day", (medicine_id,))
    weekly = db.rows("select week_start, qty_issued, had_stockout "
                     "from gold.ml_medicine_demand_weekly where medicine_id = ? "
                     "order by week_start", (medicine_id,))
    recent = [w["qty_issued"] for w in weekly[-12:]]
    avg_week = sum(recent) / len(recent) if recent else 0
    on_hand = daily[-1]["closing_qty"] if daily else 0
    return {
        "medicine": med,
        "kpis": {
            "on_hand": on_hand,
            "avg_weekly_issue_12w": avg_week,
            "weeks_of_cover": (on_hand / avg_week) if avg_week else None,
            "stockout_days": sum(1 for d in daily if d["closing_qty"] <= 0),
        },
        "daily": daily,
        "weekly": weekly,
    }


@app.get("/api/expiry")
def expiry(include_long: bool = False) -> list[dict]:
    where = "" if include_long else "where expiry_bucket <> '> 180 days'"
    return db.rows(f"""
        select batch_id, medicine_name, lot_number, store_room, source_of_fund, expiry_date,
               days_to_expiry, qty_on_hand, value_on_hand_php, expiry_bucket
        from gold.rpt_expiry_risk {where}
        order by expiry_date nulls first""")


# ── Surveillance ────────────────────────────────────────────────────────────

@app.get("/api/surveillance/options")
def surveillance_options() -> dict:
    return {
        "diagnoses": db.rows("select distinct diagnosis_name, disease_group, is_notifiable "
                             "from gold.ml_disease_weekly order by 1"),
        "municipalities": [r["municipality"] for r in
                           db.rows("select municipality from gold.dim_municipality order by 1")],
    }


@app.get("/api/surveillance")
def surveillance(diagnosis: str, municipality: str = "All") -> dict:
    """Weekly cases with a CDC EARS-C2 style alert threshold: mean + 3·sd of the
    7 weeks ending 2 weeks before the current one (the guard band keeps an
    emerging outbreak from inflating its own baseline)."""
    muni_filter = "" if municipality == "All" else "and municipality = ?"
    params: list = [diagnosis] + ([] if municipality == "All" else [municipality])
    weekly = db.rows(f"""
        with series as (
            select week_start, sum(cases) as cases
            from gold.ml_disease_weekly
            where diagnosis_name = ? {muni_filter}
            group by 1
        ), baseline as (
            select *,
                avg(cases)          over w as base_mean,
                stddev_samp(cases)  over w as base_sd,
                count(*)            over w as base_n
            from series
            window w as (order by week_start rows between 8 preceding and 2 preceding)
        )
        select week_start, cases,
               case when base_n = 7 then base_mean + 3 * greatest(base_sd, 0.5) end as threshold
        from baseline order by week_start""", params)
    for w in weekly:
        w["alert"] = w["threshold"] is not None and w["cases"] > w["threshold"] and w["cases"] >= 3

    heatmap = db.rows("""
        select municipality, cast(date_trunc('month', week_start) as date) as month,
               sum(cases) as cases
        from gold.ml_disease_weekly where diagnosis_name = ?
        group by 1, 2 order by 1, 2""", (diagnosis,))
    return {"weekly": weekly, "alerts": [w for w in weekly if w["alert"]], "heatmap": heatmap}


# ── Platform: pipeline & data quality ──────────────────────────────────────

@app.get("/api/quality")
def quality() -> dict:
    results_path = DBT_PROJECT / "target" / "run_results.json"
    tests: list[dict] = []
    summary: dict[str, int] = {}
    generated_at = None
    if results_path.exists():
        results = json.loads(results_path.read_text())
        generated_at = results["metadata"]["generated_at"]
        for r in results["results"]:
            uid = r["unique_id"]
            kind = uid.split(".")[0]
            if kind != "test":
                continue
            tests.append({"name": uid.split(".")[2], "status": r["status"],
                          "failures": r.get("failures"), "seconds": round(r["execution_time"], 3),
                          "message": r.get("message")})
            summary[r["status"]] = summary.get(r["status"], 0) + 1
    tests.sort(key=lambda t: ({"fail": 0, "error": 1, "warn": 2}.get(t["status"], 3), t["name"]))

    manifests = []
    for p in sorted((LAKE_PATH / "_manifests").glob("*.json"), reverse=True)[:10]:
        m = json.loads(p.read_text())
        manifests.append({"run_id": m["run_id"], "ingested_at": m["ingested_at"],
                          "source": m["source"], "tables": len(m["tables"]),
                          "rows": sum(m["tables"].values())})

    tables: list[dict] = []
    if WAREHOUSE_PATH.exists():
        try:
            tables = db.rows("""
                select schema_name as layer, table_name as name, estimated_size as rows
                from duckdb_tables() where schema_name in ('gold', 'reference')
                union all
                select schema_name, view_name, null from duckdb_views()
                where schema_name = 'silver'
                order by 1, 2""")
        except HTTPException:
            tables = []
    return {"dbt_generated_at": generated_at, "test_summary": summary, "tests": tests,
            "ingest_runs": manifests, "tables": tables}


class RunRequest(BaseModel):
    stage: Literal["generate", "ingest", "transform", "all"]


@app.get("/api/pipeline")
def pipeline_status() -> dict:
    return {"enabled": PIPELINE_CONTROL, "stages": [s for s in STAGES if s != "all"],
            **job.status()}


@app.post("/api/pipeline/run", status_code=202)
def pipeline_run(req: RunRequest) -> dict:
    if not PIPELINE_CONTROL:
        raise HTTPException(403, "Pipeline control is disabled (ENABLE_PIPELINE_CONTROL).")
    if not job.start(req.stage):
        raise HTTPException(409, "A pipeline run is already in progress.")
    return job.status()


# ── SQL explorer ────────────────────────────────────────────────────────────

@app.get("/api/schema")
def schema() -> list[dict]:
    cols = db.rows("""
        select table_schema, table_name, column_name, data_type
        from information_schema.columns
        where table_schema in ('gold', 'reference')
        order by table_schema, table_name, ordinal_position""")
    out: dict[str, dict] = {}
    for c in cols:
        key = f"{c['table_schema']}.{c['table_name']}"
        out.setdefault(key, {"table": key, "columns": []})["columns"].append(
            {"name": c["column_name"], "type": c["data_type"]})
    return list(out.values())


class SqlRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=10_000)


@app.post("/api/sql")
def run_sql(req: SqlRequest, limit: int = Query(SQL_ROW_LIMIT, le=SQL_ROW_LIMIT)) -> dict:
    try:
        cols, data = db.columns_and_rows(req.sql, limit)
    except duckdb.Error as exc:
        raise HTTPException(400, str(exc).split("\n")[0]) from exc
    return {"columns": cols, "rows": data[:limit], "truncated": len(data) > limit}
