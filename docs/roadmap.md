# Roadmap

Each phase is shippable on its own and is ordered by portfolio value per hour.

## ✅ Phase 1 — Core data engineering (this commit)
Synthetic sources mirroring the production schemas · PII-safe ingestion to bronze ·
dbt silver/gold star schema · 70 data tests including ledger reconciliation ·
Docker Compose stack with a Postgres source replica · CI.

## ✅ Phase 1b — Web console
FastAPI read-only API + Next.js console (overview, inventory, EARS-C2 surveillance,
pipeline control & data quality, sandboxed SQL explorer), containerized and in Compose.

## Phase 2 — Orchestration & observability
- Dagster: software-defined assets for ingest + `dagster-dbt`, daily schedule, freshness
  policies, asset checks wired to the dbt tests.
- Ingestion run metrics (rows, duration, failures) in Prometheus → Grafana.
- OpenLineage events → Marquez for cross-tool lineage.

## Phase 3 — AI layer (evaluate everything against a baseline)
- **Stockout forecasting** on `ml_medicine_demand_weekly`: seasonal-naïve baseline →
  LightGBM / Prophet. Rolling-origin backtest and MAPE/WAPE per therapeutic class.
  Turn forecasts into reorder points with safety stock. Handle censored demand (`had_stockout`).
- **Outbreak anomaly detection** on `ml_disease_weekly`: CDC EARS-C2 and CUSUM per
  municipality × notifiable disease, with an alert table and a precision check on injected
  synthetic outbreaks.
- **NL-to-SQL assistant** over gold only: an LLM with a read-only DuckDB role and a schema
  allow-list. Evaluated on a hand-written question→SQL test set (execution accuracy).
- MLflow for experiments and the model registry; the forecasting model served as a FastAPI
  container.

## Phase 4 — AWS (Terraform)
S3 lake (bronze/silver/gold buckets, lifecycle rules, SSE-KMS) · Glue Data Catalog + Athena
(dbt-athena target) · ECR · ECS Fargate scheduled task for the pipeline · Secrets Manager
for `PII_HASH_SALT` and the source DSN · GitHub Actions OIDC deploy role (no static keys) ·
budget alarm.

## Phase 5 — Kubernetes
Helm charts for the pipeline job, Dagster, MLflow and the forecasting API. Develop on k3d;
spin up EKS only to record a demo, then `terraform destroy`. The ADR documents why EKS
isn't the always-on target at IPHO's scale and budget.

## Phase 6 — More sources
Scorecard and disease surveillance schemas (after their Supabase migration), LIPH/AOP
Excel workbooks via a file-drop loader, DOH reference data.
