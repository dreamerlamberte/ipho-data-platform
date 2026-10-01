import type { Metadata } from "next";
import Nav from "@/components/Nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "IPHO Data Platform",
  description: "Inventory, clinic and surveillance analytics for the Integrated Provincial Health Office.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">
        <Nav />
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</main>
        <footer className="mx-auto max-w-7xl px-4 pb-10 text-xs text-ink-muted sm:px-6">
          Integrated Provincial Health Office · Zamboanga Sibugay · All figures are generated from synthetic data.
        </footer>
      </body>
    </html>
  );
}
