{{ config(severity = 'warn') }}
-- Warn when more than 5% of visits carry a diagnosis the mapping seed doesn't
-- recognise — the cue to extend reference/diagnosis_map.csv.
select
    count(*) filter (where diagnosis_name = 'Unclassified') * 1.0 / count(*) as unmapped_share
from {{ ref('fct_consultations') }}
having unmapped_share > 0.05
