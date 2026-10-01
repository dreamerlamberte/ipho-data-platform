{#- Feature table for demand forecasting: medicine × ISO week issued quantity
    with lag and rolling features. Computed only from past weeks, so it can be
    used for time-based train/test splits without target leakage. -#}

with weekly as (
    select
        s.medicine_id,
        d.week_start,
        sum(s.qty_issued)               as qty_issued,
        min(s.closing_qty)              as min_closing_qty,
        bool_or(s.closing_qty <= 0)     as had_stockout
    from {{ ref('fct_medicine_daily_stock') }} s
    join {{ ref('dim_date') }} d using (date_day)
    group by 1, 2
)

select
    w.medicine_id,
    m.therapeutic_class,
    w.week_start,
    weekofyear(w.week_start)                                        as iso_week,
    month(w.week_start)                                             as month,
    w.qty_issued,
    w.had_stockout,   -- censored demand: issued < true demand when stocked out
    lag(w.qty_issued, 1)  over win                                  as lag_1w,
    lag(w.qty_issued, 2)  over win                                  as lag_2w,
    lag(w.qty_issued, 4)  over win                                  as lag_4w,
    lag(w.qty_issued, 52) over win                                  as lag_52w,
    avg(w.qty_issued) over (win rows between 4 preceding and 1 preceding)  as rolling_mean_4w,
    avg(w.qty_issued) over (win rows between 12 preceding and 1 preceding) as rolling_mean_12w
from weekly w
join {{ ref('dim_medicine') }} m using (medicine_id)
window win as (partition by w.medicine_id order by w.week_start)
