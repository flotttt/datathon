# Datathon — Gérer une crise virale avec des agents IA

Cas : affaire **Ultia × CNC**. On analyse une tempête virale sur X et on outille
la riposte avec une chaîne de 3 agents IA orchestrés.

## Pipeline

```
Corpus (DataFrame)
   → Analyste   (pandas + LLM : narratifs, propagation, acteurs, ton)
   → Stratège   (décision : répondre / temporiser / non, posture, cible)
   → Rédacteur  (messages de riposte, ou note d'attente)
```

Orchestré avec **LangGraph**. Tous les agents partagent un seul LLM
(**DeepSeek**, configuré dans `common.py`) et des **contrats** de données
(`contracts.py`) — chaque binôme bosse sur son agent sans casser les autres.

## Structure

| Élément | Rôle |
| --- | --- |
| `common.py` | Plomberie LLM partagée (clé, `get_llm`, `extraire_json`) |
| `contracts.py` | Les 3 schémas de sortie + `valider_sortie` — **la colonne vertébrale** |
| `orchestrateur.py` | Le chef d'orchestre LangGraph (Analyste → Stratège → Rédacteur) |
| `agents/analyste.py` | Agent 1 — Analyste (Mathis) |
| `agents/stratege.py` | Agent 2 — Stratège (Flo) |
| `agents/redacteur.py` | Agent 3 — Rédacteur (Leo) *(placeholder en attendant sa version)* |
| `data_loading.py` · `cleaning.py` · `metrics.py` | Modules data partagés (chargement, nettoyage, agrégations) |
| `Dataset/` | `data.xlsx` (corpus) + dictionnaire |
| `datathon-viz/` | Analyse descriptive marimo (notebook + dashboard de démo) |

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # puis colle ta clé DeepSeek dans .env
```

`.env` (non versionné) :

```
DEEPSEEK_API_KEY=ta_cle_deepseek
```

## Lancer la chaîne complète

```bash
python orchestrateur.py
```

Charge le corpus, lance les 3 agents, valide chaque sortie, affiche la riposte.

## Visualisations (marimo)

```bash
cd datathon-viz
# voir datathon-viz/README.md
```
