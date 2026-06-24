"""Agent d'analyse de la coordination."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.base import BaseAnalysisAgent


class SuspiciousSignal(BaseModel):
    signal: str = Field(description="Signal de coordination suspecte")
    evidence: str = Field(description="Preuve textuelle ou statistique")
    severity: str = Field(description="Niveau : faible, moyen, fort")


class CoordinationOutput(BaseModel):
    summary: str = Field(description="Synthèse sur l'existence ou non d'une coordination")
    orchestrated: str = Field(
        description="Conclusion : coordination détectée oui/non/partiellement, avec nuance"
    )
    signals: list[SuspiciousSignal] = Field(description="Signaux observés")
    suspicious_accounts: list[str] = Field(description="Comptes à surveiller")
    clusters: list[str] = Field(description="Groupes/clusters identifiés")


class CoordinationAgent(BaseAnalysisAgent):
    name = "coordination"
    system_prompt = (
        "Tu es un analyste de détection de coordination en ligne. "
        "Tu cherches les signes de manipulation : comptes récents, copier-coller, synchronisation, "
        "hashtags identiques, clusters. Tu restes prudent et nuancé : tu ne cries pas au bot sans preuve."
    )
    output_model = CoordinationOutput

    def build_task(self, context: dict[str, Any]) -> str:
        return (
            "Analyse le corpus pour détecter d'éventuels signes de coordination ou d'orchestration.\n"
            "Cherche : comptes récents ou peu suivis très actifs, copier-coller de messages, "
            "synchronisation temporelle, hashtags communs, clusters d'acteurs.\n"
            "Donne une conclusion nuancée : coordination détectée oui/non/partiellement."
        )
