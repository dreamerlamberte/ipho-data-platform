export type Overview = {
  data_through: string;
  stock: { usable_value: number; expired_value: number; expiring_90: number | null };
  visits: { last_30: number; prior_30: number };
  stockouts_90d: number;
  weekly_visits: { week: string; visits: number }[];
  top_diagnoses: { diagnosis_name: string; visits: number }[];
  expiry_buckets: { bucket: string; batches: number; units: number; value: number }[];
};

export type Medicine = { medicine_id: string; medicine_name: string; therapeutic_class: string; unit_of_measure: string };

export type Inventory = {
  medicine: Medicine & { unit_price_php: number };
  kpis: { on_hand: number; avg_weekly_issue_12w: number; weeks_of_cover: number | null; stockout_days: number };
  daily: { date_day: string; closing_qty: number; qty_issued: number }[];
  weekly: { week_start: string; qty_issued: number; had_stockout: boolean }[];
};

export type ExpiryRow = {
  batch_id: string; medicine_name: string; lot_number: string; store_room: string; source_of_fund: string;
  expiry_date: string | null; days_to_expiry: number | null; qty_on_hand: number; value_on_hand_php: number; expiry_bucket: string;
};

export type Surveillance = {
  weekly: { week_start: string; cases: number; threshold: number | null; alert: boolean }[];
  alerts: { week_start: string; cases: number; threshold: number }[];
  heatmap: { municipality: string; month: string; cases: number }[];
};

export type Quality = {
  dbt_generated_at: string | null;
  test_summary: Record<string, number>;
  tests: { name: string; status: string; failures: number | null; seconds: number; message: string | null }[];
  ingest_runs: { run_id: string; ingested_at: string; source: string; tables: number; rows: number }[];
  tables: { layer: string; name: string; rows: number | null }[];
};

export type Pipeline = {
  enabled: boolean; stages: string[]; stage: string | null;
  state: "idle" | "running" | "succeeded" | "failed";
  started_at: string | null; finished_at: string | null; log: string[];
};
