-- Source replica of the IPHO Medicine Inventory app (Supabase `public` schema).
-- Table definitions copied verbatim from that repo's supabase/schema.sql;
-- app triggers/functions are omitted because the generator writes final balances.

CREATE TABLE IF NOT EXISTS medicine (
  medicine_id       TEXT PRIMARY KEY,
  description       TEXT NOT NULL,
  unit_of_measure   TEXT DEFAULT '',
  unit_price        NUMERIC DEFAULT 0,
  beginning_qty     NUMERIC DEFAULT 0,
  total_dispensed   NUMERIC DEFAULT 0,
  current_qty       NUMERIC DEFAULT 0,
  -- Movement metrics (recomputed via recompute_all_movement_metrics())
  dispense_rate     NUMERIC DEFAULT 0,
  event_frequency   NUMERIC DEFAULT 0,
  consumption_ratio NUMERIC DEFAULT 0,
  composite_score   NUMERIC DEFAULT 0,
  movement_category TEXT DEFAULT 'Non-Moving'
);

CREATE TABLE IF NOT EXISTS batch (
  batch_id        TEXT PRIMARY KEY,
  medicine_id     TEXT NOT NULL REFERENCES medicine(medicine_id),
  store_room      TEXT DEFAULT '',
  lot_number      TEXT DEFAULT '',
  expiry_date     TEXT DEFAULT '',
  beginning_qty   NUMERIC DEFAULT 0,
  ending_qty      NUMERIC DEFAULT 0,
  total_dispensed NUMERIC DEFAULT 0,
  current_qty     NUMERIC DEFAULT 0,
  source_of_fund  TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS distribution_event (
  event_id              TEXT PRIMARY KEY,
  event_name            TEXT DEFAULT '',
  distribution_category TEXT DEFAULT '',
  event_date            TEXT DEFAULT '',
  doc_release_date      TEXT DEFAULT '',
  transaction_ref       TEXT DEFAULT '',
  CONSTRAINT distribution_event_transaction_ref_unique UNIQUE (transaction_ref)
);

CREATE TABLE IF NOT EXISTS distribution (
  distribution_id TEXT PRIMARY KEY,
  batch_id        TEXT NOT NULL REFERENCES batch(batch_id),
  event_id        TEXT NOT NULL REFERENCES distribution_event(event_id),
  qty_dispensed   NUMERIC DEFAULT 0
);

CREATE TABLE IF NOT EXISTS returns (
  return_id       TEXT PRIMARY KEY,
  distribution_id TEXT DEFAULT '',
  batch_id        TEXT DEFAULT '',
  event_id        TEXT DEFAULT '',
  qty_returned    NUMERIC DEFAULT 0,
  returned_by     TEXT DEFAULT '',
  timestamp       TEXT DEFAULT '',
  notes           TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS restock_log (
  restock_id     TEXT PRIMARY KEY,
  medicine_id    TEXT DEFAULT '',
  quantity_added NUMERIC DEFAULT 0,
  restocked_by   TEXT DEFAULT '',
  timestamp      TEXT DEFAULT '',
  batch_id       TEXT DEFAULT ''
);
