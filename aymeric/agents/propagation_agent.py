"""Agent d'analyse de la propagation."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.base import BaseAnalysisAgent


class Peak(BaseModel):
    timestamp: str = Field(description="Date/heure du pic")
    trigger: str = Field(description="Événement déclencheur supposé")
    volume: int = Field(description="Nombre de posts approximatif")
    engagement: int = Field(description="Engagement total approximatif")


class PropagationOutput(BaseModel):
    summary: str = Field(description="Synthèse de la dynamique de propagation")
    patient_zero: str = Field(description="Compte/message à l'origine ou qui a initié la crise")
    peaks: list[Peak] = Field(description="Pics de volume identifiés")
    speed: str = Field(description="Vitesse de propagation : lent/rapide/explosif")
    amplification_channels: list[str] = Field(description="Canaux d'amplification : retweets, médias, influenceurs")


class PropagationAgent(BaseAnalysisAgent):
    name = "propagation"
    system_prompt = (
        "Tu es un analyste de propagation virale. "
        "Tu étudies la vitesse, les pics de volume, les canaux d'amplification et le patient zéro. "
        "Tu t'appuies sur les statistiques et les exemples fournis."
    )
    output_model = PropagationOutput

    def build_task(self, context: dict[str, Any]) -> str:
        return (
            "Analyse la propagation du corpus fourni ci-dessus.\n"
            "Identifie le patient zéro (compte/message à l'origine) si possible, les pics de volume, "
            "la vitesse de propagation et les canaux d'amplification (retweets, quote-tweets, médias, influenceurs).\n"
            "Utilise les statistiques de volume horaire et les top posts."
        )
