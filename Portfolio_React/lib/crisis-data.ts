export type Verdict = "repondre" | "temporiser" | "ne-pas-repondre"

export type NarrativeWeight = "dominant" | "secondaire" | "marginal"

export interface Narrative {
  label: string
  weight: NarrativeWeight
  keywords: string[]
}

export interface Actor {
  handle: string
  certified: boolean
}

export interface CrisisData {
  context: {
    entity: string
    cellLabel: string
    state: string
    sentiment: string
    aggressiveness: string
    volume: number
  }
  decision: {
    verdict: Verdict
    target: string
    posture: string
    timing: string
    confidence: "haute" | "moyenne" | "basse"
    humanEscalation: boolean
    justification: string
  }
  response: {
    channel: string
    messages: string[]
  }
  narratives: Narrative[]
  actors: Actor[]
  performance: {
    duration: string
    tokens: number
    costPerCrisis: string
    costPer1000: string
  }
}

export const crisisData: CrisisData = {
  context: {
    entity: "CNC",
    cellLabel: "Cellule de crise — CNC",
    state: "traîne",
    sentiment: "neutre",
    aggressiveness: "moyenne",
    volume: 35396,
  },
  decision: {
    verdict: "repondre",
    target: "Dénonciation d'un favoritisme idéologique",
    posture: "factuelle",
    timing: "sous 48h",
    confidence: "haute",
    humanEscalation: false,
    justification:
      "La crise est en phase de latence avec une agressivité modérée, ce qui permet une réponse posée. Une réponse factuelle rappelant les critères objectifs peut couper court aux spéculations.",
  },
  response: {
    channel: "fil",
    messages: [
      "Le CNC applique des critères de sélection transparents et objectifs, définis par la réglementation en vigueur. Les décisions de financement sont fondées sur la qualité artistique, la faisabilité et l'intérêt culturel, sans considération idéologique.",
      "Ces critères sont publics et accessibles à tous. Le CNC réaffirme son engagement en faveur de l'égalité de traitement et de la diversité des projets soutenus. Toute accusation de favoritisme est infondée.",
    ],
  },
  narratives: [
    {
      label: "Dénonciation d'un favoritisme idéologique",
      weight: "dominant",
      keywords: ["favoritisme", "idéologie", "biais", "parti pris"],
    },
    {
      label: "Exigence de transparence du financement public",
      weight: "dominant",
      keywords: ["transparence", "argent public", "critères", "redevabilité"],
    },
    {
      label: "Contestation de la légitimité des bénéficiaires",
      weight: "secondaire",
      keywords: ["légitimité", "bénéficiaires", "mérite"],
    },
    {
      label: "Défense contre les accusations de partialité",
      weight: "marginal",
      keywords: ["défense", "impartialité"],
    },
  ],
  actors: [
    { handle: "@SirAfuera", certified: false },
    { handle: "@LeDindonFiscal", certified: true },
    { handle: "@ojim_france", certified: true },
    { handle: "@jon_delorraine", certified: false },
    { handle: "@anatolium", certified: false },
  ],
  performance: {
    duration: "21,3 s",
    tokens: 3169,
    costPerCrisis: "0,0007 $",
    costPer1000: "0,68 $",
  },
}
