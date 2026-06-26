import { NextResponse } from "next/server"

// ─────────────────────────────────────────────────────────────
//  /api/run — proxy vers le micro-service Python (api_service.py).
//  Le navigateur ne parle qu'a Next ; Next relaie vers FastAPI.
//  URL configurable via ORCHESTRATOR_URL (defaut : localhost:8000).
// ─────────────────────────────────────────────────────────────

const ORCHESTRATOR_URL =
  process.env.ORCHESTRATOR_URL ?? "http://127.0.0.1:8077"

// Le pipeline appelle un LLM : prevoir large.
export const maxDuration = 120

export async function POST() {
  try {
    const res = await fetch(`${ORCHESTRATOR_URL}/run`, {
      method: "POST",
      cache: "no-store",
    })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch {
    return NextResponse.json(
      {
        erreur:
          "Orchestrateur injoignable. Lance le service Python : ./run.sh --api",
      },
      { status: 502 },
    )
  }
}
