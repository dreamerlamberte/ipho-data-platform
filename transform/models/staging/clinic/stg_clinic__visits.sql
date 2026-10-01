with src as ({{ latest_snapshot('clinic', 'visits') }})

select
    visit_id,
    patient_id                                              as patient_key,
    cast(visit_date as date)                                as visit_date,
    nullif(lower(trim(chief_complaint)), '')                as chief_complaint,
    nullif(trim(diagnosis), '')                             as diagnosis_text,
    attending_staff                                         as attending_staff_key,
    try_cast(nullif(split_part(blood_pressure, '/', 1), '') as integer) as systolic_bp,
    try_cast(nullif(split_part(blood_pressure, '/', 2), '') as integer) as diastolic_bp,
    try_cast(nullif(temperature_c, '') as decimal(4, 1))   as temperature_c
from src
