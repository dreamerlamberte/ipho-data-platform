# Python image shared by the pipeline jobs and the API: generator, ingestion,
# dbt and FastAPI in one reproducible runtime.
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY generator ./generator
COPY ingestion ./ingestion
COPY scripts ./scripts
COPY transform ./transform
COPY api ./api

ENV PYTHONPATH=/app/generator:/app/ingestion:/app/api \
    LAKE_PATH=/data/lake \
    WAREHOUSE_PATH=/data/warehouse/ipho.duckdb

RUN useradd --create-home pipeline && mkdir -p /data && chown -R pipeline /data /app
USER pipeline
