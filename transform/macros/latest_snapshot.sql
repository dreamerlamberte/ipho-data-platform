{#- Bronze is append-only: every ingest run writes a full snapshot of each
    source table. Silver reads only the most recent snapshot, which makes
    upstream deletes disappear correctly (a row-level "latest per key" dedup
    would keep deleted rows alive forever). -#}
{% macro latest_snapshot(source_name, table_name) %}
    select *
    from {{ source(source_name, table_name) }}
    where _run_id = (
        select arg_max(_run_id, _ingested_at) from {{ source(source_name, table_name) }}
    )
{% endmacro %}
