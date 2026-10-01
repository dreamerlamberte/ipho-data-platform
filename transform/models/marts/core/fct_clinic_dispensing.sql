select
    i.dispensing_item_id,
    i.dispensing_id,
    r.visit_id,
    r.patient_key,
    r.dispensed_on,
    i.medicine_id,
    i.qty_dispensed,
    i.qty_dispensed * m.unit_price_php as value_php
from {{ ref('stg_clinic__dispensing_items') }} i
join {{ ref('stg_clinic__dispensing_records') }} r using (dispensing_id)
left join {{ ref('dim_medicine') }} m using (medicine_id)
