with visits as (select * from {{ ref('int_clinic__visits_classified') }}),
     patients as (select * from {{ ref('dim_patient') }}),
     dispensed as (select distinct visit_id from {{ ref('stg_clinic__dispensing_records') }})

select
    v.visit_id,
    v.patient_key,
    v.visit_date,
    p.sex,
    p.municipality,
    year(v.visit_date) - p.birth_year                       as age_at_visit,
    case
        when year(v.visit_date) - p.birth_year < 5  then '0-4'
        when year(v.visit_date) - p.birth_year < 15 then '5-14'
        when year(v.visit_date) - p.birth_year < 25 then '15-24'
        when year(v.visit_date) - p.birth_year < 45 then '25-44'
        when year(v.visit_date) - p.birth_year < 60 then '45-59'
        else '60+'
    end                                                     as age_band,
    v.chief_complaint,
    v.diagnosis_text,
    v.diagnosis_name,
    v.icd10_code,
    v.disease_group,
    v.is_notifiable,
    v.systolic_bp,
    v.diastolic_bp,
    v.temperature_c,
    coalesce(v.systolic_bp >= 140 or v.diastolic_bp >= 90, false) as is_elevated_bp,
    coalesce(v.temperature_c >= 37.5, false)                as is_febrile,
    d.visit_id is not null                                  as had_dispensing
from visits v
left join patients p using (patient_key)
left join dispensed d using (visit_id)
