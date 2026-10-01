select
    sm.movement_id,
    sm.batch_id,
    sm.medicine_id,
    sm.movement_date,
    sm.movement_type,
    sm.qty_change,
    sm.qty_change * dm.unit_price_php           as value_change_php,
    sm.event_id,
    e.distribution_category,
    e.recipient_municipality,
    b.source_of_fund
from {{ ref('int_inventory__stock_movements') }} sm
join {{ ref('dim_medicine') }} dm using (medicine_id)
join {{ ref('stg_inventory__batches') }} b using (batch_id)
left join {{ ref('int_inventory__events_enriched') }} e using (event_id)
