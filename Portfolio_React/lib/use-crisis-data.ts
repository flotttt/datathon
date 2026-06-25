"use client"

import { useEffect, useState } from "react"
import { crisisData as fallbackData, type CrisisData } from "./crisis-data"
import { adaptPipeline } from "./adapt-pipeline"

// ─────────────────────────────────────────────────────────────
//  use-crisis-data.ts
//  Charge riposte.json depuis /public, l'adapte au format dashboard.
//  - pendant le chargement : loading = true
//  - si le fichier manque ou est invalide : on retombe sur les
//    donnees statiques (le portfolio s'affiche TOUJOURS).
// ─────────────────────────────────────────────────────────────

type State = {
  data: CrisisData
  loading: boolean
  source: "live" | "fallback"
}

export function useCrisisData(url = "/riposte.json"): State {
  const [state, setState] = useState<State>({
    data: fallbackData,
    loading: true,
    source: "fallback",
  })

  useEffect(() => {
    let actif = true
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((raw) => {
        if (!actif) return
        setState({ data: adaptPipeline(raw), loading: false, source: "live" })
      })
      .catch(() => {
        // Fichier absent / invalide -> on garde le fallback statique.
        if (!actif) return
        setState({ data: fallbackData, loading: false, source: "fallback" })
      })
    return () => {
      actif = false
    }
  }, [url])

  return state
}
