with src as ({{ latest_snapshot('inventory', 'distribution_event') }})

select
    event_id,
    trim(event_name)                                as event_name,
    nullif(trim(distribution_category), '')         as distribution_category,
    {{ parse_text_date('event_date') }}             as event_date,
    {{ parse_text_date('doc_release_date') }}       as doc_release_date,
    {{ is_legacy_date_format('event_date') }}       as event_date_was_legacy_format,
    nullif(trim(transaction_ref), '')               as transaction_ref
from src
