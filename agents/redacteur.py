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

PROMPT_REDACTEUR = """Tu es rédacteur senior pour la cellule de communication de crise du CNC (Centre National du Cinéma).
On te donne un brief stratégique issu d'une analyse de la crise en cours sur X (Twitter).
Rédige des propositions de message de riposte institutionnelle.

Ton neutre, factuel et professionnel. Ces messages seront RELUS et VALIDÉS par un humain avant toute publication.
Tu ne prends pas position sur le fond politique. Tu parles au nom de l'institution, pas d'une personne.

Brief (JSON) :
{brief}

Renvoie UNIQUEMENT un objet JSON, structure EXACTE :

{{
  "messages": ["<proposition 1>", "<proposition 2>"],
  "canal": "tweet|fil|communique",
  "a_valider_humainement": true
}}

Règles strictes :
2 propositions de message, adaptées au canal indiqué dans le brief.
Pour un tweet : max 280 caractères, phrase directe, pas de hashtag militant.
Pour un fil : 2-3 tweets enchaînés, numérotés 1/3, 2/3, 3/3.
Pour un communiqué : ton formel, intro + corps + clôture, 3-4 phrases max.
Respecte la "posture" du brief : factuel / apaisant / ferme.
Vise le narratif indiqué dans "cible_narrative", sans agressivité.
Ne mentionne aucune personne nommément. Reste au niveau institutionnel.
N'invente aucun chiffre ou fait non présent dans le brief.
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
