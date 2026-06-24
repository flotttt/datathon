"""Agent d'analyse des narratifs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.base import BaseAnalysisAgent


class Narrative(BaseModel):
    label: str = Field(description="Nom court du narratif/camp")
    description: str = Field(description="Description du discours")
    keywords: list[str] = Field(description="Mots-clés associés")
    stance: str = Field(
        description="Position : critique du CNC, défense d'Ultia, critique d'Ultia, neutre, etc."
    )
    estimated_volume: str = Field(description="Volume estimé : dominant, notable, minoritaire")


class NarrativesOutput(BaseModel):
    summary: str = Field(description="Synthèse des grands narratifs en présence")
    narratives: list[Narrative] = Field(description="Liste des narratifs identifiés")
    main_conflict: str = Field(description="Conflit narratif principal entre camps")
    evolution: str = Field(description="Évolution des narratifs dans le temps")


class NarrativesAgent(BaseAnalysisAgent):
    name = "narratifs"
    system_prompt = (
        "Tu es un analyste de narratifs sur les réseaux sociaux. "
        "Tu identifies les discours, les camps et les mots-clés. "
        "Tu restes neutre : tu ne prends pas parti, tu décris les positions en présence."
    )
    output_model = NarrativesOutput

    def build_task(self, context: dict[str, Any]) -> str:
        return (
            "Analyse les narratifs du corpus fourni ci-dessus.\n"
            "Identifie les principaux camps/discours (ex : 'censure', 'copinage', 'défense d'Ultia', 'cyberharcèlement', etc.).\n"
            "Pour chaque narratif, donne : nom, description, mots-clés, position, volume estimé.\n"
            "Explique le conflit narratif principal et comment les narratifs évoluent dans le temps."
        )
