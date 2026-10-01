with src as ({{ latest_snapshot('inventory', 'restock_log') }})

select
    restock_id,
    medicine_id,
    nullif(batch_id, '')                                as batch_id,
    cast(nullif(quantity_added, '') as decimal(14, 2))  as qty_received,
    restocked_by                                        as restocked_by_key,
    {{ to_pht_date('"timestamp"') }}                    as received_on
from src
