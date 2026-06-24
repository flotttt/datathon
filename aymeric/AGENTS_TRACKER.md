# Tracker d'idées — Agents IA

| Nom de l'idée | Description | Proposé par | Statut | Faisabilité |
|---|---|---|---|---|
| **Cartographie d'acteurs** | Identifie et catégorise les comptes clés (médias, influenceurs, militants, anonymes, suspects) et leur rôle dans la crise. | Kimi | ✅ Implémenté | Moyen |
| **Classifieur de narratifs** | Range les discours en camps : censure, copinage, défense d'Ultia, cyberharcèlement, etc. | Kimi | ✅ Implémenté | Moyen |
| **Détecteur de pics** | Analyse le volume horaire, identifie les pics viraux et propose l'événement déclencheur. | Kimi | ✅ Implémenté | Facile |
| **Détecteur de coordination** | Repère les signes d'orchestration : comptes récents, copier-coller, synchronisation, clusters. | Kimi | ✅ Implémenté | Moyen |
| **Analyse sémantique** | Étudie le ton, le sentiment, le vocabulaire et les glissements de langage dans le temps. | Kimi | ✅ Implémenté | Facile |
| **Q&R RAG Chroma** | Permet de poser des questions en langage naturel au corpus via un vrai RAG sur Chroma DB. | Kimi | ✅ Implémenté | Moyen |
| **Agent stratège final** | Agrège les analyses de tous les agents et recommande des actions concrètes à la cellule de crise. | Kimi | ✅ Implémenté | Moyen |

## Fichiers correspondants

- `agents/actors_agent.py` → Cartographie d'acteurs
- `agents/narratives_agent.py` → Classifieur de narratifs
- `agents/propagation_agent.py` → Détecteur de pics
- `agents/coordination_agent.py` → Détecteur de coordination
- `agents/semantic_agent.py` → Analyse sémantique
- `agents/qa_agent.py` → Q&R RAG Chroma
- `agents/strategist_agent.py` → Agent stratège final
- `agents/orchestrator.py` → Orchestrateur multi-agents
