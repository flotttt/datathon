"""
orchestrateur.py — LE CHEF D'ORCHESTRE (poste de Mekk)
Version LangGraph : transforme 3 agents isolés en UN produit.

Pipeline : Corpus(DataFrame) -> Analyste -> Stratège -> Rédacteur -> Riposte

Lancement :
    python orchestrateur.py
"""
import json
from typing import Any

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

from common import charger_cle, charger_corpus, echantillon, corpus_en_texte
from contracts import valider_sortie
from templates.agents import analyste, stratege, redacteur


class OrchestratorState(TypedDict):
    """État partagé entre les nœuds du graphe."""
    corpus_texte: str
    verbose: bool
    analyse: dict[str, Any] | None
    brief: dict[str, Any] | None
    riposte: dict[str, Any] | None
    erreur: str | None


def _log(state: OrchestratorState, titre: str, contenu: Any) -> None:
    """Affiche une étape si verbose=True."""
    if state.get("verbose"):
        print(f"\n=== {titre} ===")
        print(json.dumps(contenu, ensure_ascii=False, indent=2))


def nœud_analyste(state: OrchestratorState) -> OrchestratorState:
    """Nœud 1 : lance l'agent Analyste et valide sa sortie."""
    analyse = analyste.run(state["corpus_texte"])
    _log(state, "1/3  ANALYSTE", analyse)

    if not valider_sortie("analyste", analyse):
        return {"analyse": analyse, "erreur": "Sortie Analyste invalide (contrat cassé)."}

    return {"analyse": analyse, "erreur": None}


def nœud_stratege(state: OrchestratorState) -> OrchestratorState:
    """Nœud 2 : lance l'agent Stratège et valide sa sortie."""
    if state.get("erreur"):
        return {}

    brief = stratege.run(state["analyse"])
    _log(state, "2/3  STRATÈGE", brief)

    if not valider_sortie("stratege", brief):
        return {"brief": brief, "erreur": "Sortie Stratège invalide (contrat cassé)."}

    return {"brief": brief, "erreur": None}


def nœud_redacteur(state: OrchestratorState) -> OrchestratorState:
    """Nœud 3 : lance l'agent Rédacteur et valide sa sortie."""
    if state.get("erreur"):
        return {}

    riposte = redacteur.run(state["brief"])
    _log(state, "3/3  RÉDACTEUR", riposte)

    if not valider_sortie("redacteur", riposte):
        return {"riposte": riposte, "erreur": "Sortie Rédacteur invalide (contrat cassé)."}

    return {"riposte": riposte, "erreur": None}


def route_apres_analyste(state: OrchestratorState) -> str:
    """Route conditionnelle après l'Analyste."""
    return "stratege" if state.get("erreur") is None else "fin_erreur"


def route_apres_stratege(state: OrchestratorState) -> str:
    """Route conditionnelle après le Stratège."""
    return "redacteur" if state.get("erreur") is None else "fin_erreur"


def nœud_fin_erreur(state: OrchestratorState) -> OrchestratorState:
    """Nœud terminal en cas d'erreur de validation."""
    if state.get("verbose"):
        print(f"\n[ERREUR ORCHESTRATEUR] {state.get('erreur')}")
    return {}


def nœud_fin_succes(state: OrchestratorState) -> OrchestratorState:
    """Nœud terminal en cas de succès."""
    if state.get("verbose"):
        print("\n" + "=" * 50)
        print("PRODUIT FINAL — riposte prête à valider :")
        print("=" * 50)
        riposte = state.get("riposte")
        if riposte:
            for i, m in enumerate(riposte.get("messages", []), 1):
                print(f"\n  Proposition {i} :\n  {m}")
            print(f"\n  Canal : {riposte.get('canal')}")
            print(f"  À valider par un humain : {riposte.get('a_valider_humainement')}")
    return {}


def construire_graphe() -> StateGraph:
    """Construit et compile le graphe LangGraph."""
    graphe = StateGraph(OrchestratorState)

    # Nœuds
    graphe.add_node("analyste", nœud_analyste)
    graphe.add_node("stratege", nœud_stratege)
    graphe.add_node("redacteur", nœud_redacteur)
    graphe.add_node("fin_erreur", nœud_fin_erreur)
    graphe.add_node("fin_succes", nœud_fin_succes)

    # Point d'entrée
    graphe.set_entry_point("analyste")

    # Routes conditionnelles
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

    # Fin du pipeline
    graphe.add_edge("redacteur", "fin_succes")
    graphe.add_edge("fin_erreur", END)
    graphe.add_edge("fin_succes", END)

    return graphe.compile()


def lancer_pipeline(corpus_texte: str, verbose: bool = True) -> dict:
    """
    Point d'entrée principal. Conserve la même signature que l'ancien orchestrateur.
    """
    graphe = construire_graphe()

    état_initial: OrchestratorState = {
        "corpus_texte": corpus_texte,
        "verbose": verbose,
        "analyse": None,
        "brief": None,
        "riposte": None,
        "erreur": None,
    }

    résultat = graphe.invoke(état_initial)

    return {
        "analyse": résultat.get("analyse"),
        "brief": résultat.get("brief"),
        "riposte": résultat.get("riposte"),
        "erreur": résultat.get("erreur"),
    }


if __name__ == "__main__":
    charger_cle()
    df = charger_corpus("Dataset/data.xlsx")
    ech = echantillon(df, n=40, fenetre_pic=True)
    texte = corpus_en_texte(ech, max_msg=40)

    print(f"Échantillon : {len(ech)} messages de la fenêtre de pic.")
    resultat = lancer_pipeline(texte)

    if resultat.get("erreur"):
        print(f"\nPipeline interrompu : {resultat['erreur']}")
