with src as ({{ latest_snapshot('inventory', 'distribution') }})

select
    distribution_id,
    batch_id,
    event_id,
    cast(nullif(qty_dispensed, '') as decimal(14, 2)) as qty_issued
from src
