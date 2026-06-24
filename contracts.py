"""
contracts.py — Les contrats partagés entre les 3 agents.

C'EST LE FICHIER LE PLUS IMPORTANT DU PROJET.
Tant que chaque agent respecte SA structure de sortie, les 3 binômes
peuvent bosser en parallèle sans jamais se synchroniser.

Ne modifiez ces structures qu'en équipe (30 min ensemble au début).
"""

# =====================================================================
# SORTIE ANALYSTE  (= entrée du Stratège)
# =====================================================================
ANALYSTE_SCHEMA = {
    "narratifs": [
        # liste d'objets : {nom, poids, mots_cles}
        {"nom": "copinage", "poids": "dominant", "mots_cles": ["argent", "fonds", "talent"]},
    ],
    "etat_propagation": "pic",          # "montee" | "pic" | "traine"
    "ton": {
        "sentiment_global": "negatif",  # negatif | neutre | positif
        "niveau_agressivite": "eleve",  # faible | moyen | eleve
    },
    "acteurs_cles": [
        # liste d'objets : {pseudo, type, portee}
        {"pseudo": "SirAfuera", "type": "militant", "portee": "haute"},
    ],
}

# =====================================================================
# SORTIE STRATÈGE  (= entrée du Rédacteur)
# Directeur de com — aide à la décision. Il TRANCHE et JUSTIFIE.
# =====================================================================
STRATEGE_SCHEMA = {
    "repondre": "oui",                  # "oui" | "temporiser" | "non"
    "timing": "attendre la retombée (~48h)",
    "cible_narrative": "copinage",      # nom du narratif à contrer
    "posture": "factuel",               # "factuel" | "apaisant" | "ferme"
    "justification": "Narratif dominant + crise sur la traîne : fenêtre d'apaisement.",
    "confiance": "moyenne",             # "haute" | "moyenne" | "faible"
    "escalade_humaine": True,           # True au pic ou si confiance faible
}

# =====================================================================
# SORTIE RÉDACTEUR  (sortie finale du pipeline)
# Si repondre != "oui", il ne génère PAS de message : note d'attente.
# =====================================================================
REDACTEUR_SCHEMA = {
    "messages": [
        "Proposition de message 1...",
    ],
    "canal": "tweet",                   # "tweet" | "fil" | "communique"
    "a_valider_humainement": True,      # TOUJOURS True — jamais de publi auto
}


def valider_sortie(nom_agent: str, sortie: dict) -> bool:
    """Mini-validateur : vérifie que les clés attendues sont présentes.
    Appelé par l'orchestrateur pour détecter un contrat cassé tôt."""
    schemas = {
        "analyste": ANALYSTE_SCHEMA,
        "stratege": STRATEGE_SCHEMA,
        "redacteur": REDACTEUR_SCHEMA,
    }
    attendu = set(schemas[nom_agent].keys())
    recu = set(sortie.keys())
    manquant = attendu - recu
    if manquant:
        print(f"[CONTRAT CASSÉ] {nom_agent} : clés manquantes -> {manquant}")
        return False
    return True
