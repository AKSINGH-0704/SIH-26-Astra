import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import Link from "next/link";

import { Wordmark } from "@/components/wordmark";
import { api, tryFetch } from "@/lib/api";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono-face",
});

export const metadata: Metadata = {
  title: "ASTRA - Proactive Settlement Risk & Relocation Intelligence",
  description:
    "GIS decision support for multi-hazard red zones, carrying capacity assessment and phased relocation prioritisation. Decision-support output; final decisions rest with the SDMA.",
};

const NAV = [
  { href: "/study-area", label: "Study Area & Data", available: true },
  { href: "/model", label: "Model & Provenance", available: true },
  { href: "/command", label: "Command Centre", available: false },
  { href: "/risk", label: "Risk Explorer", available: false },
  { href: "/priority", label: "Habitation Priority", available: false },
  { href: "/sites", label: "Relocation Sites", available: false },
  { href: "/plan", label: "Optimised Plan", available: false },
  { href: "/simulate", label: "What-If Simulation", available: false },
];

async function StatusStrip() {
  const health = await tryFetch(api.health);
  if (!health) {
    return (
      <span className="numeric text-[11px] text-[var(--color-critical)]">
        API UNREACHABLE
      </span>
    );
  }
  const ok = health.status === "ok" && health.fixtures_valid;
  return (
    <div className="flex items-center gap-5 text-[11px]">
      <span className="flex items-center gap-2">
        <span
          aria-hidden
          className="h-1.5 w-1.5 rounded-full"
          style={{
            backgroundColor: ok ? "var(--color-safe)" : "var(--color-warning)",
          }}
        />
        <span className="uppercase tracking-[0.12em] text-[var(--color-ink-muted)]">
          {ok ? "System nominal" : "Degraded"}
        </span>
      </span>
      <span className="text-[var(--color-ink-faint)]">
        Engine <span className="numeric text-[var(--color-ink-muted)]">{health.engine_version}</span>
        <span className="mx-2 text-[var(--color-line-strong)]">|</span>
        Config{" "}
        <span className="numeric text-[var(--color-ink-muted)]">
          {health.model_config_version}
        </span>
        <span className="mx-2 text-[var(--color-line-strong)]">|</span>
        AI explanation{" "}
        <span className="uppercase text-[var(--color-ink-muted)]">
          {health.llm_mode === "connected" ? "Connected" : "Template mode"}
        </span>
      </span>
    </div>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body className="min-h-screen bg-[var(--color-abyss)]">
        <header className="sticky top-0 z-20 border-b border-[var(--color-line)] bg-[var(--color-surface)]/95 backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-4 px-5 py-3">
            <Link href="/model" className="rounded-sm">
              <Wordmark />
            </Link>
            <StatusStrip />
          </div>
        </header>
        <div className="flex min-h-[calc(100vh-64px)] flex-col lg:flex-row">
          <nav
            aria-label="Operational navigation"
            className="border-b border-[var(--color-line)] bg-[var(--color-surface-inset)] px-3 py-3 lg:w-56 lg:shrink-0 lg:border-b-0 lg:border-r"
          >
            <ul className="flex flex-wrap gap-1 lg:flex-col">
              {NAV.map((item) => (
                <li key={item.href}>
                  {item.available ? (
                    <Link
                      href={item.href}
                      className="block rounded px-3 py-2 text-[12px] text-[var(--color-ink)] hover:bg-[var(--color-surface-raised)]"
                    >
                      {item.label}
                    </Link>
                  ) : (
                    <span
                      className="block cursor-not-allowed px-3 py-2 text-[12px] text-[var(--color-ink-faint)]"
                      title="Not yet built. ASTRA does not show a screen before the engine behind it exists."
                    >
                      {item.label}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </nav>
          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
