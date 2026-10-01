with src as ({{ latest_snapshot('inventory', 'returns') }})

select
    return_id,
    nullif(distribution_id, '')                     as distribution_id,
    nullif(batch_id, '')                            as batch_id,
    nullif(event_id, '')                            as event_id,
    cast(nullif(qty_returned, '') as decimal(14, 2)) as qty_returned,
    returned_by                                     as returned_by_key,
    {{ to_pht_date('"timestamp"') }}                as returned_on,
    nullif(trim(notes), '')                         as return_reason
from src
