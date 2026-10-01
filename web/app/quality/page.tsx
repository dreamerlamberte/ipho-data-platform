"use client";

import { useEffect, useRef, useState } from "react";
import { Card, ErrorState, Loading, PageHeader, StatTile, Status, type StatusKind } from "@/components/ui";
import { api, useApi } from "@/lib/api";
import { dateTime, num } from "@/lib/format";
import type { Pipeline, Quality } from "@/lib/types";

const TEST_STATUS: Record<string, StatusKind> = { pass: "good", warn: "warning", fail: "critical", error: "critical" };
const STAGES: { id: string; label: string; help: string }[] = [
  { id: "all", label: "Run full pipeline", help: "generate → ingest → dbt build" },
  { id: "generate", label: "Generate", help: "Synthetic source data" },
  { id: "ingest", label: "Ingest", help: "Sources → bronze Parquet" },
  { id: "transform", label: "dbt build", help: "Bronze → silver → gold + tests" },
];

export default function QualityPage() {
  const q = useApi<Quality>("/quality");
  const p = useApi<Pipeline>("/pipeline");
  const [runError, setRunError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"issues" | "all">("issues");
  const logRef = useRef<HTMLPreElement>(null);
  const running = p.data?.state === "running";
  const { reload: reloadPipeline } = p;
  const { reload: reloadQuality } = q;

  // Poll while a run is in progress; refresh quality data once it finishes.
  useEffect(() => {
    if (!running) return;
    const t = setInterval(reloadPipeline, 1200);
    return () => {
      clearInterval(t);
      reloadQuality();
    };
  }, [running, reloadPipeline, reloadQuality]);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight });
  }, [p.data?.log.length]);

  async function run(stage: string) {
    setRunError(null);
    try {
      await api("/pipeline/run", { method: "POST", body: JSON.stringify({ stage }) });
      reloadPipeline();
    } catch (e) {
      setRunError(e instanceof Error ? e.message : String(e));
    }
  }

  const tests = q.data?.tests ?? [];
  const shown = filter === "issues" ? tests.filter((t) => t.status !== "pass") : tests;
  const s = q.data?.test_summary ?? {};
  const layers = ["silver", "gold", "reference"].map((l) => ({ layer: l, items: q.data?.tables.filter((t) => t.layer === l) ?? [] }));

  return (
    <>
      <PageHeader title="Pipeline & data quality" subtitle="Run the pipeline, then check dbt test results, ingest runs and warehouse contents" />

      <Card title="Pipeline control">
        {!p.data ? <Loading /> : !p.data.enabled ? (
          <p className="text-sm text-ink-2">
            Running the pipeline from the browser is turned off. Start the API with{" "}
            <code className="rounded bg-hover px-1.5 py-0.5 text-xs">ENABLE_PIPELINE_CONTROL=true</code> (it is on with{" "}
            <code className="rounded bg-hover px-1.5 py-0.5 text-xs">make api</code>), or run{" "}
            <code className="rounded bg-hover px-1.5 py-0.5 text-xs">make pipeline</code> in a terminal.
          </p>
        ) : (
          <>
            <div className="flex flex-wrap gap-2">
              {STAGES.map((st, i) => (
                <button key={st.id} onClick={() => run(st.id)} disabled={running} title={st.help}
                  className={`rounded-lg px-3.5 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${
                    i === 0 ? "bg-series text-white hover:opacity-90" : "border border-hair bg-surface hover:bg-hover"}`}>
                  {st.label}
                </button>
              ))}
              <span className="ml-auto self-center text-sm">
                {p.data.state === "idle" && <Status kind="neutral">No run this session</Status>}
                {p.data.state === "running" && <Status kind="warning">Running {p.data.stage}…</Status>}
                {p.data.state === "succeeded" && <Status kind="good">{p.data.stage} succeeded · {dateTime(p.data.finished_at)}</Status>}
                {p.data.state === "failed" && <Status kind="critical">{p.data.stage} failed · {dateTime(p.data.finished_at)}</Status>}
              </span>
            </div>
            {runError && <p className="mt-3 text-sm text-critical">{runError}</p>}
            {p.data.log.length > 0 && (
              <pre ref={logRef} className="mt-4 max-h-72 overflow-auto rounded-lg bg-hover p-3 text-[11px] leading-relaxed text-ink-2">
                {p.data.log.join("\n")}
              </pre>
            )}
          </>
        )}
      </Card>

      {q.error ? <div className="mt-6"><ErrorState message={q.error.message} /></div> : !q.data ? <Loading /> : (
        <>
          <div className="mt-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatTile label="Tests passing" value={num(s.pass ?? 0)} sub={`of ${num(tests.length)} data tests`} />
            <StatTile label="Warnings" value={num(s.warn ?? 0)} sub="Data findings, build continues" />
            <StatTile label="Failures" value={num((s.fail ?? 0) + (s.error ?? 0))} sub="Block the build" />
            <StatTile label="Last dbt build" value={<span className="text-lg">{dateTime(q.data.dbt_generated_at)}</span>} />
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-3">
            <Card title="dbt data tests" className="lg:col-span-2">
              <div className="mb-3 flex gap-1 text-sm">
                {(["issues", "all"] as const).map((f) => (
                  <button key={f} onClick={() => setFilter(f)}
                    className={`rounded-md px-3 py-1 ${filter === f ? "bg-hover font-medium" : "text-ink-2 hover:bg-hover"}`}>
                    {f === "issues" ? "Warnings & failures" : "All tests"}
                  </button>
                ))}
              </div>
              {shown.length === 0 ? <p className="text-sm text-ink-2">No warnings or failures. 🎉</p> : (
                <div className="max-h-96 overflow-auto">
                  <table className="w-full text-sm">
                    <tbody className="tabular">
                      {shown.map((t) => (
                        <tr key={t.name} className="border-b border-hair last:border-0">
                          <td className="py-2 pr-3"><Status kind={TEST_STATUS[t.status] ?? "neutral"}>{t.status}</Status></td>
                          <td className="py-2 pr-3 font-mono text-xs">{t.name}</td>
                          <td className="py-2 text-right text-xs text-ink-2">{t.failures ? `${num(t.failures)} rows` : ""}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            <Card title="Recent ingest runs" caption="Each run writes a full snapshot to bronze">
              <ul className="divide-y divide-[var(--border)] text-sm">
                {q.data.ingest_runs.map((r) => (
                  <li key={r.run_id} className="py-2">
                    <div className="flex justify-between">
                      <span className="font-mono text-xs">{r.run_id}</span>
                      <span className="text-xs text-ink-2">{r.source}</span>
                    </div>
                    <div className="tabular text-xs text-ink-2">{dateTime(r.ingested_at)} · {r.tables} tables · {num(r.rows)} rows</div>
                  </li>
                ))}
              </ul>
            </Card>
          </div>

          <Card title="Warehouse contents" caption="Silver models are views over bronze Parquet; gold and reference are materialized tables" className="mt-6">
            <div className="grid gap-6 md:grid-cols-3">
              {layers.map(({ layer, items }) => (
                <div key={layer}>
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-2">{layer} · {items.length}</h3>
                  <ul className="space-y-1 text-sm">
                    {items.map((t) => (
                      <li key={t.name} className="flex justify-between gap-2">
                        <span className="truncate font-mono text-xs">{t.name}</span>
                        <span className="tabular text-xs text-ink-2">{t.rows == null ? "view" : num(t.rows)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </>
  );
}
