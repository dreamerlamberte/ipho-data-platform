# ADR 0002 — Pseudonymize at ingestion, not in the warehouse

**Status:** accepted · 2026-10-01

## Context
The Outpatient Clinic holds personal and health information, which the Data Privacy Act of
2012 (RA 10173) classes as *sensitive personal information*. The platform feeds BI tools,
ML training, and potentially LLM prompts (NL-to-SQL), each a possible leak path.

## Decision
Apply a column-level **allow-list policy** (`ingestion/pii_policy.yml`) in the extractor,
*before* data is written to bronze:

| Data | Treatment |
|---|---|
| Names, address, contact number, free-text notes | dropped |
| `patient_id`, staff emails | keyed HMAC-SHA256 pseudonym (secret `PII_HASH_SALT`, never in the repo) |
| Birthdate | birth year only; age bands derived in gold |
| PhilHealth number | presence flag |
| Barangay | kept in silver, excluded from gold (small-area re-identification risk) |

Tables missing from the policy are not ingested at all, and the policy fails loudly if it
references a column that no longer exists.

## Consequences
- No raw identifier ever exists in the lake, so lake backups, CI artifacts and ML
  datasets carry no direct identifiers.
- Pseudonyms are stable, so longitudinal analysis (repeat visits, chronic-disease follow-up)
  still works.
- Re-identification requires the HMAC secret *and* the source system, which separates the
  duties of analysts from those of system custodians.
- Trade-off: analysts can never look up an individual patient in the platform. That is
  intentional, because individual care belongs in the clinic app.
- Pseudonymized data is still personal data under RA 10173. Access control on gold is still
  required (Lake Formation / IAM in the AWS phase).
