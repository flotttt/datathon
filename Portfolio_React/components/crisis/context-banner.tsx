import { Activity, MessageSquare, ShieldAlert, TrendingUp } from "lucide-react"
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

export function ContextBanner({ context }: { context: CrisisData["context"] }) {
  return (
    <header className="animate-rise rounded-2xl border border-border bg-card/60 p-5 backdrop-blur-sm">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="relative flex size-2.5">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary opacity-60" />
            <span className="relative inline-flex size-2.5 rounded-full bg-primary" />
          </span>
          <div>
            <p className="text-[0.7rem] uppercase tracking-widest text-muted-foreground">
              Salle de crise
            </p>
            <h1 className="text-lg font-semibold leading-tight text-foreground text-balance">
              {context.cellLabel}
            </h1>
          </div>
        </div>
        <span className="rounded-full border border-border bg-secondary px-3 py-1 font-mono text-xs text-muted-foreground">
          entité · {context.entity}
        </span>
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
