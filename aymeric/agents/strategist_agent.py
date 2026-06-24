"""Agent stratège final : recommande des actions de communication de crise."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.base import BaseAnalysisAgent


class Recommendation(BaseModel):
    priority: str = Field(description="Priorité : immédiat/urgent/moyen terme/long terme")
    action: str = Field(description="Action concrète recommandée")
    justification: str = Field(description="Justification basée sur les analyses")
    owner: str = Field(description="Qui doit s'en charger : direction, com, community manager, juridique")


class KeyMessage(BaseModel):
    do: str = Field(description="Message à privilégier")
    dont: str = Field(description="Message à éviter")


class StrategistOutput(BaseModel):
    summary: str = Field(description="Synthèse de la situation et risque principal")
    recommendations: list[Recommendation] = Field(description="Liste d'actions recommandées")
    key_messages: list[KeyMessage] = Field(description="Messages clés à tenir/éviter")
    monitoring: list[str] = Field(description="Éléments à surveiller dans les prochaines heures")


class StrategistAgent(BaseAnalysisAgent):
    name = "strategie"
    system_prompt = (
        "Tu es un conseiller en communication de crise. "
        "Tu reçois les analyses d'une équipe d'agents spécialisés et tu proposes un plan d'action concret, "
        "mesurable et adapté à une institution publique. Tu restes factuel et stratégique."
    )
    output_model = StrategistOutput

    def build_task(self, context: dict[str, Any]) -> str:
        return (
            "Tu disposes ci-dessus des analyses produites par 5 agents spécialisés "
            "(acteurs, narratifs, propagation, coordination, sémantique).\n"
            "Propose un plan d'action de communication de crise : actions prioritaires, messages à tenir, "
            "messages à éviter, et éléments à surveiller. Sois concret et réaliste."
        )

    def run(self, context: dict[str, Any]) -> Any:
        # Le contexte doit contenir les sorties des autres agents
        agent_outputs = context.get("agent_outputs", {})

        # Construction d'un contexte enrichi pour le stratège
        strategist_context = self._build_strategist_context(context, agent_outputs)

        dry_run = self._is_fake_or_dry()
        if dry_run:
            return self._dry_run_output()

        task = self.build_task(context)
        return self.chain.invoke({"context": strategist_context, "task": task})

    def _build_strategist_context(
        self, context: dict[str, Any], agent_outputs: dict[str, Any]
    ) -> str:
        lines = ["# Analyses des agents spécialisés\n"]

        for name in ("actors", "narratives", "propagation", "coordination", "semantics"):
            output = agent_outputs.get(name)
            if output is None:
                continue
            lines.append(f"\n## Agent {name}\n")
            if hasattr(output, "model_dump"):
                lines.append(output.model_dump_json(indent=2))
            else:
                lines.append(str(output))

        lines.append("\n# Contexte global\n")
        lines.append(context.get("markdown", ""))
        return "\n".join(lines)

    def _is_fake_or_dry(self) -> bool:
        import os

        return os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes") or self._is_fake
