#!/usr/bin/env bash
#
# demo.sh — Lance TOUTE la demo en une commande :
#           1) l'orchestrateur (API Python, port 8077)
#           2) le dashboard React (Next, port 3000)
#
# Le dashboard reste vide tant qu'on ne clique pas sur
# "Lancer l'orchestrateur". Ctrl+C arrete les deux services.
#
#   ./demo.sh
#
set -euo pipefail
cd "$(dirname "$0")"

export DATATHON_DATA="${DATATHON_DATA:-Dataset/data.xlsx}"
API_PORT="${API_PORT:-8077}"

echo "=============================================="
echo "  Demo Salle de crise — Ultia x CNC"
echo "=============================================="

# --- 1) Cle API ----------------------------------------------------
if [ -f .env ]; then set -a; source .env; set +a; fi
if [ -z "${DEEPSEEK_API_KEY:-}" ] && [ -z "${LLM_API_KEY:-}" ]; then
  echo "ERREUR : pas de cle API. Mets DEEPSEEK_API_KEY dans .env."
  exit 1
fi
echo "[OK] Cle API detectee."

# --- 2) Corpus -----------------------------------------------------
if [ ! -f "$DATATHON_DATA" ]; then
  echo "ERREUR : corpus introuvable a '$DATATHON_DATA'."
  exit 1
fi
echo "[OK] Corpus : $DATATHON_DATA"

# --- 3) Python (venv si present) -----------------------------------
if [ -d .venv ]; then PY=".venv/bin/python"; PIP=".venv/bin/pip"; else PY="python3"; PIP="pip3"; fi
if ! $PY -c "import langgraph, langchain_openai, pandas, openpyxl, fastapi, uvicorn" 2>/dev/null; then
  echo "[SETUP] Installation des dependances Python..."
  $PIP install -q -r requirements.txt
fi
echo "[OK] Dependances Python pretes."

# --- 4) Gestionnaire de paquets Node -------------------------------
if command -v pnpm >/dev/null 2>&1; then PM="pnpm"
elif command -v npm >/dev/null 2>&1; then PM="npm"
else echo "ERREUR : ni pnpm ni npm trouve."; exit 1; fi

if [ ! -d Portfolio_React/node_modules ]; then
  echo "[SETUP] Installation des dependances Node ($PM)..."
  (cd Portfolio_React && $PM install)
fi
echo "[OK] Dependances Node pretes ($PM)."

# --- Arret propre des deux services --------------------------------
API_PID=""
cleanup() {
  echo
  echo "[STOP] Arret des services..."
  [ -n "$API_PID" ] && kill "$API_PID" 2>/dev/null || true
  # marimo est lance par l'API comme process separe -> le tuer aussi.
  pkill -f "marimo run app.py" 2>/dev/null || true
  pkill -f "datathon-viz/.venv/bin/marimo" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# --- 5) Orchestrateur (arriere-plan) -------------------------------
echo "----------------------------------------------"
echo "[API] Orchestrateur -> http://localhost:$API_PORT"
PORT="$API_PORT" $PY -m uvicorn api_service:app --host 0.0.0.0 --port "$API_PORT" \
  >/tmp/orchestrateur-api.log 2>&1 &
API_PID=$!

for _ in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:$API_PORT/health" >/dev/null 2>&1; then
    echo "[API] pret."
    break
  fi
  sleep 0.5
done

# --- 6) Dashboard React (premier plan) -----------------------------
echo "[WEB] Dashboard -> http://localhost:3000"
echo "      (Ctrl+C pour tout arreter)"
echo "----------------------------------------------"
cd Portfolio_React
ORCHESTRATOR_URL="http://127.0.0.1:$API_PORT" $PM run dev
