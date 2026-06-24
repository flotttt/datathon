# Datathon CNC × Ultia — Agents IA d'analyse de crise

Pipeline d'agents IA pour analyser la crise informationnelle autour de l'affaire **Ultia × CNC** (mars-avril 2026).

## Objectif

Comprendre et outiller la riposte face à un déferlement viral sur X/Twitter, en s'appuyant sur le corpus fourni (`Dataset/data.xlsx`).

Le projet suit la grille d'analyse du brief :

- **Acteurs** : qui parle, qui amplifie ?
- **Narratifs** : quels discours/camps ?
- **Propagation** : pics, patient zéro, vitesse ?
- **Coordination** : signes d'orchestration ?
- **Sémantique** : ton, sentiment, glissements de vocabulaire ?
- **Stratégie** : recommandations d'actions pour la cellule de crise
- **Q&R** : poser des questions au corpus via un RAG sur Chroma DB

## Architecture

```
.
├── data_utils.py              # Chargement / agrégation du corpus
├── chroma_store.py            # Indexation et retrieval Chroma DB
├── agents/
│   ├── model.py               # Factory LLM (Mistral via LangChain)
│   ├── base.py                # Classe de base des agents
│   ├── actors_agent.py        # Agent acteurs
│   ├── narratives_agent.py    # Agent narratifs
│   ├── propagation_agent.py   # Agent propagation
│   ├── coordination_agent.py  # Agent coordination
│   ├── semantic_agent.py      # Agent sémantique
│   ├── qa_agent.py            # Agent Q&A avec RAG Chroma
│   ├── strategist_agent.py    # Agent recommandations
│   └── orchestrator.py        # Orchestrateur multi-agents
├── demo.py                    # Script de démo analyse de crise
├── ask.py                     # Script interactif de Q&R RAG
├── docker-compose.yml         # Chroma DB en conteneur
├── requirements.txt
└── .env.example
```

## Prérequis

- Python 3.10+
- Docker Desktop démarré
- Une clé API Mistral (`MISTRAL_API_KEY`)

## Installation

### 1. Lancer Chroma DB

```bash
docker compose up -d
```

Chroma est accessible sur `http://localhost:8000`.

### 2. Installer les dépendances Python

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

> **Note espace disque** : si l'installation échoue par manque d'espace, les paquets peuvent être installés dans l'environnement Conda/Python actif avec `pip install --no-cache-dir langchain-core langchain-mistralai python-dotenv`.

### 3. Configurer les clés

```bash
cp .env.example .env
# Éditer .env et renseigner MISTRAL_API_KEY
cat .env
```

```dotenv
MISTRAL_API_KEY=ta_cle_mistral_ici
MISTRAL_MODEL=mistral-small-latest   # conseillé pour le free tier
MISTRAL_MAX_RETRIES=5
MISTRAL_RPS=1.0                      # requêtes/sec max
AGENT_DELAY=2.0                      # délai entre agents
DRY_RUN=false
```

> **Free tier Mistral** : les 429 (`Rate limit exceeded`) arrivent vite avec 5 agents. Le repo est configuré par défaut en mode séquentiel + rate limiter + petit modèle. Si vous avez encore des 429, augmentez `AGENT_DELAY` (ex : `5.0`) ou baissez `MISTRAL_RPS` (ex : `0.5`).

## Indexer les tweets dans Chroma

```bash
python chroma_store.py
```

Par défaut, indexe les tweets liés à `ultia` (6 896 tweets). Les embeddings utilisent Mistral si `MISTRAL_API_KEY` est renseignée, sinon Chroma utilise son embedding function locale par défaut.

## Utilisation

### Analyse complète de crise

```bash
python demo.py
```

Le script :
1. Charge le corpus Excel (35 396 posts)
2. Filtre sur le focus `ultia` (6 896 posts)
3. Construit un contexte markdown pour les agents
4. Lance les 5 agents d'analyse séquentiellement
5. Lance l'agent stratège final
6. Génère un rapport JSON + Markdown dans `outputs/`

### Poser des questions au corpus (RAG)

```bash
# Une seule question
python ask.py "Quel est le compte qui a lancé la crise ?"
python ask.py "Quel est le principal reproche fait au CNC ?"

# Mode interactif
python ask.py
```

## Mode test (sans clé API)

Pour vérifier que le pipeline s'exécute sans appeler Mistral :

```bash
DRY_RUN=true python demo.py
```

Les agents retournent alors des sorties factices.

## Livrables générés

- `outputs/context_*.md` : contexte envoyé aux agents
- `outputs/report_*.json` : rapport structuré complet (5 agents + stratège)
- `outputs/report_*.md` : version lisible du rapport

## Axes d'amélioration possibles

- Utiliser les embeddings Mistral (`mistral-embed`) pour un RAG plus précis
- Ajouter des filtres sémantiques dans Chroma (par date, sentiment, auteur)
- Enrichir la détection de coordination avec des mesures de similarité de texte
- Ajouter des visualisations (pics de volume, réseau d'acteurs)
- Brancher l'orchestrateur sur LangGraph pour des workflows plus complexes
