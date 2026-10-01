import Link from "next/link";
import type { ReactNode } from "react";

export function PageHeader({ title, subtitle, children }: { title: string; subtitle?: ReactNode; children?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-ink-2">{subtitle}</p>}
      </div>
      {children && <div className="flex flex-wrap items-end gap-3">{children}</div>}
    </div>
  );
}

export function Card({ title, caption, children, className = "" }: { title?: string; caption?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-xl border border-hair bg-surface p-5 ${className}`}>
      {title && <h2 className="text-sm font-semibold">{title}</h2>}
      {caption && <p className="mt-0.5 text-xs text-ink-2">{caption}</p>}
      <div className={title || caption ? "mt-4" : ""}>{children}</div>
    </section>
  );
}

export function StatTile({ label, value, sub, help }: { label: string; value: ReactNode; sub?: ReactNode; help?: string }) {
  return (
    <div className="rounded-xl border border-hair bg-surface p-4" title={help}>
      <div className="text-xs text-ink-2">{label}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight">{value}</div>
      {sub && <div className="mt-1 text-xs text-ink-2">{sub}</div>}
    </div>
  );
}

export function Select<T extends string>({ label, value, onChange, options }: {
  label: string; value: T; onChange: (v: T) => void; options: { value: T; label: string }[];
}) {
  return (
    <label className="flex flex-col gap-1 text-xs text-ink-2">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="min-w-[12rem] rounded-lg border border-hair bg-surface px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-series/40"
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </label>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return <div className="py-16 text-center text-sm text-ink-muted">{label}</div>;
}

export function ErrorState({ message }: { message: string }) {
  const notBuilt = /not built|rebuilt/i.test(message);
  return (
    <div className="rounded-xl border border-hair bg-surface p-6 text-sm">
      <p className="font-medium">{notBuilt ? "No data yet" : "Couldn't load data"}</p>
      <p className="mt-1 text-ink-2">{message}</p>
      {notBuilt && (
        <Link href="/quality" className="mt-3 inline-block text-series hover:underline">
          Go to Pipeline &amp; data quality →
        </Link>
      )}
    </div>
  );
}

/** Status pill: color is never alone — always an icon glyph + label. */
const STATUS = {
  good: { cls: "text-good", icon: "●" },
  warning: { cls: "text-warning", icon: "▲" },
  serious: { cls: "text-serious", icon: "◆" },
  critical: { cls: "text-critical", icon: "■" },
  neutral: { cls: "text-ink-muted", icon: "○" },
} as const;
export type StatusKind = keyof typeof STATUS;

export function Status({ kind, children }: { kind: StatusKind; children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 whitespace-nowrap">
      <span className={`text-[10px] ${STATUS[kind].cls}`} aria-hidden>{STATUS[kind].icon}</span>
      <span>{children}</span>
    </span>
  );
}
