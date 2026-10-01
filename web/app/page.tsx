"use client";

import { HBar, TimeLine } from "@/components/charts";
import { Card, ErrorState, Loading, PageHeader, StatTile, Status } from "@/components/ui";
import { useApi } from "@/lib/api";
import { EXPIRY_STATUS } from "@/lib/expiry";
import { day, num, peso } from "@/lib/format";
import type { Overview } from "@/lib/types";

export default function OverviewPage() {
  const { data, error } = useApi<Overview>("/overview");
  if (error) return <ErrorState message={error.message} />;
  if (!data) return <Loading />;

  const delta = data.visits.last_30 - data.visits.prior_30;
  return (
    <>
      <PageHeader title="Overview" subtitle={<>Province-wide · data through <b>{day(data.data_through)}</b></>} />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile label="Usable stock value" value={peso(data.stock.usable_value)} sub="Unexpired batches on hand" />
        <StatTile label="Expired stock still on hand" value={peso(data.stock.expired_value)} sub="Not yet written off" />
        <StatTile
          label="Consultations, last 30 days"
          value={num(data.visits.last_30)}
          sub={<span className="tabular">{delta >= 0 ? "▲" : "▼"} {num(Math.abs(delta))} vs prior 30 days</span>}
        />
        <StatTile label="Medicines stocked out" value={num(data.stockouts_90d)} sub="At least once in the last 90 days" />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card title="Weekly consultations" caption="Outpatient clinic visits per week">
          <TimeLine data={data.weekly_visits} x="week" y="visits" yLabel="Consultations" />
        </Card>
        <Card title="Top diagnoses" caption="Consultations in the last 90 days">
          <HBar data={data.top_diagnoses} label="diagnosis_name" value="visits" valueLabel="Consultations" />
        </Card>
      </div>

      <Card title="Where the stock value sits" caption="Batches with stock remaining, grouped by time to expiry" className="mt-6">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-xs text-ink-2">
              <tr className="border-b border-hair">
                <th className="py-2 font-medium">Expiry</th>
                <th className="py-2 text-right font-medium">Batches</th>
                <th className="py-2 text-right font-medium">Units on hand</th>
                <th className="py-2 text-right font-medium">Value</th>
              </tr>
            </thead>
            <tbody className="tabular">
              {data.expiry_buckets.map((b) => {
                const s = EXPIRY_STATUS[b.bucket] ?? { kind: "neutral" as const, label: b.bucket };
                return (
                  <tr key={b.bucket} className="border-b border-hair last:border-0">
                    <td className="py-2"><Status kind={s.kind}>{s.label}</Status></td>
                    <td className="py-2 text-right">{num(b.batches)}</td>
                    <td className="py-2 text-right">{num(b.units)}</td>
                    <td className="py-2 text-right">{peso(b.value)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </>
  );
}
