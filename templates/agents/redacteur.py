"""
agents/redacteur.py — AGENT 3 : LE RÉDACTEUR
Binôme : Leo

RÔLE : écrire les messages de riposte selon le brief du Stratège.
ENTRÉE : la sortie du Stratège (dict STRATEGE_SCHEMA).
SORTIE : le dict REDACTEUR_SCHEMA (voir contracts.py).

RÈGLE CLÉ : si le Stratège dit "non" ou "temporiser", on ne génère PAS
de message — on renvoie une note d'attente. Cohérence du système.

C'est la VITRINE de la démo : ce sont ces messages que le jury va lire.
À FAIRE par le binôme : affiner le PROMPT pour des messages crédibles,
courts, alignés sur la posture demandée.
"""
import json
from common import get_llm, extraire_json

PROMPT_REDACTEUR = """Tu es rédacteur pour une cellule de communication de crise institutionnelle.
On te donne un brief stratégique. Rédige des propositions de message de riposte.
Ton neutre et professionnel. Ces messages seront RELUS par un humain avant publication.

Brief (JSON) :
{brief}

Renvoie UNIQUEMENT un objet JSON, structure EXACTE :

{{
  "messages": ["<proposition 1>", "<proposition 2>"],
  "canal": "tweet|fil|communique",
  "a_valider_humainement": true
}}

Règles :
- 2 propositions de message, courtes (adaptées au canal).
- Respecte la "posture" du brief (factuel / apaisant / ferme).
- Vise le narratif indiqué dans "cible_narrative", sans agresser.
- Ne mentionne pas de personne nommément ; reste au niveau institutionnel.
"""

# Note d'attente quand on ne répond pas
def _note_attente(brief: dict) -> dict:
    return {
        "messages": [
            f"[AUCUN MESSAGE GÉNÉRÉ] Décision : {brief['repondre']}. "
            f"{brief['justification']} Timing conseillé : {brief['timing']}."
        ],
        "canal": "communique",
        "a_valider_humainement": True,
    }


def run(brief: dict) -> dict:
    # Cohérence du pipeline : on ne rédige que si on répond.
    if brief.get("repondre") != "oui":
        return _note_attente(brief)

    llm = get_llm(temperature=0.4)  # rédaction = un peu plus de créativité
    prompt = PROMPT_REDACTEUR.format(brief=json.dumps(brief, ensure_ascii=False, indent=2))
    reponse = llm.invoke(prompt)
    return extraire_json(reponse.content)
