"""Agent d'analyse sémantique et tonale."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.base import BaseAnalysisAgent


class SemanticOutput(BaseModel):
    summary: str = Field(description="Synthèse du ton et du vocabulaire")
    global_sentiment: str = Field(description="Sentiment dominant")
    tone_evolution: str = Field(description="Évolution du ton dans le temps")
    aggressive_vocabulary: list[str] = Field(description="Mots/expressions marquantes agressives ou polarisantes")
    vocabulary_shifts: list[str] = Field(description="Glissements de vocabulaire observés")
    key_themes: list[str] = Field(description="Thèmes principaux")


class SemanticAgent(BaseAnalysisAgent):
    name = "semantique"
    system_prompt = (
        "Tu es un analyste sémantique. "
        "Tu décryptes le ton, le sentiment, le vocabulaire et les thèmes d'un corpus. "
        "Tu restes neutre et analytique."
    )
    output_model = SemanticOutput

    def build_task(self, context: dict[str, Any]) -> str:
        return (
            "Analyse le ton et le vocabulaire du corpus fourni.\n"
            "Donne : sentiment global, évolution du ton, expressions agressives ou polarisantes, "
            "glissements de vocabulaire et thèmes principaux. "
            "Tire des insights sur la montée en intensité émotionnelle si elle est visible."
        )
