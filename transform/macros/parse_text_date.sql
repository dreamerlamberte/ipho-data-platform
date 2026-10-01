{#- Inventory dates are TEXT. Rows from before the 2025 Google-Sheets →
    Supabase migration use MM/DD/YYYY; newer rows are ISO. Blank → null. -#}
{% macro parse_text_date(column) %}
    cast(try_strptime(nullif(trim({{ column }}), ''), ['%Y-%m-%d', '%m/%d/%Y']) as date)
{% endmacro %}

{% macro is_legacy_date_format(column) %}
    regexp_matches(coalesce({{ column }}, ''), '^\d{2}/\d{2}/\d{4}$')
{% endmacro %}

{#- Supabase timestamps are ISO-8601 with offset; report dates in Philippine time. -#}
{% macro to_pht_date(column) %}
    cast(timezone('Asia/Manila', cast(nullif({{ column }}, '') as timestamptz)) as date)
{% endmacro %}
