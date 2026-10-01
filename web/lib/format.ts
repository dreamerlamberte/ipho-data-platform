const nf = new Intl.NumberFormat("en-PH", { maximumFractionDigits: 0 });
const nf1 = new Intl.NumberFormat("en-PH", { maximumFractionDigits: 1 });

export const num = (v: number | null | undefined) => (v == null ? "–" : nf.format(v));
export const num1 = (v: number | null | undefined) => (v == null ? "–" : nf1.format(v));

export function peso(v: number | null | undefined): string {
  if (v == null) return "–";
  if (Math.abs(v) >= 1_000_000) return `₱${nf1.format(v / 1_000_000)}M`;
  if (Math.abs(v) >= 1_000) return `₱${nf1.format(v / 1_000)}k`;
  return `₱${nf.format(v)}`;
}

const df = new Intl.DateTimeFormat("en-PH", { month: "short", day: "numeric", year: "numeric" });
const mf = new Intl.DateTimeFormat("en-PH", { month: "short", year: "2-digit" });
const parse = (iso: string) => new Date(iso.length === 10 ? `${iso}T00:00:00` : iso);

export const day = (iso: string | null | undefined) => (iso ? df.format(parse(iso)) : "–");
export const month = (iso: string) => mf.format(parse(iso));
export const dateTime = (iso: string | null | undefined) =>
  iso ? parse(iso).toLocaleString("en-PH", { dateStyle: "medium", timeStyle: "short" }) : "–";
