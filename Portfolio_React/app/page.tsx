"use client"

import { AnalysisSection } from "@/components/crisis/analysis-section"
import { ContextBanner } from "@/components/crisis/context-banner"
import { DecisionBlock } from "@/components/crisis/decision-block"
import { PerformanceFooter } from "@/components/crisis/performance-footer"
import { ResponseSection } from "@/components/crisis/response-section"
import { useCrisisData } from "@/lib/use-crisis-data"

export default function Page() {
  const { data, loading, source } = useCrisisData()

  return (
    <main className="min-h-screen bg-background">
      <div className="pointer-events-none fixed inset-x-0 top-0 -z-10 h-80 bg-[radial-gradient(60%_100%_at_50%_0%,var(--color-primary)/0.14,transparent_70%)]" />
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6 sm:py-12">
        {loading ? (
          <div className="flex min-h-[60vh] items-center justify-center">
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <span className="size-2 animate-ping rounded-full bg-primary" />
              Analyse de la crise en cours…
            </div>
          </div>
        ) : (
          <>
            <ContextBanner context={data.context} />
            <DecisionBlock decision={data.decision} />
            <ResponseSection response={data.response} />
            <AnalysisSection
              narratives={data.narratives}
              actors={data.actors}
            />
            <PerformanceFooter performance={data.performance} />
            {source === "fallback" ? (
              <p className="text-center font-mono text-xs text-muted-foreground/60">
                données de démonstration · riposte.json introuvable
              </p>
            ) : null}
          </>
        )}
      </div>
    </main>
  )
}
