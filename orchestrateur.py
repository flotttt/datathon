"""
orchestrateur.py — LE CHEF D'ORCHESTRE
Version LangGraph : transforme 3 agents isoles en UN produit.

Pipeline : Corpus(DataFrame) -> Analyste -> Stratege -> Redacteur -> Riposte

Les agents finis vivent dans agents/. L'Analyste est hybride (pandas + LLM)
et prend le DataFrame du corpus (il echantillonne lui-meme les textes uniques).

Lancement :
    python orchestrateur.py
"""
import json
import time
from typing import Any

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

import data_loading
import common
from common import charger_cle
from contracts import valider_sortie
from agents import analyste, stratege, redacteur


class OrchestratorState(TypedDict):
    """Etat partage entre les noeuds du graphe."""
    corpus: Any                       # DataFrame du corpus
    verbose: bool
    analyse: dict[str, Any] | None
    brief: dict[str, Any] | None
    riposte: dict[str, Any] | None
    metriques: dict[str, Any] | None  # temps + tokens par agent
    erreur: str | None


def _mesure(state: OrchestratorState, nom: str, t0: float) -> dict:
    """Releve le temps et les tokens consommes depuis le reset, par agent."""
    metriques = dict(state.get("metriques") or {})
    releve = common.USAGE.snapshot()
    releve["duree_s"] = round(time.perf_counter() - t0, 2)
    metriques[nom] = releve
    return metriques


def _log(state: OrchestratorState, titre: str, contenu: Any) -> None:
    """Affiche une etape si verbose=True."""
    if state.get("verbose"):
        print(f"\n=== {titre} ===")
        print(json.dumps(contenu, ensure_ascii=False, indent=2))


def noeud_analyste(state: OrchestratorState) -> OrchestratorState:
    """Noeud 1 : lance l'agent Analyste (hybride pandas + LLM) et valide."""
    common.USAGE.reset()
    t0 = time.perf_counter()
    analyse = analyste.run(state["corpus"])
    metriques = _mesure(state, "analyste", t0)
    _log(state, "1/3  ANALYSTE", analyse)

    if not valider_sortie("analyste", analyse):
        return {"analyse": analyse, "metriques": metriques,
                "erreur": "Sortie Analyste invalide (contrat casse)."}

    return {"analyse": analyse, "metriques": metriques, "erreur": None}


def noeud_stratege(state: OrchestratorState) -> OrchestratorState:
    """Noeud 2 : lance l'agent Stratege et valide sa sortie."""
    if state.get("erreur"):
        return {}

    common.USAGE.reset()
    t0 = time.perf_counter()
    brief = stratege.run(state["analyse"])
    metriques = _mesure(state, "stratege", t0)
    _log(state, "2/3  STRATEGE", brief)

    if not valider_sortie("stratege", brief):
        return {"brief": brief, "metriques": metriques,
                "erreur": "Sortie Stratege invalide (contrat casse)."}

    return {"brief": brief, "metriques": metriques, "erreur": None}


def noeud_redacteur(state: OrchestratorState) -> OrchestratorState:
    """Noeud 3 : lance l'agent Redacteur et valide sa sortie."""
    if state.get("erreur"):
        return {}

    common.USAGE.reset()
    t0 = time.perf_counter()
    riposte = redacteur.run(state["brief"])
    metriques = _mesure(state, "redacteur", t0)
    _log(state, "3/3  REDACTEUR", riposte)

    if not valider_sortie("redacteur", riposte):
        return {"riposte": riposte, "metriques": metriques,
                "erreur": "Sortie Redacteur invalide (contrat casse)."}

    return {"riposte": riposte, "metriques": metriques, "erreur": None}


def route_apres_analyste(state: OrchestratorState) -> str:
    """Route conditionnelle apres l'Analyste."""
    return "stratege" if state.get("erreur") is None else "fin_erreur"


def route_apres_stratege(state: OrchestratorState) -> str:
    """Route conditionnelle apres le Stratege."""
    return "redacteur" if state.get("erreur") is None else "fin_erreur"


def noeud_fin_erreur(state: OrchestratorState) -> OrchestratorState:
    """Noeud terminal en cas d'erreur de validation."""
    if state.get("verbose"):
        print(f"\n[ERREUR ORCHESTRATEUR] {state.get('erreur')}")
    return {}


def noeud_fin_succes(state: OrchestratorState) -> OrchestratorState:
    """Noeud terminal en cas de succes."""
    if state.get("verbose"):
        print("\n" + "=" * 50)
        print("PRODUIT FINAL — riposte prete a valider :")
        print("=" * 50)
        riposte = state.get("riposte")
        if riposte:
            for i, m in enumerate(riposte.get("messages", []), 1):
                print(f"\n  Proposition {i} :\n  {m}")
            print(f"\n  Canal : {riposte.get('canal')}")
            print(f"  A valider par un humain : {riposte.get('a_valider_humainement')}")
    return {}


def construire_graphe():
    """Construit et compile le graphe LangGraph."""
    graphe = StateGraph(OrchestratorState)

    graphe.add_node("analyste", noeud_analyste)
    graphe.add_node("stratege", noeud_stratege)
    graphe.add_node("redacteur", noeud_redacteur)
    graphe.add_node("fin_erreur", noeud_fin_erreur)
    graphe.add_node("fin_succes", noeud_fin_succes)

    graphe.set_entry_point("analyste")

    graphe.add_conditional_edges(
        "analyste",
        route_apres_analyste,
        {"stratege": "stratege", "fin_erreur": "fin_erreur"},
    )
    graphe.add_conditional_edges(
        "stratege",
        route_apres_stratege,
        {"redacteur": "redacteur", "fin_erreur": "fin_erreur"},
    )

    graphe.add_edge("redacteur", "fin_succes")
    graphe.add_edge("fin_erreur", END)
    graphe.add_edge("fin_succes", END)

    return graphe.compile()


def lancer_pipeline(corpus, verbose: bool = True) -> dict:
    """Point d'entree principal. corpus = DataFrame charge via data_loading."""
    graphe = construire_graphe()

    etat_initial: OrchestratorState = {
        "corpus": corpus,
        "verbose": verbose,
        "analyse": None,
        "brief": None,
        "riposte": None,
        "metriques": {},
        "erreur": None,
    }

    resultat = graphe.invoke(etat_initial)

    return {
        "analyse": resultat.get("analyse"),
        "brief": resultat.get("brief"),
        "riposte": resultat.get("riposte"),
        "metriques": resultat.get("metriques"),
        "erreur": resultat.get("erreur"),
    }


if __name__ == "__main__":
    charger_cle()
    df = data_loading.load_corpus("Dataset/data.xlsx")
    print(f"Corpus charge : {len(df)} messages.")

    resultat = lancer_pipeline(df)

    with open("riposte.json", "w", encoding="utf-8") as fichier:
        json.dump(resultat, fichier, ensure_ascii=False, indent=2)
    print("\nResultat ecrit dans riposte.json (lisible par le dashboard).")

    if resultat.get("erreur"):
        print(f"\nPipeline interrompu : {resultat['erreur']}")
