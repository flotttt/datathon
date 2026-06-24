"""Orchestrateur LangGraph coordonnant les agents d'analyse."""
from __future__ import annotations

import os
import time
from typing import Any

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from agents.actors_agent import ActorsAgent
from agents.narratives_agent import NarrativesAgent
from agents.propagation_agent import PropagationAgent
from agents.coordination_agent import CoordinationAgent
from agents.semantic_agent import SemanticAgent
from agents.strategist_agent import StrategistAgent


class CrisisState(TypedDict):
    context: dict[str, Any]
    actors: Any
    narratives: Any
    propagation: Any
    coordination: Any
    semantics: Any
    strategist_output: Any
    final_report: dict[str, Any]


ANALYSIS_AGENTS = [
    ("actors", ActorsAgent),
    ("narratives", NarrativesAgent),
    ("propagation", PropagationAgent),
    ("coordination", CoordinationAgent),
    ("semantics", SemanticAgent),
]


def start_node(state: CrisisState) -> CrisisState:
    """Point d'entrée : ne fait rien, sert de déclencheur."""
    return {}


def make_agent_node(name: str, agent_cls: type, delay: float):
    """Factory de nœud LangGraph pour un agent d'analyse."""

    def _node(state: CrisisState) -> CrisisState:
        if delay > 0:
            time.sleep(delay)
        agent = agent_cls()
        result = agent.run(state["context"])
        return {name: result}

    return _node


def strategist_node(state: CrisisState) -> CrisisState:
    """Exécute l'agent stratège final en agrégeant les analyses."""
    outputs = {
        "actors": state.get("actors"),
        "narratives": state.get("narratives"),
        "propagation": state.get("propagation"),
        "coordination": state.get("coordination"),
        "semantics": state.get("semantics"),
    }

    delay = float(os.getenv("AGENT_DELAY", "2.0"))
    if delay > 0:
        time.sleep(delay)

    strategist_context = dict(state["context"])
    strategist_context["agent_outputs"] = outputs

    agent = StrategistAgent()
    result = agent.run(strategist_context)
    return {"strategist_output": result}


def final_aggregate(state: CrisisState) -> CrisisState:
    """Construit le rapport final complet."""
    actors = state.get("actors") or {}
    narratives = state.get("narratives") or {}

    report = {
        "context_summary": {
            "focus_keyword": state["context"].get("focus_keyword"),
            "basic_stats": state["context"].get("basic_stats"),
        },
        "actors": state.get("actors"),
        "narratives": state.get("narratives"),
        "propagation": state.get("propagation"),
        "coordination": state.get("coordination"),
        "semantics": state.get("semantics"),
        "strategy": state.get("strategist_output"),
        "synthesis": {
            "main_insight": getattr(actors, "main_insight", ""),
            "main_conflict": getattr(narratives, "main_conflict", ""),
        },
    }
    return {"final_report": report}


def build_graph() -> StateGraph:
    """Construit le graphe LangGraph d'orchestration."""
    graph = StateGraph(CrisisState)

    delay = float(os.getenv("AGENT_DELAY", "2.0"))

    # Nœuds
    graph.add_node("start", start_node)
    for idx, (name, cls) in enumerate(ANALYSIS_AGENTS):
        node_delay = delay if idx > 0 else 0.0
        graph.add_node(name, make_agent_node(name, cls, node_delay))
    graph.add_node("strategist", strategist_node)
    graph.add_node("final_aggregate", final_aggregate)

    # Séquence : orchestrateur qui enchaîne les agents
    graph.set_entry_point("start")
    graph.add_edge("start", ANALYSIS_AGENTS[0][0])
    for i in range(len(ANALYSIS_AGENTS) - 1):
        graph.add_edge(ANALYSIS_AGENTS[i][0], ANALYSIS_AGENTS[i + 1][0])
    graph.add_edge(ANALYSIS_AGENTS[-1][0], "strategist")
    graph.add_edge("strategist", "final_aggregate")
    graph.add_edge("final_aggregate", END)

    return graph.compile()


class CrisisOrchestrator:
    """Orchestreur haut niveau du pipeline d'analyse de crise."""

    def __init__(self):
        self.graph = build_graph()

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Lance l'analyse complète et retourne le rapport final."""
        state = {"context": context}
        result = self.graph.invoke(state)
        return result["final_report"]
