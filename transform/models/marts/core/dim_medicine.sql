select
    m.medicine_id,
    m.medicine_name,
    m.unit_of_measure,
    m.unit_price_php,
    coalesce(c.therapeutic_class, 'unclassified') as therapeutic_class,
    coalesce(c.item_category, 'medicine')         as item_category
from {{ ref('stg_inventory__medicines') }} m
left join {{ ref('medicine_classification') }} c using (medicine_id)
