import type { StatusKind } from "@/components/ui";

export const EXPIRY_STATUS: Record<string, { kind: StatusKind; label: string }> = {
  expired: { kind: "critical", label: "Expired" },
  "≤ 90 days": { kind: "serious", label: "≤ 90 days" },
  "91–180 days": { kind: "warning", label: "91–180 days" },
  "> 180 days": { kind: "good", label: "> 180 days" },
  "unknown expiry": { kind: "neutral", label: "Unknown expiry" },
};
