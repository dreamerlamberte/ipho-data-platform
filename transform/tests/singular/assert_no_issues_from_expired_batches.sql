{{ config(severity = 'warn') }}
-- Issuing from a batch after its expiry date is a compliance finding, not a
-- pipeline error — so this warns instead of failing the build.
select m.movement_id, m.batch_id, m.movement_date, b.expiry_date
from {{ ref('fct_stock_movements') }} m
join {{ ref('stg_inventory__batches') }} b using (batch_id)
where m.movement_type = 'issue'
  and b.expiry_date is not null
  and m.movement_date > b.expiry_date
