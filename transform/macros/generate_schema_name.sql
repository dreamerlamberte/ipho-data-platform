{#- Use the configured schema name as-is (silver / gold / reference) instead of
    dbt's default "<target>_<custom>" prefixing, so layer names stay readable. -#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name if custom_schema_name else target.schema }}
{%- endmacro %}
