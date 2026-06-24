"""
agents/analyste.py — AGENT 1 : L'ANALYSTE
Binôme : Mathis + 2

RÔLE : comprendre le corpus et sortir une synthèse structurée.
ENTRÉE : un bloc de texte (échantillon du corpus).
SORTIE : le dict ANALYSTE_SCHEMA (voir contracts.py).

À FAIRE par le binôme :
  1. Affiner le PROMPT ci-dessous (c'est 80 % du boulot).
  2. (Optionnel) brancher de vrais OUTILS pandas du Jour 1
     (détecteur de pic, classifieur narratifs, cartographie acteurs)
     pour donner des chiffres exacts au lieu de tout laisser au LLM.
"""
from common import get_llm, extraire_json

PROMPT_ANALYSTE = """Tu es un analyste de crise informationnelle. On te donne un échantillon
de messages X (Twitter) issus d'une crise. Tu DÉCRIS, tu ne juges pas. Ton neutre.

Analyse l'échantillon et renvoie UNIQUEMENT un objet JSON, sans texte autour,
avec EXACTEMENT cette structure :

{{
  "narratifs": [
    {{"nom": "<nom court du discours>", "poids": "dominant|secondaire|marginal", "mots_cles": ["..."]}}
  ],
  "etat_propagation": "montee|pic|traine",
  "ton": {{"sentiment_global": "negatif|neutre|positif", "niveau_agressivite": "faible|moyen|eleve"}},
  "acteurs_cles": [
    {{"pseudo": "<sans @>", "type": "elu|media|militant|anonyme", "portee": "haute|moyenne|faible"}}
  ]
}}

Règles :
- 2 à 4 narratifs maximum, les plus présents.
- Base-toi uniquement sur ce que tu vois dans l'échantillon.
- N'invente pas de pseudo : prends-les dans les messages.

ÉCHANTILLON :
{corpus}
"""


def run(corpus_texte: str) -> dict:
    llm = get_llm(temperature=0.1)  # analyse = peu de créativité
    prompt = PROMPT_ANALYSTE.format(corpus=corpus_texte)
    reponse = llm.invoke(prompt)
    return extraire_json(reponse.content)


# --- PISTE OUTILS (optionnel mais valorisant) ---------------------------
# Au lieu de laisser le LLM deviner l'état de propagation, calculez-le en
# pandas et injectez-le dans le prompt. Exemple de squelette :
#
# def detecter_propagation(df) -> str:
#     vol_jour = df.set_index("Date").resample("D").size()
#     # ... votre logique du Jour 1 ...
#     return "pic"
