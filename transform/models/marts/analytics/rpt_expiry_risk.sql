{#- Batches still holding stock, ranked by how soon they expire and the peso
    value at risk. Drives the "redistribute before it expires" worklist. -#}

with on_hand as (
    select batch_id, sum(qty_change) as qty_on_hand
    from {{ ref('fct_stock_movements') }}
    group by 1
)

select
    b.batch_id,
    b.medicine_id,
    m.medicine_name,
    b.lot_number,
    b.store_room,
    b.source_of_fund,
    b.expiry_date,
    oh.qty_on_hand,
    oh.qty_on_hand * m.unit_price_php                           as value_on_hand_php,
    date_diff('day', cast('{{ var("analysis_end_date") }}' as date), b.expiry_date) as days_to_expiry,
    case
        when b.expiry_date is null then 'unknown expiry'
        when b.expiry_date <= cast('{{ var("analysis_end_date") }}' as date) then 'expired'
        when b.expiry_date <= cast('{{ var("analysis_end_date") }}' as date) + interval 90 day  then '≤ 90 days'
        when b.expiry_date <= cast('{{ var("analysis_end_date") }}' as date) + interval 180 day then '91–180 days'
        else '> 180 days'
    end                                                         as expiry_bucket
from {{ ref('stg_inventory__batches') }} b
join on_hand oh using (batch_id)
join {{ ref('dim_medicine') }} m using (medicine_id)
where oh.qty_on_hand > 0
