import {
  Activity,
  BarChart3,
  Loader2,
  MessageSquare,
  Play,
  ShieldAlert,
  TrendingUp,
} from "lucide-react"
import type { CrisisData } from "@/lib/crisis-data"

function Metric({
  icon,
  label,
  value,
  mono = false,
}: {
  icon: React.ReactNode
  label: string
  value: string
  mono?: boolean
}) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-secondary text-primary">
        {icon}
      </div>
      <div className="flex flex-col">
        <span className="text-[0.7rem] uppercase tracking-wide text-muted-foreground">
          {label}
        </span>
        <span
          className={`text-sm font-medium text-foreground ${
            mono ? "font-mono" : ""
          }`}
        >
          {value}
        </span>
      </div>
    </div>
  )
}

export function ContextBanner({
  context,
  onRun,
  running = false,
  onMarimo,
  marimoLoading = false,
}: {
  context: CrisisData["context"]
  onRun?: () => void
  running?: boolean
  onMarimo?: () => void
  marimoLoading?: boolean
}) {
  return (
    <header className="animate-rise rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-sm">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="relative flex size-2.5">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-60" />
            <span className="relative inline-flex size-2.5 rounded-full bg-primary" />
          </span>
          <div>
            <p className="font-mono text-[0.7rem] uppercase tracking-[0.2em] text-primary">
              ● Salle de crise
            </p>
            <h1 className="text-lg font-semibold leading-tight text-foreground text-balance">
              {context.cellLabel}
            </h1>
          </div>
        </div>
        <div className="flex items-center gap-2.5">
          <span className="rounded-full border border-border bg-secondary px-3 py-1 font-mono text-xs text-muted-foreground">
            entité · {context.entity}
          </span>
          {onMarimo ? (
            <button
              type="button"
              onClick={onMarimo}
              disabled={marimoLoading}
              className="inline-flex items-center gap-2 rounded-md border border-border bg-secondary px-3.5 py-2 font-mono text-xs font-medium uppercase tracking-wide text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-60"
            >
              {marimoLoading ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <BarChart3 className="size-3.5" />
              )}
              Dashboard viz
            </button>
          ) : null}
          {onRun ? (
            <button
              type="button"
              onClick={onRun}
              disabled={running}
              className="inline-flex items-center gap-2 rounded-md border border-primary/40 bg-primary/10 px-3.5 py-2 font-mono text-xs font-medium uppercase tracking-wide text-primary transition-colors hover:bg-primary/15 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {running ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <Play className="size-3.5" />
              )}
              {running ? "Analyse en cours…" : "Relancer"}
            </button>
          ) : null}
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-4 border-t border-border pt-5 sm:grid-cols-4">
        <Metric
          icon={<Activity className="size-4" />}
          label="État"
          value={context.state}
        />
        <Metric
          icon={<TrendingUp className="size-4" />}
          label="Sentiment"
          value={context.sentiment}
        />
        <Metric
          icon={<ShieldAlert className="size-4" />}
          label="Agressivité"
          value={context.aggressiveness}
        />
        <Metric
          icon={<MessageSquare className="size-4" />}
          label="Volume"
          value={`${context.volume.toLocaleString("fr-FR")} msg`}
          mono
        />
      </div>
    </header>
  )
}
