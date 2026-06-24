"""
agents/stratege.py — AGENT 2 : LE STRATÈGE (Directeur de com)
Binôme : Flo + 1

RÔLE : aide à la décision. Il TRANCHE et JUSTIFIE — il ne rédige pas.
ENTRÉE : la sortie de l'Analyste (dict ANALYSTE_SCHEMA).
SORTIE : le dict STRATEGE_SCHEMA (voir contracts.py).

Il répond aux 5 questions d'un directeur de com :
  1. Faut-il répondre ?  2. Quand ?  3. Quel narratif contrer ?
  4. Quel ton ?  5. Pourquoi ? (+ confiance + escalade humaine)

GARDE-FOU : au pic, ou si confiance faible -> temporiser + escalade humaine.

À FAIRE par le binôme : affiner le PROMPT + tester les règles de décision
sur plusieurs cas (pic vs traîne, narratif agressif vs calme).
"""
import json
from common import get_llm, extraire_json

PROMPT_STRATEGE = """Tu es un directeur de la communication de crise. On te donne l'analyse
d'une crise sur X. Tu CONSEILLES un décideur humain : tu tranches et tu justifies.
Tu ne rédiges AUCUN message — ce n'est pas ton rôle.

Voici l'analyse (JSON) :
{analyse}

Décide et renvoie UNIQUEMENT un objet JSON, sans texte autour, structure EXACTE :

{{
  "repondre": "oui|temporiser|non",
  "timing": "<quand agir, en une phrase>",
  "cible_narrative": "<le narratif à contrer en priorité>",
  "posture": "factuel|apaisant|ferme",
  "justification": "<2-3 phrases : pourquoi cette reco>",
  "confiance": "haute|moyenne|faible",
  "escalade_humaine": true
}}

Règles de décision :
- Si etat_propagation = "pic" : privilégie "temporiser" (répondre au pic jette de l'huile sur le feu).
- Si etat_propagation = "traine" : une mise au point posée peut clore le sujet -> "oui" possible.
- Si niveau_agressivite = "eleve" : posture "apaisant" ou "factuel", jamais "ferme".
- escalade_humaine = true si propagation = "pic" OU confiance = "faible".
- Cible TOUJOURS le narratif "dominant" en priorité.
"""


def run(analyse: dict) -> dict:
    llm = get_llm(temperature=0.2)
    prompt = PROMPT_STRATEGE.format(analyse=json.dumps(analyse, ensure_ascii=False, indent=2))
    reponse = llm.invoke(prompt)
    return extraire_json(reponse.content)
