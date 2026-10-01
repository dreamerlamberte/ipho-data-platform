-- Source replica of the IPHO Outpatient Clinic app (Supabase `clinic` schema).
-- Table definitions copied verbatim from that repo's supabase/schema.sql.

CREATE SCHEMA IF NOT EXISTS clinic;

CREATE TABLE IF NOT EXISTS clinic.patients (
  patient_id     TEXT PRIMARY KEY,        -- PT000001, PT000002…
  last_name      TEXT NOT NULL,
  first_name     TEXT NOT NULL,
  middle_name    TEXT DEFAULT '',
  suffix         TEXT DEFAULT '',
  sex            TEXT DEFAULT '',          -- Male / Female
  birthdate      DATE,
  civil_status   TEXT DEFAULT '',
  occupation     TEXT DEFAULT '',
  address        TEXT DEFAULT '',
  barangay       TEXT DEFAULT '',
  municipality   TEXT DEFAULT '',
  contact_number TEXT DEFAULT '',
  philhealth_no  TEXT DEFAULT '',
  created_at     TIMESTAMPTZ DEFAULT now(),
  created_by     TEXT DEFAULT '',
  updated_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS clinic.visits (
  visit_id        TEXT PRIMARY KEY,        -- V000001, V000002…
  patient_id      TEXT NOT NULL REFERENCES clinic.patients(patient_id),
  visit_date      DATE NOT NULL DEFAULT CURRENT_DATE,
  chief_complaint TEXT DEFAULT '',
  diagnosis       TEXT DEFAULT '',
  attending_staff TEXT DEFAULT '',
  blood_pressure  TEXT DEFAULT '',          -- optional, e.g. "120/80"
  temperature_c   NUMERIC(4,1),             -- optional, body temp in °C
  notes           TEXT DEFAULT '',
  created_at      TIMESTAMPTZ DEFAULT now(),
  created_by      TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS clinic.dispensing_records (
  dispensing_id TEXT PRIMARY KEY,          -- DSP000001, DSP000002…
  visit_id      TEXT NOT NULL REFERENCES clinic.visits(visit_id),
  patient_id    TEXT NOT NULL REFERENCES clinic.patients(patient_id),
  dispensed_by  TEXT DEFAULT '',
  dispensed_at  TIMESTAMPTZ DEFAULT now(),
  notes         TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS clinic.dispensing_items (
  item_id         BIGSERIAL PRIMARY KEY,
  dispensing_id   TEXT NOT NULL REFERENCES clinic.dispensing_records(dispensing_id),
  medicine_id     TEXT NOT NULL,           -- references public.medicine(medicine_id), read-only lookup
  medicine_name   TEXT DEFAULT '',         -- denormalised snapshot for history display
  qty_dispensed   NUMERIC NOT NULL CHECK (qty_dispensed > 0)
);
