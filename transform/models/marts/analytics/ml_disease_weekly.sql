{#- Diagnosis × municipality × week case counts on a complete zero-filled grid
    (a missing week means zero cases, not missing data). Input for outbreak
    anomaly detection such as EARS-C2 / CUSUM. -#}

with weeks as (
    select distinct week_start from {{ ref('dim_date') }}
    where date_day between cast('{{ var("inventory_opening_date") }}' as date)
                       and cast('{{ var("analysis_end_date") }}' as date)
),
grid as (
    select w.week_start, m.municipality, dx.diagnosis_name, dx.disease_group, dx.is_notifiable
    from weeks w
    cross join {{ ref('dim_municipality') }} m
    cross join (select distinct diagnosis_name, disease_group, is_notifiable
                from {{ ref('diagnosis_map') }}) dx
),
cases as (
    select cast(date_trunc('week', visit_date) as date) as week_start,
           municipality, diagnosis_name, count(*) as cases
    from {{ ref('fct_consultations') }}
    group by 1, 2, 3
)

select
    g.week_start,
    g.municipality,
    g.diagnosis_name,
    g.disease_group,
    g.is_notifiable,
    coalesce(c.cases, 0) as cases
from grid g
left join cases c using (week_start, municipality, diagnosis_name)
