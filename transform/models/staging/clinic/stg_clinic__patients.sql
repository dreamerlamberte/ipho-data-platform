with src as ({{ latest_snapshot('clinic', 'patients') }})

select
    patient_id                                  as patient_key,   -- HMAC pseudonym
    nullif(sex, '')                             as sex,
    try_cast(nullif(birthdate, '') as integer)  as birth_year,    -- generalized at ingestion
    philhealth_no = 'true'                      as has_philhealth,
    nullif(civil_status, '')                    as civil_status,
    nullif(occupation, '')                      as occupation,
    nullif(trim(barangay), '')                  as barangay,
    nullif(trim(municipality), '')              as municipality,
    {{ to_pht_date('created_at') }}             as registered_on
from src
