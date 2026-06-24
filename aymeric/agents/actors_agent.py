"""Agent d'analyse des acteurs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.base import BaseAnalysisAgent


class ActorProfile(BaseModel):
    username: str = Field(description="Pseudo Twitter/X de l'acteur")
    category: str = Field(
        description="Catégorie : media, influenceur, militant, anonyme, institution, bot/suspect, autre"
    )
    role_in_crisis: str = Field(description="Rôle joué dans la crise")
    estimated_reach: str = Field(description="Portée approximative : followers, impressions")
    key_tweet_summary: str = Field(
        description="Résumé d'un tweet marquant ou pattern observé"
    )


class ActorsOutput(BaseModel):
    summary: str = Field(description="Synthèse générale de l'écosystème d'acteurs")
    actors: list[ActorProfile] = Field(description="Liste des acteurs identifiés")
    main_insight: str = Field(
        description="Insight principal : qui a lancé/amplifié et comment"
    )


class ActorsAgent(BaseAnalysisAgent):
    name = "acteurs"
    system_prompt = (
        "Tu es un analyste spécialisé dans l'identification des acteurs d'une crise informationnelle. "
        "Tu restes neutre et factuel. Tu catégorises les comptes selon leur nature et leur rôle. "
        "Tu ne juge pas le fond, tu décris la dynamique."
    )
    output_model = ActorsOutput

    def build_task(self, context: dict[str, Any]) -> str:
        return (
            "Analyse les acteurs du corpus fourni ci-dessus.\n"
            "Identifie jusqu'à 10 acteurs clés (media, influenceurs, militants, anonymes, comptes suspects, institutions).\n"
            "Pour chacun, précise : catégorie, rôle dans la crise, portée, et un tweet/pattern marquant.\n"
            "Termine par un insight principal : qui a lancé ou amplifié la crise et comment ?"
        )
