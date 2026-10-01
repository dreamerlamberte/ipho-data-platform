-- The rebuilt stock ledger must agree with the Inventory app's own
-- batch.current_qty (maintained by its Postgres triggers). A mismatch means
-- either a movement type we don't model yet or a trigger drift in the app.
with ledger as (
    select batch_id, sum(qty_change) as ledger_qty
    from {{ ref('fct_stock_movements') }}
    group by 1
)
select b.batch_id, b.app_current_qty, coalesce(l.ledger_qty, 0) as ledger_qty
from {{ ref('stg_inventory__batches') }} b
left join ledger l using (batch_id)
where abs(b.app_current_qty - coalesce(l.ledger_qty, 0)) > 0.001
