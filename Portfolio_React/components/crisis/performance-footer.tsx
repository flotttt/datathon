import { Coins, Cpu, Layers, Timer } from "lucide-react"
import type { CrisisData } from "@/lib/crisis-data"

function Stat({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="flex items-center gap-2.5">
      <span className="text-muted-foreground">{icon}</span>
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="font-mono text-xs font-medium text-foreground/80">
        {value}
      </span>
    </div>
  )
}

export function PerformanceFooter({
  performance,
}: {
  performance: CrisisData["performance"]
}) {
  return (
    <footer
      className="animate-rise flex flex-wrap items-center gap-x-6 gap-y-3 border-t border-border pt-5"
      style={{ animationDelay: "320ms" }}
    >
      <span className="text-[0.7rem] uppercase tracking-widest text-muted-foreground/70">
        Performance
      </span>
      <Stat
        icon={<Timer className="size-3.5" />}
        label="Temps"
        value={performance.duration}
      />
      <Stat
        icon={<Cpu className="size-3.5" />}
        label="Tokens"
        value={performance.tokens.toLocaleString("fr-FR")}
      />
      <Stat
        icon={<Coins className="size-3.5" />}
        label="Coût / crise"
        value={performance.costPerCrisis}
      />
      <Stat
        icon={<Layers className="size-3.5" />}
        label="Coût / 1000 crises"
        value={performance.costPer1000}
      />
    </footer>
  )
}
