import { NextResponse } from "next/server"

// ─────────────────────────────────────────────────────────────
//  /api/marimo — proxy vers le micro-service Python.
//  Demarre (si besoin) le notebook marimo de visualisation et
//  renvoie son URL, que le navigateur ouvre dans un nouvel onglet.
// ─────────────────────────────────────────────────────────────

const ORCHESTRATOR_URL =
  process.env.ORCHESTRATOR_URL ?? "http://127.0.0.1:8077"

// Le premier demarrage de marimo peut prendre quelques secondes.
export const maxDuration = 60

export async function POST() {
  try {
    const res = await fetch(`${ORCHESTRATOR_URL}/marimo`, {
      method: "POST",
      cache: "no-store",
    })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch {
    return NextResponse.json(
      {
        erreur:
          "Service injoignable. Lance le micro-service Python : ./demo.sh",
      },
      { status: 502 },
    )
  }
}
