# ADR 0003 — Full snapshots in bronze, latest snapshot in silver

**Status:** accepted · 2026-10-01

## Context
The source tables have no reliable `updated_at` column (the Inventory app stores timestamps
as TEXT, and some tables have none), and rows can be hard-deleted by the apps.
Change data capture (logical replication / Debezium) isn't available on the Supabase free tier.

## Decision
Each ingest run writes a **full snapshot** of every allow-listed table to a new, immutable
bronze Parquet file. Silver models read only the most recent `_run_id` per table
(`latest_snapshot` macro).

## Consequences
- Deletes and corrections upstream are reflected correctly. A "latest row per key" dedup
  would keep deleted rows alive forever.
- Bronze keeps full history, so any past state can be rebuilt or audited by pointing silver
  at an older `_run_id`.
- Cost grows linearly with runs × table size. At IPHO volumes that's megabytes. A lifecycle
  rule (S3 → Glacier after 90 days) bounds it in production.
- Revisit with incremental extraction once sources expose a trustworthy change column, or
  CDC once on a paid tier.
