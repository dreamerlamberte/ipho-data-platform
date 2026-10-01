# IPHO Data Platform

A centralized, privacy-first data platform for the **Integrated Provincial Health Office (IPHO)
of Zamboanga Sibugay, Philippines**. It consolidates the IPHO's operational systems (medicine
inventory and outpatient clinic, with scorecard and disease surveillance next) into one
modelled, tested, documented warehouse that powers dashboards and AI features.

> **All data in this repository is synthetic.** The generator reproduces the real production
> schemas column-for-column, but no row describes a real patient, staff member or transaction.

```
 OPERATIONAL APPS (Supabase)         INGEST              LAKE + WAREHOUSE                 SERVE
 ───────────────────────────         ──────              ────────────────                 ─────
 Medicine Inventory  (public)  ─┐                    bronze  Parquet, append-only,
 Outpatient Clinic   (clinic)  ─┼─► extract.py ───►          all-string, PII-free
 Scorecard / Surveillance (next)┘   + PII policy        │
                                                        ▼  dbt (DuckDB)
                                                     silver  typed, parsed, de-duplicated
                                                        │
                                                        ▼
                                                     gold    star schema + ML feature tables ──► BI · forecasting · anomaly detection · NL-to-SQL
```

## Quickstart

Requires [uv](https://docs.astral.sh/uv/). No database server needed for the local path.

```bash
make setup      # Python 3.11 env with dbt-duckdb, pyarrow
make pipeline   # generate synthetic sources → ingest to bronze → dbt build (24 models, 3 seeds, 70 tests)
make docs       # dbt docs + lineage graph on http://localhost:8080
```

Or run the full containerized stack, with a real Postgres playing the role of the Supabase source:

```bash
docker compose up --build
```

## What's inside

| Layer | Where | What it does |
|---|---|---|
| Synthetic sources | `generator/` | Seeded, deterministic copy of the Inventory + Clinic databases, ~65k rows across 10 tables. Models seasonality per therapeutic class, FEFO batch picking, restocks, returns, and the real messiness: legacy `MM/DD/YYYY` text dates from the Google Sheets era, free-text diagnoses with spelling variants, blank expiries, zero-qty lines. |
| Ingestion | `ingestion/` | Pulls each table (CSV or live Postgres via `COPY`) into **bronze** Parquet with Hive partitions and lineage columns (`_ingested_at`, `_run_id`, `_source`), and writes a run manifest. Applies an **allow-list PII policy before anything is written**. |
| Privacy | `ingestion/pii_policy.yml` | Names, addresses and contact numbers are dropped. Patient IDs become keyed HMAC-SHA256 pseudonyms, birthdates become birth year, PhilHealth numbers become a yes/no flag. Tables not on the list are never ingested. |
| Silver | `transform/models/staging`, `intermediate` | Typing, multi-format date parsing, latest-snapshot selection, the rebuilt **stock ledger**, recipient municipality recovered from free-text event names, and diagnoses mapped to ICD-10 through a curated seed. |
| Gold | `transform/models/marts` | Star schema (`dim_date`, `dim_medicine`, `dim_municipality`, `dim_patient`, `fct_stock_movements`, `fct_medicine_daily_stock`, `fct_consultations`, `fct_clinic_dispensing`), an expiry-risk worklist, and leakage-safe ML feature tables (`ml_medicine_demand_weekly`, `ml_disease_weekly`). |
| Quality | `transform/tests`, `*.yml` | 70 data tests: keys, referential integrity, accepted values, non-negative balances, and a **ledger reconciliation** test proving the rebuilt ledger matches the app's trigger-maintained balances for every batch. Compliance findings (issuing from expired batches, unmapped diagnoses) *warn* instead of failing the build. |
| CI | `.github/workflows/ci.yml` | Lint, unit tests, full end-to-end pipeline, dbt docs artifact, Docker image build and a Compose run. |

## Design decisions

The reasoning behind the main choices is in [`docs/adr/`](docs/adr):

1. [Medallion lakehouse on Parquet + DuckDB, portable to S3 + Athena](docs/adr/0001-medallion-lakehouse.md)
2. [Pseudonymize at ingestion, not in the warehouse](docs/adr/0002-pseudonymize-at-ingestion.md)
3. [Full snapshots in bronze, latest snapshot in silver](docs/adr/0003-snapshot-ingestion.md)

## Roadmap

See [`docs/roadmap.md`](docs/roadmap.md). In order: orchestration (Dagster) → AI layer
(stockout forecasting, outbreak anomaly detection, NL-to-SQL assistant, tracked in MLflow) →
AWS via Terraform (S3, Glue/Athena, ECR, ECS) → Kubernetes (Helm on k3d, short-lived EKS demo)
→ onboarding the Scorecard and Surveillance sources.
