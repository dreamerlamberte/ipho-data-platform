{#- Medicine × day stock position, zero-filled so every day exists. This is the
    canonical input for stock-out analysis and demand forecasting. Note: on-hand
    includes expired-but-not-written-off stock, as the source app does. -#}

with spine as (
    select m.medicine_id, d.date_day
    from {{ ref('dim_medicine') }} m
    cross join {{ ref('dim_date') }} d
    where d.date_day between cast('{{ var("inventory_opening_date") }}' as date)
                         and cast('{{ var("analysis_end_date") }}' as date)
),

daily as (
    select
        medicine_id,
        movement_date                                                   as date_day,
        sum(case when movement_type in ('opening', 'receipt') then qty_change else 0 end) as qty_received,
        sum(case when movement_type = 'issue'  then -qty_change else 0 end)               as qty_issued,
        sum(case when movement_type = 'return' then qty_change else 0 end)                as qty_returned,
        sum(qty_change)                                                                   as net_change
    from {{ ref('fct_stock_movements') }}
    group by 1, 2
)

select
    s.medicine_id,
    s.date_day,
    coalesce(d.qty_received, 0) as qty_received,
    coalesce(d.qty_issued, 0)   as qty_issued,
    coalesce(d.qty_returned, 0) as qty_returned,
    sum(coalesce(d.net_change, 0)) over (
        partition by s.medicine_id order by s.date_day rows unbounded preceding
    )                           as closing_qty
from spine s
left join daily d using (medicine_id, date_day)
