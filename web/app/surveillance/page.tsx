"use client";

import { useState } from "react";
import { CasesWithThreshold, Heatmap } from "@/components/charts";
import { Card, ErrorState, Loading, PageHeader, Select, StatTile, Status } from "@/components/ui";
import { useApi } from "@/lib/api";
import { day, num } from "@/lib/format";
import type { Surveillance } from "@/lib/types";

type Options = { diagnoses: { diagnosis_name: string; disease_group: string; is_notifiable: boolean }[]; municipalities: string[] };

export default function SurveillancePage() {
  const opts = useApi<Options>("/surveillance/options");
  const [dx, setDx] = useState("Dengue fever");
  const [muni, setMuni] = useState("All");
  const s = useApi<Surveillance>(`/surveillance?diagnosis=${encodeURIComponent(dx)}&municipality=${encodeURIComponent(muni)}`);

  if (opts.error) return <ErrorState message={opts.error.message} />;
  if (!opts.data) return <Loading />;

  const total = s.data?.weekly.reduce((a, w) => a + w.cases, 0) ?? 0;
  const last = s.data?.weekly.at(-1);
  const notifiable = opts.data.diagnoses.find((d) => d.diagnosis_name === dx)?.is_notifiable;

  return (
    <>
      <PageHeader title="Disease surveillance" subtitle="Weekly outpatient cases with an early-warning threshold (CDC EARS-C2 method)">
        <Select label="Diagnosis" value={dx} onChange={setDx}
          options={opts.data.diagnoses.map((d) => ({ value: d.diagnosis_name, label: d.diagnosis_name + (d.is_notifiable ? " (notifiable)" : "") }))} />
        <Select label="Municipality" value={muni} onChange={setMuni}
          options={[{ value: "All", label: "All municipalities" }, ...opts.data.municipalities.map((m) => ({ value: m, label: m }))]} />
      </PageHeader>

      {s.error ? <ErrorState message={s.error.message} /> : !s.data ? <Loading /> : (
        <>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatTile label="Cases, all weeks" value={num(total)} sub={muni === "All" ? "Province-wide" : muni} />
            <StatTile label="Latest week" value={num(last?.cases)} sub={last ? `Week of ${day(last.week_start)}` : ""} />
            <StatTile label="Alert threshold now" value={last?.threshold == null ? "–" : last.threshold.toFixed(1)} sub="Mean + 3 SD of 7-week baseline" />
            <StatTile label="Alert weeks" value={num(s.data.alerts.length)} sub={notifiable ? "Notifiable disease" : "Not notifiable"} />
          </div>

          <Card title="Weekly cases" className="mt-6"
            caption="A week is flagged when cases exceed the mean + 3 standard deviations of weeks t−8 to t−2 (with at least 3 cases). The 2-week gap stops an emerging outbreak from raising its own baseline.">
            <CasesWithThreshold data={s.data.weekly} />
          </Card>

          <div className="mt-6 grid gap-6 lg:grid-cols-3">
            <Card title="Cases by municipality and month" caption={`${dx}, all municipalities`} className="lg:col-span-2">
              <Heatmap data={s.data.heatmap} />
            </Card>
            <Card title="Flagged weeks" caption="Weeks that crossed the alert threshold">
              {s.data.alerts.length === 0 ? (
                <p className="text-sm text-ink-2">No weeks crossed the threshold.</p>
              ) : (
                <ul className="divide-y divide-[var(--border)] text-sm">
                  {[...s.data.alerts].reverse().map((a) => (
                    <li key={a.week_start} className="flex items-center justify-between py-2">
                      <Status kind="critical">Week of {day(a.week_start)}</Status>
                      <span className="tabular text-ink-2">{num(a.cases)} vs {a.threshold.toFixed(1)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </>
      )}
    </>
  );
}
