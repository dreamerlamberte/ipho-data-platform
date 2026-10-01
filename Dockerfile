# Pipeline image: generator, ingestion and dbt in one reproducible runtime.
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

ENV PYTHONPATH=/app/generator:/app/ingestion \
    LAKE_PATH=/data/lake \
    WAREHOUSE_PATH=/data/warehouse/ipho.duckdb

RUN useradd --create-home pipeline && mkdir -p /data && chown -R pipeline /data /app
USER pipeline
