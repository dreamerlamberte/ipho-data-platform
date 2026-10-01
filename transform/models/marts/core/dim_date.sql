with days as (
    select cast(range as date) as date_day
    from range(date '2023-01-01', date '2028-01-01', interval 1 day)
)

select
    date_day,
    cast(strftime(date_day, '%Y%m%d') as integer)   as date_key,
    year(date_day)                                  as year,
    quarter(date_day)                               as quarter,
    month(date_day)                                 as month,
    strftime(date_day, '%b')                        as month_name,
    isoyear(date_day)                               as iso_year,
    weekofyear(date_day)                            as iso_week,
    cast(date_trunc('week', date_day) as date)      as week_start,
    isodow(date_day)                                as iso_day_of_week,
    isodow(date_day) >= 6                           as is_weekend,
    -- PAGASA: southwest monsoon / rainy season roughly June–November
    case when month(date_day) between 6 and 11 then 'wet' else 'dry' end as season
from days
