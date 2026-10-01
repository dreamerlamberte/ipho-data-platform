{#- One row per quantity change of a batch: the stock ledger.
    opening  = batches that pre-date the app (no restock record) — opening balance
    receipt  = restock_log entry
    issue    = distribution line (negative), dated by its distribution event
    return   = goods returned to the warehouse (positive) -#}

with batches as (select * from {{ ref('stg_inventory__batches') }}),
     restocks as (select * from {{ ref('stg_inventory__restocks') }}),
     distributions as (select * from {{ ref('stg_inventory__distributions') }}),
     events as (select * from {{ ref('stg_inventory__distribution_events') }}),
     returns_ as (select * from {{ ref('stg_inventory__returns') }})

select
    'OPN-' || b.batch_id                as movement_id,
    b.batch_id,
    b.medicine_id,
    cast('{{ var("inventory_opening_date") }}' as date) as movement_date,
    'opening'                           as movement_type,
    b.beginning_qty                     as qty_change,
    null                                as event_id
from batches b
where not exists (select 1 from restocks r where r.batch_id = b.batch_id)

union all

select
    r.restock_id, r.batch_id, r.medicine_id, r.received_on, 'receipt', r.qty_received, null
from restocks r

union all

select
    d.distribution_id, d.batch_id, b.medicine_id, e.event_date, 'issue', -d.qty_issued, d.event_id
from distributions d
join batches b using (batch_id)
join events e using (event_id)
where d.qty_issued > 0

union all

select
    rt.return_id, rt.batch_id, b.medicine_id, rt.returned_on, 'return', rt.qty_returned, rt.event_id
from returns_ rt
join batches b using (batch_id)
