import { BadgeCheck, Network, Users } from "lucide-react"
import type {
  Actor,
  CrisisData,
  Narrative,
  NarrativeWeight,
} from "@/lib/crisis-data"

const weightConfig: Record<
  NarrativeWeight,
  { label: string; accent: string; bar: string; dot: string }
> = {
  dominant: {
    label: "Dominant",
    accent: "border-primary/40 bg-primary/10",
    bar: "w-full bg-primary",
    dot: "bg-primary",
  },
  secondaire: {
    label: "Secondaire",
    accent: "border-chart-3/40 bg-chart-3/10",
    bar: "w-2/3 bg-chart-3",
    dot: "bg-chart-3",
  },
  marginal: {
    label: "Marginal",
    accent: "border-border bg-secondary",
    bar: "w-1/3 bg-muted-foreground",
    dot: "bg-muted-foreground",
  },
}

function NarrativeCard({ narrative }: { narrative: Narrative }) {
  const cfg = weightConfig[narrative.weight]
  return (
    <article className={`rounded-2xl border ${cfg.accent} p-4`}>
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-sm font-medium leading-snug text-foreground text-pretty">
          {narrative.label}
        </h3>
        <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-background/50 px-2 py-0.5 text-[0.7rem] uppercase tracking-wide text-muted-foreground">
          <span className={`size-1.5 rounded-full ${cfg.dot}`} />
          {cfg.label}
        </span>
      </div>
      <div className="mt-3 h-1 overflow-hidden rounded-full bg-background/50">
        <div className={`h-full rounded-full ${cfg.bar}`} />
      </div>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {narrative.keywords.map((kw) => (
          <span
            key={kw}
            className="rounded-md bg-background/50 px-2 py-0.5 font-mono text-xs text-muted-foreground"
          >
            {kw}
          </span>
        ))}
      </div>
    </article>
  )
}

function ActorPill({ actor }: { actor: Actor }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card/60 py-1 pl-3 pr-2.5 font-mono text-sm text-foreground transition-colors hover:border-primary/40">
      {actor.handle}
      {actor.certified ? (
        <BadgeCheck className="size-4 text-primary" aria-label="Certifié" />
      ) : (
        <span
          className="size-1.5 rounded-full bg-muted-foreground"
          aria-label="Non certifié"
        />
      )}
    </span>
  )
}

export function AnalysisSection({
  narratives,
  actors,
}: {
  narratives: CrisisData["narratives"]
  actors: CrisisData["actors"]
}) {
  return (
    <section
      aria-label="Analyse de la crise"
      className="animate-rise grid grid-cols-1 gap-6 lg:grid-cols-3"
      style={{ animationDelay: "240ms" }}
    >
      <div className="lg:col-span-2">
        <div className="mb-4 flex items-center gap-2">
          <Network className="size-4 text-primary" />
          <h2 className="text-base font-semibold text-foreground">
            Narratifs détectés
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {narratives.map((n) => (
            <NarrativeCard key={n.label} narrative={n} />
          ))}
        </div>
      </div>

      <div>
        <div className="mb-4 flex items-center gap-2">
          <Users className="size-4 text-primary" />
          <h2 className="text-base font-semibold text-foreground">
            Acteurs clés
          </h2>
        </div>
        <div className="flex flex-wrap gap-2">
          {actors.map((a) => (
            <ActorPill key={a.handle} actor={a} />
          ))}
        </div>
        <p className="mt-4 flex items-center gap-1.5 text-xs text-muted-foreground">
          <BadgeCheck className="size-3.5 text-primary" />
          Compte certifié
        </p>
      </div>
    </section>
  )
}
