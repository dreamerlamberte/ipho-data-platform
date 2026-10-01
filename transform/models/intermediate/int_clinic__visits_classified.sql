with visits as (select * from {{ ref('stg_clinic__visits') }}),
     dx as (select * from {{ ref('diagnosis_map') }})

select
    v.*,
    coalesce(dx.diagnosis_name, 'Unclassified') as diagnosis_name,
    dx.icd10_code,
    coalesce(dx.disease_group, 'unclassified')  as disease_group,
    coalesce(dx.is_notifiable, false)           as is_notifiable
from visits v
left join dx on dx.diagnosis_text = lower(trim(v.diagnosis_text))
