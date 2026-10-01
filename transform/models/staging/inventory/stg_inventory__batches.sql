with src as ({{ latest_snapshot('inventory', 'batch') }})

select
    batch_id,
    medicine_id,
    nullif(trim(store_room), '')                    as store_room,
    nullif(trim(lot_number), '')                    as lot_number,
    {{ parse_text_date('expiry_date') }}            as expiry_date,
    {{ is_legacy_date_format('expiry_date') }}      as expiry_date_was_legacy_format,
    nullif(trim(source_of_fund), '')                as source_of_fund,
    cast(nullif(beginning_qty, '') as decimal(14, 2))   as beginning_qty,
    cast(nullif(current_qty, '') as decimal(14, 2))     as app_current_qty
from src
