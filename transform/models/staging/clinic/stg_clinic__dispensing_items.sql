with src as ({{ latest_snapshot('clinic', 'dispensing_items') }})

select
    cast(item_id as bigint)                         as dispensing_item_id,
    dispensing_id,
    medicine_id,
    medicine_name                                   as medicine_name_snapshot,
    cast(nullif(qty_dispensed, '') as decimal(14, 2)) as qty_dispensed
from src
