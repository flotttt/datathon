import type { CrisisData, Verdict, NarrativeWeight } from "./crisis-data"

// ─────────────────────────────────────────────────────────────
//  adapt-pipeline.ts
//  Traduit le format produit par le pipeline d'agents (riposte.json)
//  vers le format attendu par le dashboard (CrisisData).
//
//  Le dashboard est le bout de la chaine : c'est LUI qui s'adapte au
//  pipeline, jamais l'inverse. Si le pipeline change un nom de champ,
//  on ne touche qu'ici — les composants ne bougent pas.
// ─────────────────────────────────────────────────────────────

// Forme brute de riposte.json (ce que sort l'orchestrateur Python).
interface PipelineJSON {
  analyse: {
    etat_propagation: string
    ton: { sentiment_global: string; niveau_agressivite: string }
    acteurs_cles: { pseudo: string; type: string; portee: string }[]
    narratifs: { nom: string; poids: string; mots_cles: string[] }[]
  }
  brief: {
    repondre: string // "oui" | "temporiser" | "non"
    timing: string
    cible_narrative: string
    posture: string
    justification: string
    confiance: string // "haute" | "moyenne" | "faible"
    escalade_humaine: boolean
  }
  riposte: {
    messages: string[]
    canal: string
    a_valider_humainement: boolean
  }
  metriques?: Record<
    string,
    { duree_s?: number; total_tokens?: number; input_tokens?: number; output_tokens?: number }
  >
  // certains exports incluent le contexte ; sinon valeurs par defaut.
  contexte?: { entite?: string; messages?: number }
}

// Tarifs DeepSeek ($/million de tokens) — memes constantes que le dashboard marimo.
const PRIX_INPUT = 0.14
const PRIX_OUTPUT = 0.28

// "oui"/"temporiser"/"non" -> verdict du dashboard
function mapVerdict(repondre: string): Verdict {
  switch (repondre) {
    case "oui":
      return "repondre"
    case "temporiser":
      return "temporiser"
    default:
      return "ne-pas-repondre" // "non" et tout autre cas
  }
}

// "haute"/"moyenne"/"faible" -> type attendu par le dashboard
function mapConfiance(c: string): "haute" | "moyenne" | "basse" {
  if (c === "haute") return "haute"
  if (c === "moyenne") return "moyenne"
  return "basse" // "faible" cote pipeline -> "basse" cote dashboard
}

// "dominant"/"secondaire"/"marginal" -> NarrativeWeight (avec garde-fou)
function mapPoids(p: string): NarrativeWeight {
  if (p === "dominant") return "dominant"
  if (p === "marginal") return "marginal"
  return "secondaire"
}

export function adaptPipeline(raw: PipelineJSON): CrisisData {
  const { analyse, brief, riposte, metriques, contexte } = raw

  // --- Performance : on agrege les metriques par agent ---
  const agents = Object.values(metriques ?? {})
  const tokens = agents.reduce((s, m) => s + (m.total_tokens ?? 0), 0)
  const duree = agents.reduce((s, m) => s + (m.duree_s ?? 0), 0)
  const cout = agents.reduce(
    (s, m) =>
      s +
      ((m.input_tokens ?? 0) / 1e6) * PRIX_INPUT +
      ((m.output_tokens ?? 0) / 1e6) * PRIX_OUTPUT,
    0,
  )

  return {
    context: {
      entity: contexte?.entite?.replace(/^.*—\s*/, "") ?? "CNC",
      cellLabel: contexte?.entite ?? "Cellule de crise — CNC",
      state: analyse.etat_propagation,
      sentiment: analyse.ton.sentiment_global,
      aggressiveness: analyse.ton.niveau_agressivite,
      volume: contexte?.messages ?? 0,
    },
    decision: {
      verdict: mapVerdict(brief.repondre),
      target: brief.cible_narrative,
      posture: brief.posture,
      timing: brief.timing,
      confidence: mapConfiance(brief.confiance),
      humanEscalation: brief.escalade_humaine,
      justification: brief.justification,
    },
    response: {
      channel: riposte.canal,
      messages: riposte.messages,
    },
    narratives: analyse.narratifs.map((n) => ({
      label: n.nom,
      weight: mapPoids(n.poids),
      keywords: n.mots_cles,
    })),
    actors: analyse.acteurs_cles.map((a) => ({
      handle: `@${a.pseudo}`,
      certified: a.type === "certifie",
    })),
    performance: {
      duration: `${duree.toFixed(1).replace(".", ",")} s`,
      tokens,
      costPerCrisis: `${cout.toFixed(4).replace(".", ",")} $`,
      costPer1000: `${(cout * 1000).toFixed(2).replace(".", ",")} $`,
    },
  }
}
