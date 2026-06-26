"use client"

import { useCallback, useState } from "react"
import { type CrisisData } from "./crisis-data"
import { adaptPipeline } from "./adapt-pipeline"

// ─────────────────────────────────────────────────────────────
//  use-crisis-data.ts
//  Rien n'est affiche au depart : data = null (etat "idle").
//  run() declenche le pipeline live via /api/run (orchestrateur
//  Python) ; les donnees n'apparaissent qu'apres un lancement.
// ─────────────────────────────────────────────────────────────

type State = {
  data: CrisisData | null
  running: boolean
  error: string | null
}

export function useCrisisData() {
  const [state, setState] = useState<State>({
    data: null,
    running: false,
    error: null,
  })

  const run = useCallback(async () => {
    setState((s) => ({ ...s, running: true, error: null }))
    try {
      const r = await fetch("/api/run", { method: "POST" })
      const raw = await r.json()
      if (!r.ok || raw?.erreur) {
        throw new Error(raw?.erreur ?? `HTTP ${r.status}`)
      }
      setState({ data: adaptPipeline(raw), running: false, error: null })
    } catch (e) {
      setState((s) => ({
        ...s,
        running: false,
        error: e instanceof Error ? e.message : "Erreur inconnue",
      }))
    }
  }, [])

  return { ...state, run }
}
