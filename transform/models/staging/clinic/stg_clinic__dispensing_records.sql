with src as ({{ latest_snapshot('clinic', 'dispensing_records') }})

select
    dispensing_id,
    visit_id,
    patient_id                      as patient_key,
    dispensed_by                    as dispensed_by_key,
    {{ to_pht_date('dispensed_at') }} as dispensed_on
from src
