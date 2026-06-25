"""
test_agents.py — Teste CHAQUE agent isolement.

Pourquoi ce script existe (argument pour le jury) :
grace aux CONTRATS (contracts.py), chaque agent se teste sans les autres.
On donne a chaque agent une entree au bon format et on verifie que sa
sortie respecte son contrat. C'est ce qui a permis a 3 binomes de coder
en parallele.

Usage :
    python test_agents.py             # teste les 3 agents
    python test_agents.py analyste    # teste un seul agent
    python test_agents.py --no-llm    # Analyste sans appel LLM (rapide)

L'Analyste tourne sur un ECHANTILLON du vrai corpus (pas tout, pour aller vite).
Le Stratege et le Redacteur tournent sur des ENTREES FIXTURES (issues des
schemas), donc sans dependre de l'Analyste.
"""
import sys
import json

import data_loading
from common import charger_cle
from contracts import (
    valider_sortie,
    ANALYSTE_SCHEMA,
    STRATEGE_SCHEMA,
)
from agents import analyste, stratege, redacteur


# Couleurs terminal (degradent proprement si non supporte).
VERT, ROUGE, GRAS, FIN = "\033[92m", "\033[91m", "\033[1m", "\033[0m"


def titre(txt):
    print(f"\n{GRAS}{'=' * 56}{FIN}\n{GRAS}  {txt}{FIN}\n{GRAS}{'=' * 56}{FIN}")


def verdict(nom, sortie):
    """Affiche la sortie et valide le contrat. Renvoie True/False."""
    print(json.dumps(sortie, ensure_ascii=False, indent=2, default=str))
    ok = valider_sortie(nom, sortie)
    if ok:
        print(f"{VERT}[OK] Contrat '{nom}' respecte.{FIN}")
    else:
        print(f"{ROUGE}[ECHEC] Contrat '{nom}' casse.{FIN}")
    return ok


# ---------------------------------------------------------------------
# ENTREES FIXTURES — fausses entrees au bon format, pour tester un agent
# sans faire tourner celui d'avant. (basees sur les schemas des contrats)
# ---------------------------------------------------------------------
FIXTURE_ANALYSE = {
    "etat_propagation": "traine",
    "ton": {"sentiment_global": "neutre", "niveau_agressivite": "moyen"},
    "acteurs_cles": [
        {"pseudo": "SirAfuera", "type": "non_certifie", "portee": "haute"},
        {"pseudo": "LeDindonFiscal", "type": "certifie", "portee": "haute"},
    ],
    "narratifs": [
        {"nom": "Denonciation d'un favoritisme ideologique", "poids": "dominant",
         "mots_cles": ["CNC", "copinage", "subventions", "partialite"]},
        {"nom": "Exigence de transparence", "poids": "secondaire",
         "mots_cles": ["transparence", "controle", "argent public"]},
    ],
}

FIXTURE_BRIEF = {
    "repondre": "oui",
    "timing": "Sous 48h, avant que les narratifs ne se consolident.",
    "cible_narrative": "Denonciation d'un favoritisme ideologique",
    "posture": "factuel",
    "justification": "Crise sur la traine, agressivite moderee : une mise au point factuelle est possible.",
    "confiance": "haute",
    "escalade_humaine": False,
}


# ---------------------------------------------------------------------
# TESTS PAR AGENT
# ---------------------------------------------------------------------
def test_analyste(use_llm=True, n_echantillon=500):
    titre("AGENT 1/3 — ANALYSTE (sur echantillon du corpus)")
    df = data_loading.load_corpus()
    echantillon = df.head(n_echantillon)
    print(f"Echantillon : {len(echantillon)} messages (sur {len(df)}).")
    sortie = analyste.run(echantillon, use_llm=use_llm)
    return verdict("analyste", sortie)


def test_stratege():
    titre("AGENT 2/3 — STRATEGE (entree fixture)")
    print(f"{GRAS}Entree (fausse analyse au format ANALYSTE_SCHEMA) :{FIN}")
    print(json.dumps(FIXTURE_ANALYSE, ensure_ascii=False, indent=2))
    print(f"\n{GRAS}Sortie :{FIN}")
    sortie = stratege.run(FIXTURE_ANALYSE)
    return verdict("stratege", sortie)


def test_redacteur():
    titre("AGENT 3/3 — REDACTEUR (entree fixture)")
    print(f"{GRAS}Entree (faux brief au format STRATEGE_SCHEMA) :{FIN}")
    print(json.dumps(FIXTURE_BRIEF, ensure_ascii=False, indent=2))
    print(f"\n{GRAS}Sortie :{FIN}")
    sortie = redacteur.run(FIXTURE_BRIEF)
    return verdict("redacteur", sortie)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    use_llm = "--no-llm" not in sys.argv

    charger_cle()

    tests = {
        "analyste": lambda: test_analyste(use_llm=use_llm),
        "stratege": test_stratege,
        "redacteur": test_redacteur,
    }

    cibles = args if args else list(tests)
    resultats = {}
    for nom in cibles:
        if nom not in tests:
            print(f"{ROUGE}Agent inconnu : {nom}. Choix : {', '.join(tests)}.{FIN}")
            continue
        try:
            resultats[nom] = tests[nom]()
        except Exception as e:
            print(f"{ROUGE}[ERREUR] {nom} a leve une exception : {e}{FIN}")
            resultats[nom] = False

    # --- Bilan ---
    titre("BILAN")
    for nom, ok in resultats.items():
        etat = f"{VERT}OK{FIN}" if ok else f"{ROUGE}ECHEC{FIN}"
        print(f"  {nom:12s} : {etat}")
    total = sum(resultats.values())
    print(f"\n  {total}/{len(resultats)} agents valident leur contrat.")


if __name__ == "__main__":
    main()
