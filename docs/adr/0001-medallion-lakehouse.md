# ADR 0001 — Medallion lakehouse on Parquet + DuckDB, portable to S3 + Athena

**Status:** accepted · 2026-10-01

## Context
IPHO's data lives in several small operational Postgres schemas on a free-tier Supabase
project, plus Excel workbooks. Volumes are modest (tens to hundreds of thousands of rows
per year), budget is close to zero, and the platform has to run on one laptop for
development and in CI.

## Decision
- **Storage:** open-format Parquet files in a bronze / silver / gold layout. Bronze is files
  on disk (S3 in production); silver and gold are built by dbt.
- **Engine:** DuckDB through `dbt-duckdb`. It reads Parquet in place, runs in-process, and
  needs no server.
- **Cloud path:** the same Parquet layout on S3, registered in the Glue Data Catalog and queried
  by Athena (or dbt-athena). Only the dbt profile and the `LAKE_PATH` URI change.

## Consequences
- Zero infrastructure cost locally and in CI; the whole platform builds in seconds.
- Engine and storage are decoupled through open formats, so moving to Athena, Redshift
  Serverless or Spark doesn't mean rewriting the data.
- DuckDB is single-writer: fine for a batch platform, not for concurrent interactive writes.
  Revisit if many analysts need to query the warehouse at once (MotherDuck or Athena).
- Rejected: a Postgres warehouse inside Supabase. It would compete with the operational apps
  for the free-tier database and mixes OLTP and OLAP workloads.
