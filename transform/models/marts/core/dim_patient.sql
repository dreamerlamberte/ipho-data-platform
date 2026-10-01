{#- Pseudonymous patient dimension. No direct identifiers exist upstream;
    barangay is intentionally left out of gold (small-area re-identification risk). -#}
select
    patient_key,
    sex,
    birth_year,
    has_philhealth,
    civil_status,
    occupation,
    municipality,
    registered_on
from {{ ref('stg_clinic__patients') }}
