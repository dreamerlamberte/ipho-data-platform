# One-command local pipeline:  make pipeline
# Each target maps to one stage of the platform so it's easy to run in pieces.

SHELL := /bin/bash
ROOT  := $(shell pwd)
export LAKE_PATH      ?= $(ROOT)/data/lake
export WAREHOUSE_PATH ?= $(ROOT)/data/warehouse/ipho.duckdb
export PII_HASH_SALT  ?= local-dev-salt-not-for-production
DBT := uv run dbt --no-use-colors
DBT_ARGS := --project-dir transform --profiles-dir transform

.PHONY: setup generate ingest transform docs test lint pipeline api web clean

setup:          ## install Python + web deps
	uv sync
	cd web && npm install

generate:       ## synthetic IPHO source data → data/source
	PYTHONPATH=generator uv run python -m ipho_synth.generate --out data/source

ingest:         ## data/source → bronze Parquet (PII policy applied)
	PYTHONPATH=ingestion uv run python -m ipho_ingest.extract --source csv

transform:      ## bronze → silver → gold with dbt (models + data tests)
	mkdir -p $(dir $(WAREHOUSE_PATH))
	$(DBT) build $(DBT_ARGS)

docs:           ## generate and serve dbt docs (lineage graph) on :8080
	$(DBT) docs generate $(DBT_ARGS) && $(DBT) docs serve $(DBT_ARGS) --port 8080

api:            ## FastAPI on :8000 (pipeline control enabled for local use)
	ENABLE_PIPELINE_CONTROL=true uv run uvicorn ipho_api.main:app --app-dir api --reload --port 8000

web:            ## Next.js console on :3900 (proxies /api to :8000)
	cd web && npm install && npm run dev

test:           ## Python unit tests
	uv run pytest -q

lint:
	uv run ruff check .

pipeline: generate ingest transform   ## full end-to-end run

clean:
	rm -rf data transform/target
