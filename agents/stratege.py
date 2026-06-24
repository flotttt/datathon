"""
agents/stratege.py — AGENT 2 : LE STRATEGE (Directeur de com)
Binome : Flo

ROLE : aide a la decision. Il TRANCHE et JUSTIFIE — il ne redige pas.
ENTREE : la sortie de l'Analyste (dict ANALYSTE_SCHEMA).
SORTIE : le dict STRATEGE_SCHEMA (voir contracts.py).

Il repond aux 5 questions d'un directeur de com :
  1. Faut-il repondre ?  2. Quand ?  3. Quel narratif contrer ?
  4. Quel ton ?  5. Pourquoi ? (+ confiance + escalade humaine)

GARDE-FOU : au pic, ou si confiance faible -> temporiser + escalade humaine.
"""
import json

from common import get_llm, extraire_json

PROMPT_STRATEGE = """Tu es un directeur de la communication de crise, mandate par le CNC.
On te donne l'analyse d'une crise virale sur X. Tu CONSEILLES un decideur humain :
tu tranches et tu justifies. Tu ne rediges AUCUN message — ce n'est pas ton role.

Tu restes neutre et factuel : tu analyses une dynamique, tu ne prends pas position
dans le debat politique. Tes recommandations sont des propositions a valider par un humain.

Voici l'analyse (JSON) :
{analyse}

Decide et renvoie UNIQUEMENT un objet JSON, sans texte autour, structure EXACTE :

{{
  "repondre": "oui|temporiser|non",
  "timing": "<quand agir, en une phrase>",
  "cible_narrative": "<le narratif a contrer en priorite>",
  "posture": "factuel|apaisant|ferme",
  "justification": "<2-3 phrases : pourquoi cette reco>",
  "confiance": "haute|moyenne|faible",
  "escalade_humaine": true
}}

Regles de decision :
- Si etat_propagation = "pic" : privilegie "temporiser" (repondre au pic jette de l'huile sur le feu).
- Si etat_propagation = "traine" : une mise au point posee peut clore le sujet -> "oui" possible.
- Si niveau_agressivite = "eleve" : posture "apaisant" ou "factuel", jamais "ferme".
- escalade_humaine = true si propagation = "pic" OU confiance = "faible".
- Cible TOUJOURS le narratif "dominant" en priorite.
- Si aucun narratif n'est clairement adressable par des faits verifiables : "temporiser".
"""


def run(analyse: dict) -> dict:
    """Transforme l'analyse en decision strategique (STRATEGE_SCHEMA)."""
    llm = get_llm(temperature=0.2)
    prompt = PROMPT_STRATEGE.format(
        analyse=json.dumps(analyse, ensure_ascii=False, indent=2)
    )
    reponse = llm.invoke(prompt)
    return extraire_json(reponse.content)
