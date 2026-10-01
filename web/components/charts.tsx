"use client";

import type { ReactNode } from "react";
import {
  Area, Bar, BarChart, CartesianGrid, Cell, ComposedChart, Line, ResponsiveContainer,
  Scatter, Tooltip, XAxis, YAxis,
} from "recharts";
import { day, month, num } from "@/lib/format";

// Shared chart chrome: hairline solid grid, recessive axes, text in ink tokens.
const AXIS = { stroke: "var(--axis)", tick: { fill: "var(--muted)", fontSize: 11 }, tickLine: false };
const GRID = <CartesianGrid stroke="var(--grid)" vertical={false} />;

export function TooltipBox({ title, rows }: { title: string; rows: { label: string; value: ReactNode; swatch?: string }[] }) {
  return (
    <div className="rounded-lg border border-hair bg-surface px-3 py-2 text-xs shadow-sm">
      <div className="mb-1 font-medium text-ink">{title}</div>
      {rows.map((r) => (
        <div key={r.label} className="flex items-center justify-between gap-4 text-ink-2">
          <span className="flex items-center gap-1.5">
            {r.swatch && <span className="h-2 w-2 rounded-full" style={{ background: r.swatch }} />}
            {r.label}
          </span>
          <span className="tabular font-medium text-ink">{r.value}</span>
        </div>
      ))}
    </div>
  );
}

export function Legend({ items }: { items: { label: string; color: string; shape?: "dot" | "line" | "dash" }[] }) {
  return (
    <div className="mb-2 flex flex-wrap gap-4 text-xs text-ink-2">
      {items.map((i) => (
        <span key={i.label} className="flex items-center gap-1.5">
          {i.shape === "line" || i.shape === "dash" ? (
            <svg width="16" height="6" aria-hidden>
              <line x1="0" y1="3" x2="16" y2="3" stroke={i.color} strokeWidth="2" strokeDasharray={i.shape === "dash" ? "4 3" : undefined} />
            </svg>
          ) : (
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: i.color }} />
          )}
          {i.label}
        </span>
      ))}
    </div>
  );
}

type Row = Record<string, unknown>;

/** Single-series time line (or area) with a crosshair tooltip. */
export function TimeLine<T extends Row>({ data, x, y, yLabel, height = 260, area = false }: {
  data: T[]; x: keyof T & string; y: keyof T & string; yLabel: string; height?: number; area?: boolean;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data as Row[]} margin={{ top: 8, right: 8, bottom: 0, left: -8 }}>
        {GRID}
        <XAxis dataKey={x as string} {...AXIS} tickFormatter={month} minTickGap={40} />
        <YAxis {...AXIS} axisLine={false} tickFormatter={num} width={56} />
        <Tooltip
          cursor={{ stroke: "var(--muted)", strokeWidth: 1 }}
          content={({ active, payload }) =>
            active && payload?.length ? (
              <TooltipBox title={day(String(payload[0].payload[x]))} rows={[{ label: yLabel, value: num(Number(payload[0].payload[y])) }]} />
            ) : null
          }
        />
        {area ? (
          <Area dataKey={y as string} type="linear" stroke="var(--series-1)" strokeWidth={2} fill="var(--series-1)" fillOpacity={0.12} isAnimationActive={false} activeDot={{ r: 4, stroke: "var(--surface)", strokeWidth: 2 }} />
        ) : (
          <Line dataKey={y as string} type="linear" stroke="var(--series-1)" strokeWidth={2} dot={false} isAnimationActive={false} activeDot={{ r: 4, stroke: "var(--surface)", strokeWidth: 2 }} />
        )}
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/** Horizontal single-series bar list, rounded at the data end. */
export function HBar<T extends Row>({ data, label, value, valueLabel, height }: {
  data: T[]; label: keyof T & string; value: keyof T & string; valueLabel: string; height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height ?? data.length * 34 + 24}>
      <BarChart data={data as Row[]} layout="vertical" margin={{ top: 0, right: 40, bottom: 0, left: 0 }} barCategoryGap={8}>
        <XAxis type="number" hide />
        <YAxis type="category" dataKey={label as string} width={210} {...AXIS} axisLine={false} tick={{ fill: "var(--ink-2)", fontSize: 12 }} />
        <Tooltip
          cursor={{ fill: "var(--hover)" }}
          content={({ active, payload }) =>
            active && payload?.length ? (
              <TooltipBox title={String(payload[0].payload[label])} rows={[{ label: valueLabel, value: num(Number(payload[0].payload[value])) }]} />
            ) : null
          }
        />
        <Bar dataKey={value as string} fill="var(--series-1)" radius={[0, 4, 4, 0]} isAnimationActive={false}
          label={{ position: "right", fill: "var(--ink-2)", fontSize: 11, formatter: (v: unknown) => num(Number(v)) }} />
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Weekly bars where a status flag recolors the bar (status color + legend label). */
export function StatusBars<T extends Row>({ data, x, y, flag, yLabel, flagLabel, height = 220 }: {
  data: T[]; x: keyof T & string; y: keyof T & string; flag: keyof T & string; yLabel: string; flagLabel: string; height?: number;
}) {
  return (
    <>
      <Legend items={[{ label: "In stock", color: "var(--series-1)" }, { label: flagLabel, color: "var(--critical)" }]} />
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data as Row[]} margin={{ top: 8, right: 8, bottom: 0, left: -8 }} barCategoryGap={1}>
          {GRID}
          <XAxis dataKey={x as string} {...AXIS} tickFormatter={month} minTickGap={40} />
          <YAxis {...AXIS} axisLine={false} tickFormatter={num} width={56} />
          <Tooltip
            cursor={{ fill: "var(--hover)" }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const p = payload[0].payload as T;
              return (
                <TooltipBox title={`Week of ${day(String(p[x]))}`} rows={[
                  { label: yLabel, value: num(Number(p[y])) },
                  { label: "Status", value: p[flag] ? flagLabel : "In stock" },
                ]} />
              );
            }}
          />
          <Bar dataKey={y as string} radius={[2, 2, 0, 0]} isAnimationActive={false}>
            {data.map((d, i) => (
              <Cell key={i} fill={d[flag] ? "var(--critical)" : "var(--series-1)"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </>
  );
}

/** Weekly cases + EARS-C2 alert threshold + alert markers, one shared axis (same unit). */
export function CasesWithThreshold({ data, height = 280 }: {
  data: { week_start: string; cases: number; threshold: number | null; alert: boolean }[]; height?: number;
}) {
  const alerts = data.map((d) => ({ ...d, alertCases: d.alert ? d.cases : null }));
  return (
    <>
      <Legend items={[
        { label: "Weekly cases", color: "var(--series-1)", shape: "line" },
        { label: "Alert threshold", color: "var(--muted)", shape: "dash" },
        { label: "Above threshold", color: "var(--critical)" },
      ]} />
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={alerts} margin={{ top: 8, right: 8, bottom: 0, left: -8 }}>
          {GRID}
          <XAxis dataKey="week_start" {...AXIS} tickFormatter={month} minTickGap={40} />
          <YAxis {...AXIS} axisLine={false} allowDecimals={false} width={56} />
          <Tooltip
            cursor={{ stroke: "var(--muted)", strokeWidth: 1 }}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const p = payload[0].payload as (typeof alerts)[number];
              return (
                <TooltipBox title={`Week of ${day(p.week_start)}`} rows={[
                  { label: "Cases", value: num(p.cases), swatch: "var(--series-1)" },
                  { label: "Threshold", value: p.threshold == null ? "building baseline" : p.threshold.toFixed(1), swatch: "var(--muted)" },
                  ...(p.alert ? [{ label: "Status", value: "Above threshold", swatch: "var(--critical)" }] : []),
                ]} />
              );
            }}
          />
          <Line dataKey="threshold" stroke="var(--muted)" strokeWidth={1.5} strokeDasharray="4 3" dot={false} connectNulls={false} isAnimationActive={false} activeDot={false} />
          <Line dataKey="cases" stroke="var(--series-1)" strokeWidth={2} dot={false} isAnimationActive={false} activeDot={{ r: 4, stroke: "var(--surface)", strokeWidth: 2 }} />
          <Scatter dataKey="alertCases" fill="var(--critical)" stroke="var(--surface)" strokeWidth={2} isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </>
  );
}

/** Municipality × month heatmap on a one-hue sequential ramp, with hover tooltip. */
export function Heatmap({ data }: { data: { municipality: string; month: string; cases: number }[] }) {
  const rows = Array.from(new Set(data.map((d) => d.municipality)));
  const cols = Array.from(new Set(data.map((d) => d.month))).sort();
  const lookup = new Map(data.map((d) => [`${d.municipality}|${d.month}`, d.cases]));
  const max = Math.max(1, ...data.map((d) => d.cases));
  const step = (v: number) => (v === 0 ? 0 : Math.min(7, 1 + Math.floor((v / max) * 6.999)));

  return (
    <div>
      <div className="overflow-x-auto">
        <div className="grid min-w-[40rem] gap-[2px] text-[11px]" style={{ gridTemplateColumns: `8.5rem repeat(${cols.length}, minmax(10px, 1fr))` }}>
          {rows.map((r) => (
            <div key={r} className="contents">
              <div className="truncate pr-2 text-ink-2">{r}</div>
              {cols.map((c) => {
                const v = lookup.get(`${r}|${c}`) ?? 0;
                return (
                  <div key={c} className="group relative h-5 rounded-[3px]" style={{ background: `var(--seq-${step(v)})` }}>
                    <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-1 hidden -translate-x-1/2 group-hover:block">
                      <TooltipBox title={`${r} · ${month(c)}`} rows={[{ label: "Cases", value: num(v) }]} />
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
          <div />
          {cols.map((c, i) => (
            <div key={c} className="whitespace-nowrap pt-1 text-ink-muted">{i % 3 === 0 ? month(c) : ""}</div>
          ))}
        </div>
      </div>
      <div className="mt-3 flex items-center gap-2 text-xs text-ink-2">
        <span>0</span>
        {Array.from({ length: 8 }, (_, i) => (
          <span key={i} className="h-3 w-5 rounded-[2px]" style={{ background: `var(--seq-${i})` }} />
        ))}
        <span>{num(max)} cases / month</span>
      </div>
    </div>
  );
}
