"use client";

import { BarChart3, Loader2, Play } from "lucide-react";
import { useState } from "react";
import { AnalysisSection } from "@/components/crisis/analysis-section";
import { ContextBanner } from "@/components/crisis/context-banner";
import { DecisionBlock } from "@/components/crisis/decision-block";
import { PerformanceFooter } from "@/components/crisis/performance-footer";
import { ResponseSection } from "@/components/crisis/response-section";
import { useCrisisData } from "@/lib/use-crisis-data";

export default function Page() {
  const { data, running, error, run } = useCrisisData();
  const [marimoLoading, setMarimoLoading] = useState(false);

  async function openMarimo() {
    setMarimoLoading(true);
    try {
      const r = await fetch("/api/marimo", { method: "POST" });
      const j = await r.json();
      if (j?.url) window.open(j.url, "_blank", "noopener");
    } catch {
      // silencieux : le bouton se reactive simplement
    } finally {
      setMarimoLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="pointer-events-none fixed inset-x-0 top-0 -z-10 h-0.5 bg-gradient-to-r from-transparent via-primary/70 to-transparent" />
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6 sm:py-12">
        {data ? (
          <>
            <ContextBanner
              context={data.context}
              onRun={run}
              running={running}
              onMarimo={openMarimo}
              marimoLoading={marimoLoading}
            />
            {error ? (
              <p className="rounded-md border border-danger/40 bg-danger/[0.06] px-4 py-2.5 font-mono text-xs text-danger">
                ⚠ {error}
              </p>
            ) : null}
            <DecisionBlock decision={data.decision} />
            <ResponseSection response={data.response} />
            <AnalysisSection
              narratives={data.narratives}
              actors={data.actors}
            />
            <PerformanceFooter performance={data.performance} />
          </>
        ) : (
          <div className="flex min-h-[72vh] flex-col items-center justify-center text-center">
            <p className="font-mono text-[0.7rem] uppercase tracking-[0.3em] text-primary">
              ● Salle de crise
            </p>
            <h1 className="mt-3 text-2xl font-semibold text-foreground sm:text-3xl">
              Cellule de crise — CNC
            </h1>
            <p className="mt-3 max-w-md text-sm leading-relaxed text-muted-foreground text-pretty">
              Le pipeline d&apos;agents (Analyste → Stratège → Rédacteur)
              n&apos;a pas encore été lancé. Démarre l&apos;orchestrateur pour
              produire une riposte à partir du corpus en temps réel.
            </p>
            <button
              type="button"
              onClick={run}
              disabled={running}
              className="mt-7 inline-flex items-center gap-2.5 rounded-md border border-primary/40 bg-primary/10 px-5 py-3 font-mono text-sm font-medium uppercase tracking-wide text-primary transition-colors hover:bg-primary/15 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {running ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Play className="size-4" />
              )}
              {running
                ? "Analyse de la crise en cours…"
                : "Lancer l'orchestrateur"}
            </button>
            <button
              type="button"
              onClick={openMarimo}
              disabled={marimoLoading}
              className="mt-3 inline-flex items-center gap-2 font-mono text-xs uppercase tracking-wide text-muted-foreground transition-colors hover:text-foreground disabled:opacity-60"
            >
              {marimoLoading ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <BarChart3 className="size-3.5" />
              )}
              ou explorer le corpus (dashboard viz)
            </button>
            {running ? (
              <p className="mt-4 font-mono text-xs text-muted-foreground/70">
                Analyste → Stratège → Rédacteur · ~20 s
              </p>
            ) : null}
            {error ? (
              <p className="mt-4 max-w-md rounded-md border border-danger/40 bg-danger/[0.06] px-4 py-2.5 font-mono text-xs text-danger">
                ⚠ {error}
              </p>
            ) : null}
          </div>
        )}
      </div>
    </main>
  );
}
