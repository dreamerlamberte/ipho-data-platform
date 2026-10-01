with src as ({{ latest_snapshot('inventory', 'medicine') }})

select
    medicine_id,
    trim(description)                          as medicine_name,
    nullif(trim(unit_of_measure), '')          as unit_of_measure,
    cast(nullif(unit_price, '') as decimal(12, 2)) as unit_price_php,
    -- App-maintained aggregates, kept only for reconciliation tests
    cast(nullif(current_qty, '') as decimal(14, 2)) as app_current_qty
from src
