import {
  CheckCircle2,
  Clock,
  Crosshair,
  Gauge,
  MessageCircle,
  UserCheck,
} from "lucide-react"
import type { CrisisData, Verdict } from "@/lib/crisis-data"

const verdictConfig: Record<
  Verdict,
  { label: string; tone: string; ring: string; glow: string }
> = {
  repondre: {
    label: "Répondre",
    tone: "text-success",
    ring: "border-success/40 bg-success/10",
    glow: "shadow-[0_0_60px_-15px_var(--color-success)]",
  },
  temporiser: {
    label: "Temporiser",
    tone: "text-warning",
    ring: "border-warning/40 bg-warning/10",
    glow: "shadow-[0_0_60px_-15px_var(--color-warning)]",
  },
  "ne-pas-repondre": {
    label: "Ne pas répondre",
    tone: "text-danger",
    ring: "border-danger/40 bg-danger/10",
    glow: "shadow-[0_0_60px_-15px_var(--color-danger)]",
  },
}

function Attribute({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="rounded-xl border border-border bg-background/40 p-4">
      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}
        <span className="text-[0.7rem] uppercase tracking-wide">{label}</span>
      </div>
      <p className="mt-1.5 text-sm font-medium text-foreground first-letter:uppercase">
        {value}
      </p>
    </div>
  )
}

export function DecisionBlock({
  decision,
}: {
  decision: CrisisData["decision"]
}) {
  const cfg = verdictConfig[decision.verdict]

  return (
    <section
      aria-label="Décision recommandée"
      className={`animate-rise rounded-3xl border ${cfg.ring} ${cfg.glow} p-6 sm:p-8`}
      style={{ animationDelay: "80ms" }}
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <div
            className={`flex size-14 items-center justify-center rounded-2xl border ${cfg.ring} ${cfg.tone}`}
          >
            <CheckCircle2 className="size-7" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-widest text-muted-foreground">
              Décision recommandée
            </p>
            <h2
              className={`text-4xl font-bold leading-none tracking-tight sm:text-5xl ${cfg.tone}`}
            >
              {cfg.label}
            </h2>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border ${cfg.ring} px-3 py-1 text-sm font-medium ${cfg.tone}`}
          >
            <Gauge className="size-3.5" />
            Confiance {decision.confidence}
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-secondary px-3 py-1 text-xs text-muted-foreground">
            <UserCheck className="size-3.5" />
            Escalade humaine&nbsp;:{" "}
            <span className="font-medium text-foreground">
              {decision.humanEscalation ? "oui" : "non"}
            </span>
          </span>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Attribute
          icon={<Crosshair className="size-4" />}
          label="Cible narrative"
          value={decision.target}
        />
        <Attribute
          icon={<MessageCircle className="size-4" />}
          label="Posture"
          value={decision.posture}
        />
        <Attribute
          icon={<Clock className="size-4" />}
          label="Timing"
          value={decision.timing}
        />
      </div>

      <div className="mt-5 rounded-xl border border-border bg-background/40 p-4">
        <p className="text-[0.7rem] uppercase tracking-wide text-muted-foreground">
          Justification
        </p>
        <p className="mt-1.5 text-sm leading-relaxed text-foreground/90 text-pretty">
          {decision.justification}
        </p>
      </div>
    </section>
  )
}
