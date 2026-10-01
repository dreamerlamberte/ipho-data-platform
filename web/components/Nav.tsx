"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Overview" },
  { href: "/inventory", label: "Inventory" },
  { href: "/surveillance", label: "Surveillance" },
  { href: "/quality", label: "Pipeline & quality" },
  { href: "/explorer", label: "SQL explorer" },
];

export default function Nav() {
  const path = usePathname();
  return (
    <header className="sticky top-0 z-20 border-b border-hair bg-page/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span className="grid h-7 w-7 place-items-center rounded-md bg-series text-xs text-white">IP</span>
          IPHO Data Platform
        </Link>
        <nav className="order-last -mx-1 flex w-full gap-1 overflow-x-auto text-sm md:order-none md:w-auto md:flex-1">
          {LINKS.map((l) => {
            const active = l.href === "/" ? path === "/" : path.startsWith(l.href);
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`whitespace-nowrap rounded-md px-3 py-1.5 ${active ? "bg-hover font-medium text-ink" : "text-ink-2 hover:bg-hover"}`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>
        <span className="ml-auto rounded-full border border-hair px-2.5 py-0.5 text-xs text-ink-2 md:ml-0">Synthetic data</span>
      </div>
    </header>
  );
}
