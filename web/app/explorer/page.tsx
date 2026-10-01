"use client";

import { useState } from "react";
import { Card, ErrorState, Loading, PageHeader } from "@/components/ui";
import { api, useApi } from "@/lib/api";
import { num } from "@/lib/format";

type Schema = { table: string; columns: { name: string; type: string }[] }[];
type Result = { columns: string[]; rows: unknown[][]; truncated: boolean };

const EXAMPLES = [
  { label: "Dengue cases by municipality", sql: "select municipality, sum(cases) as cases\nfrom gold.ml_disease_weekly\nwhere diagnosis_name = 'Dengue fever'\ngroup by 1\norder by 2 desc" },
  { label: "Stock value by fund source", sql: "select source_of_fund, round(sum(value_on_hand_php)) as value_php\nfrom gold.rpt_expiry_risk\ngroup by 1\norder by 2 desc" },
  { label: "Elevated BP by age band", sql: "select age_band,\n       count(*) as visits,\n       round(avg(is_elevated_bp::int) * 100, 1) as pct_elevated_bp\nfrom gold.fct_consultations\ngroup by 1\norder by 1" },
];

export default function ExplorerPage() {
  const schema = useApi<Schema>("/schema");
  const [sql, setSql] = useState(EXAMPLES[0].sql);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [open, setOpen] = useState<string | null>(null);

  async function run() {
    setRunning(true);
    setError(null);
    try {
      setResult(await api<Result>("/sql", { method: "POST", body: JSON.stringify({ sql }) }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setResult(null);
    } finally {
      setRunning(false);
    }
  }

  return (
    <>
      <PageHeader title="SQL explorer"
        subtitle="Query the gold and reference layers with DuckDB SQL. Read-only, no file access, results capped at 1,000 rows." />

      <div className="grid gap-6 lg:grid-cols-[16rem_1fr]">
        <Card title="Tables">
          {schema.error ? <ErrorState message={schema.error.message} /> : !schema.data ? <Loading /> : (
            <ul className="max-h-[32rem] space-y-0.5 overflow-auto text-sm">
              {schema.data.map((t) => (
                <li key={t.table}>
                  <button onClick={() => setOpen(open === t.table ? null : t.table)}
                    className="w-full truncate rounded px-2 py-1 text-left font-mono text-xs hover:bg-hover">
                    {open === t.table ? "▾" : "▸"} {t.table}
                  </button>
                  {open === t.table && (
                    <ul className="mb-2 ml-5 space-y-0.5">
                      <li>
                        <button onClick={() => setSql(`select *\nfrom ${t.table}\nlimit 100`)} className="text-xs text-series hover:underline">
                          Query this table
                        </button>
                      </li>
                      {t.columns.map((c) => (
                        <li key={c.name} className="flex justify-between gap-2 text-xs">
                          <span className="truncate font-mono">{c.name}</span>
                          <span className="text-ink-muted">{c.type.toLowerCase()}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          )}
        </Card>

        <div className="min-w-0 space-y-6">
          <Card>
            <div className="mb-3 flex flex-wrap gap-2">
              {EXAMPLES.map((e) => (
                <button key={e.label} onClick={() => setSql(e.sql)}
                  className="rounded-full border border-hair px-3 py-1 text-xs text-ink-2 hover:bg-hover">
                  {e.label}
                </button>
              ))}
            </div>
            <textarea value={sql} onChange={(e) => setSql(e.target.value)} spellCheck={false} rows={8}
              onKeyDown={(e) => { if ((e.metaKey || e.ctrlKey) && e.key === "Enter") run(); }}
              className="w-full rounded-lg border border-hair bg-page p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-series/40" />
            <div className="mt-3 flex items-center gap-3">
              <button onClick={run} disabled={running || !sql.trim()}
                className="rounded-lg bg-series px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50">
                {running ? "Running…" : "Run query"}
              </button>
              <span className="text-xs text-ink-muted">⌘/Ctrl + Enter</span>
            </div>
            {error && <p className="mt-3 rounded-lg bg-hover p-3 font-mono text-xs text-critical">{error}</p>}
          </Card>

          {result && (
            <Card title={`${num(result.rows.length)} row${result.rows.length === 1 ? "" : "s"}${result.truncated ? " (truncated)" : ""}`}>
              <div className="max-h-[32rem] overflow-auto">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-surface text-left text-xs text-ink-2">
                    <tr className="border-b border-hair">
                      {result.columns.map((c, j) => (
                        <th key={c} className={`py-2 pr-4 font-medium ${typeof result.rows[0]?.[j] === "number" ? "text-right" : ""}`}>{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="tabular">
                    {result.rows.map((r, i) => (
                      <tr key={i} className="border-b border-hair last:border-0 hover:bg-hover">
                        {r.map((v, j) => (
                          <td key={j} className={`py-1.5 pr-4 ${typeof v === "number" ? "text-right" : ""}`}>
                            {v == null ? <span className="text-ink-muted">null</span> : typeof v === "number" ? v.toLocaleString("en-PH") : String(v)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      </div>
    </>
  );
}
