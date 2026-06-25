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
| `agents/redacteur.py` | Agent 3 — Rédacteur (Paulette + Leonardo) |
| `data_loading.py` · `cleaning.py` · `metrics.py` | Modules data partagés (chargement, nettoyage, agrégations) |
| `test_agents.py` | Teste chaque agent **isolément** (preuve que les contrats tiennent) |
| `dashboard.py` | Dashboard de décision (marimo) — lit `riposte.json` |
| `run.sh` | Lanceur tout-en-un (pipeline + dashboard) |
| `Dataset/` | `data.xlsx` (corpus) + dictionnaire |

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

## Lancer (avec run.sh)

Le script gère tout : vérification de la clé, du corpus, installation des
dépendances si besoin, puis lancement.

```bash
chmod +x run.sh        # une seule fois

./run.sh               # pipeline seul → écrit riposte.json
./run.sh --dash        # pipeline PUIS ouvre le dashboard
./run.sh --dash-only   # dashboard seul (réutilise riposte.json existant)
./run.sh --check       # vérifie l'environnement, sans appeler le LLM
```

Lancer la chaîne directement, sans le script :

```bash
python orchestrateur.py
```

Charge le corpus, lance les 3 agents, valide chaque sortie, affiche la riposte
et écrit `riposte.json`.

## Tester les agents un par un

Grâce aux contrats, chaque agent se teste **sans les autres** : on lui donne
une entrée au bon format et on vérifie que sa sortie respecte son contrat.

```bash
python test_agents.py              # teste les 3 agents
python test_agents.py analyste     # un seul agent
python test_agents.py --no-llm     # Analyste sans appel LLM (rapide, gratuit)
```

L'Analyste tourne sur un échantillon du corpus ; le Stratège et le Rédacteur
sur des entrées fixtures, donc indépendamment de l'agent précédent.

## Dashboard de décision (marimo)

```bash
./run.sh --dash-only            # le plus simple (réutilise riposte.json)
# ou directement :
RIPOSTE_JSON=riposte.json python3 -m marimo run dashboard.py
```

Affiche la sortie du pipeline en **pyramide de décision** : la décision en haut
(couleur sémantique), la riposte, puis l'analyse en preuve et le coût en pied.

## Portfolio (React / Next.js)

Une version léchée du dashboard vit dans `Portfolio_react/` (projet Next.js).
Elle lit dynamiquement le `riposte.json` du pipeline :

```bash
cp riposte.json Portfolio_react/public/riposte.json
cd Portfolio_react && npm run dev
```

Le dashboard s'adapte au format du pipeline via `lib/adapt-pipeline.ts` ; si le
fichier est absent, il retombe sur des données de démonstration.
