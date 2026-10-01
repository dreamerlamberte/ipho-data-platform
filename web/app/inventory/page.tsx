"use client";

import { useEffect, useMemo, useState } from "react";
import { StatusBars, TimeLine } from "@/components/charts";
import { Card, ErrorState, Loading, PageHeader, Select, StatTile, Status } from "@/components/ui";
import { useApi } from "@/lib/api";
import { EXPIRY_STATUS } from "@/lib/expiry";
import { day, num, num1, peso } from "@/lib/format";
import type { ExpiryRow, Inventory, Medicine } from "@/lib/types";

export default function InventoryPage() {
  const meds = useApi<Medicine[]>("/medicines");
  const [cls, setCls] = useState("all");
  const [medId, setMedId] = useState("");
  const [includeLong, setIncludeLong] = useState(false);

  const classes = useMemo(() => Array.from(new Set(meds.data?.map((m) => m.therapeutic_class) ?? [])).sort(), [meds.data]);
  const pool = useMemo(() => (meds.data ?? []).filter((m) => cls === "all" || m.therapeutic_class === cls), [meds.data, cls]);

  useEffect(() => {
    if (pool.length && !pool.some((m) => m.medicine_id === medId)) setMedId(pool[0].medicine_id);
  }, [pool, medId]);

  const inv = useApi<Inventory>(medId ? `/inventory/${encodeURIComponent(medId)}` : null);
  const expiry = useApi<ExpiryRow[]>(`/expiry?include_long=${includeLong}`);

  if (meds.error) return <ErrorState message={meds.error.message} />;
  if (!meds.data) return <Loading />;

  const k = inv.data?.kpis;
  return (
    <>
      <PageHeader title="Inventory" subtitle="Stock position, demand and expiry risk per medicine">
        <Select label="Therapeutic class" value={cls} onChange={setCls}
          options={[{ value: "all", label: "All classes" }, ...classes.map((c) => ({ value: c, label: c.replace("_", " ") }))]} />
        <Select label="Medicine" value={medId} onChange={setMedId}
          options={pool.map((m) => ({ value: m.medicine_id, label: m.medicine_name }))} />
      </PageHeader>

      {inv.error ? <ErrorState message={inv.error.message} /> : !inv.data || !k ? <Loading /> : (
        <>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatTile label="On hand" value={num(k.on_hand)} sub={inv.data.medicine.unit_of_measure} />
            <StatTile label="Avg weekly issue" value={num(k.avg_weekly_issue_12w)} sub="Last 12 weeks" />
            <StatTile label="Weeks of cover" value={k.weeks_of_cover == null ? "–" : num1(k.weeks_of_cover)} sub="On hand ÷ avg weekly issue" />
            <StatTile label="Days stocked out" value={num(k.stockout_days)} sub="Since the ledger opened" />
          </div>
          <div className="mt-6 grid gap-6">
            <Card title="Stock on hand" caption="Daily closing balance from the rebuilt stock ledger">
              <TimeLine data={inv.data.daily} x="date_day" y="closing_qty" yLabel="Units on hand" area height={240} />
            </Card>
            <Card title="Weekly quantity issued"
              caption="Weeks marked as stocked out understate true demand, because stock ran out before requests could be filled.">
              <StatusBars data={inv.data.weekly} x="week_start" y="qty_issued" flag="had_stockout" yLabel="Units issued" flagLabel="Stocked out that week" />
            </Card>
          </div>
        </>
      )}

      <Card title="Expiry worklist" caption="Batches with stock remaining, soonest expiry first. Redistribute or use these before they expire." className="mt-6">
        <label className="mb-3 flex items-center gap-2 text-sm text-ink-2">
          <input type="checkbox" checked={includeLong} onChange={(e) => setIncludeLong(e.target.checked)} className="accent-[var(--series-1)]" />
          Include batches with more than 180 days left
        </label>
        {expiry.error ? <ErrorState message={expiry.error.message} /> : !expiry.data ? <Loading /> : (
          <>
            <div className="max-h-[28rem] overflow-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-surface text-left text-xs text-ink-2">
                  <tr className="border-b border-hair">
                    {["Status", "Medicine", "Batch / lot", "Store room", "Fund", "Expiry", "Days left", "On hand", "Value"].map((h, i) => (
                      <th key={h} className={`py-2 pr-3 font-medium ${i >= 6 ? "text-right" : ""}`}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="tabular">
                  {expiry.data.map((r) => {
                    const s = EXPIRY_STATUS[r.expiry_bucket] ?? { kind: "neutral" as const, label: r.expiry_bucket };
                    return (
                      <tr key={r.batch_id} className="border-b border-hair last:border-0 hover:bg-hover">
                        <td className="py-2 pr-3"><Status kind={s.kind}>{s.label}</Status></td>
                        <td className="py-2 pr-3">{r.medicine_name}</td>
                        <td className="py-2 pr-3 text-ink-2">{r.batch_id} · {r.lot_number}</td>
                        <td className="py-2 pr-3 text-ink-2">{r.store_room}</td>
                        <td className="py-2 pr-3 text-ink-2">{r.source_of_fund}</td>
                        <td className="py-2 pr-3">{day(r.expiry_date)}</td>
                        <td className="py-2 pr-3 text-right">{r.days_to_expiry == null ? "–" : num(r.days_to_expiry)}</td>
                        <td className="py-2 pr-3 text-right">{num(r.qty_on_hand)}</td>
                        <td className="py-2 text-right">{peso(r.value_on_hand_php)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-xs text-ink-2">
              {num(expiry.data.length)} batches · {peso(expiry.data.reduce((s, r) => s + r.value_on_hand_php, 0))} in view
            </p>
          </>
        )}
      </Card>
    </>
  );
}
