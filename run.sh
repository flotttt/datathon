#!/usr/bin/env bash
#
# run.sh — Lance le pipeline d'agents (Analyste -> Stratege -> Redacteur)
#          et, en option, le dashboard de visualisation.
# Marche pour toute l'equipe : execute-le depuis la racine du projet.
#
#   ./run.sh              # pipeline seul -> ecrit riposte.json
#   ./run.sh --dash       # pipeline PUIS ouvre le dashboard
#   ./run.sh --dash-only  # dashboard seul (reutilise riposte.json existant)
#   ./run.sh --check      # verifie l'environnement, sans appeler le LLM
#
set -euo pipefail

# --- Se placer a la racine du projet (la ou est ce script) ---
cd "$(dirname "$0")"

# --- Chemin du corpus (les modules le lisent via cette variable) ---
export DATATHON_DATA="${DATATHON_DATA:-Dataset/data.xlsx}"

echo "=============================================="
echo "  Pipeline de crise — Ultia x CNC"
echo "=============================================="

# --- 1) Verifier la cle API DeepSeek -------------------------------
# On charge .env s'il existe (sans l'afficher), puis on verifie la cle.
if [ -f .env ]; then
  set -a; source .env; set +a
fi

if [ -z "${DEEPSEEK_API_KEY:-}" ] && [ -z "${LLM_API_KEY:-}" ]; then
  echo "ERREUR : pas de cle API DeepSeek."
  echo "  -> Mets DEEPSEEK_API_KEY dans un fichier .env a la racine,"
  echo "     ou exporte-la : export DEEPSEEK_API_KEY=sk-..."
  echo "     (recupere-la sur platform.deepseek.com)"
  exit 1
fi
echo "[OK] Cle API detectee."

# --- 2) Verifier le corpus -----------------------------------------
if [ ! -f "$DATATHON_DATA" ]; then
  echo "ERREUR : corpus introuvable a '$DATATHON_DATA'."
  echo "  -> Place data.xlsx dans Dataset/, ou ajuste DATATHON_DATA."
  exit 1
fi
echo "[OK] Corpus : $DATATHON_DATA"

# --- 3) Choisir l'interpreteur Python (venv si present) ------------
if [ -d ".venv" ]; then
  PY=".venv/bin/python"
  PIP=".venv/bin/pip"
else
  PY="python3"
  PIP="pip3"
fi

# --- 3bis) Installer les dependances si besoin ---------------------
# On teste un import cle ; s'il manque, on installe requirements.txt.
# Evite de relancer pip a chaque fois (rapide quand tout est deja la).
if ! $PY -c "import langgraph, langchain_openai, pandas, openpyxl, fastapi, uvicorn" 2>/dev/null; then
  echo "[SETUP] Dependances manquantes -> installation (requirements.txt)..."
  $PIP install -q -r requirements.txt
  echo "[OK] Dependances installees."
else
  echo "[OK] Dependances deja presentes."
fi

# --- Mode --api : micro-service HTTP pour le dashboard React --------
if [ "${1:-}" = "--api" ]; then
  PORT="${PORT:-8077}"
  echo "----------------------------------------------"
  echo "[API] Orchestrateur expose sur http://localhost:$PORT"
  echo "      Endpoint : POST /run   (Ctrl+C pour quitter)"
  echo "----------------------------------------------"
  PORT="$PORT" $PY -m uvicorn api_service:app --host 0.0.0.0 --port "$PORT"
  exit 0
fi

# --- Mode --check : on s'arrete avant l'appel LLM ------------------
if [ "${1:-}" = "--check" ]; then
  echo "[CHECK] Verification des imports (sans appel LLM)..."
  $PY -c "import data_loading, metrics, cleaning; from agents import analyste, stratege, redacteur; from contracts import valider_sortie; print('[OK] Tous les modules s\'importent.')"
  echo "Environnement pret. Lance './run.sh' pour le pipeline complet."
  exit 0
fi

# --- Fonction : lance le dashboard marimo --------------------------
lancer_dashboard() {
  if [ ! -f "riposte.json" ]; then
    echo "ERREUR : riposte.json introuvable. Lance d'abord le pipeline (./run.sh)."
    exit 1
  fi
  echo "----------------------------------------------"
  echo "[DASH] Ouverture du dashboard (Ctrl+C pour quitter)..."
  # Chemin absolu : robuste meme si marimo change de repertoire courant.
  RIPOSTE_JSON="$(pwd)/riposte.json" $PY -m marimo run dashboard.py
}

# --- Mode --dash-only : on saute le pipeline -----------------------
if [ "${1:-}" = "--dash-only" ]; then
  lancer_dashboard
  exit 0
fi

# --- 4) Lancer le pipeline -----------------------------------------
echo "[RUN] Lancement du pipeline complet..."
echo "----------------------------------------------"
$PY orchestrateur.py

echo "----------------------------------------------"
echo "[FINI] Resultat ecrit dans riposte.json"

# --- 5) Dashboard si demande ---------------------------------------
if [ "${1:-}" = "--dash" ]; then
  lancer_dashboard
fi
