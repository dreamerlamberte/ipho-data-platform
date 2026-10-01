{#- Event names are free text ("Allocation - RHU Ipil - Jan 2024"). Recover the
    receiving municipality by matching against the reference list; the longest
    match wins so "Roseller T. Lim" isn't mistaken for a shorter name. -#}

with events as (select * from {{ ref('stg_inventory__distribution_events') }}),
     munis as (select municipality from {{ ref('municipalities') }}),

matches as (
    select
        e.event_id,
        m.municipality,
        row_number() over (partition by e.event_id order by length(m.municipality) desc) as rn
    from events e
    join munis m on contains(lower(e.event_name), lower(m.municipality))
)

select
    e.*,
    coalesce(m.municipality, case when e.distribution_category = 'OPD' then 'Ipil' end)
        as recipient_municipality
from events e
left join matches m on m.event_id = e.event_id and m.rn = 1
