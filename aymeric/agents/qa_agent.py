"""Agent Q&A avec RAG sur Chroma DB."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agents.base import BaseAnalysisAgent
from chroma_store import query_tweets, format_retrieved_context


class Source(BaseModel):
    rank: int = Field(description="Rang du tweet dans les résultats")
    author: str = Field(description="Auteur du tweet")
    date: str = Field(description="Date du tweet")
    text: str = Field(description="Contenu du tweet")
    relevance: str = Field(description="Score de pertinence (distance)")


class QAOutput(BaseModel):
    answer: str = Field(description="Réponse à la question posée")
    sources: list[Source] = Field(description="Sources utilisées pour la réponse")
    confidence: str = Field(description="Niveau de confiance : élevé/moyen/faible")


class QAAgent(BaseAnalysisAgent):
    name = "qa"
    system_prompt = (
        "Tu es un analyste de crise informationnelle. "
        "Tu réponds aux questions en t'appuyant UNIQUEMENT sur les tweets fournis en contexte. "
        "Tu cites tes sources de manière concise. Tu restes neutre et factuel."
    )
    output_model = QAOutput

    def __init__(self, n_results: int = 8):
        super().__init__()
        self.n_results = n_results

    def build_task(self, context: dict[str, Any]) -> str:
        question = context.get("question", "")
        return (
            f"Question de l'utilisateur : {question}\n\n"
            "Réponds en t'appuyant sur les tweets ci-dessus. "
            "Si le corpus ne permet pas de répondre, dis-le clairement."
        )

    def run(self, context: dict[str, Any]) -> Any:
        question = context.get("question", "")
        if not question:
            return self._dry_run_output()

        dry_run = self._is_fake_or_dry()
        if dry_run:
            return self._dry_run_output()

        # Récupération des tweets pertinents via Chroma
        results = query_tweets(question, n_results=self.n_results)
        retrieved_context = format_retrieved_context(results)

        # On remplace temporairement le contexte markdown par les tweets pertinents
        original_markdown = context.get("markdown", "")
        context["markdown"] = retrieved_context

        task = self.build_task(context)
        output = self.chain.invoke({"context": retrieved_context, "task": task})

        # Restauration
        context["markdown"] = original_markdown
        return output

    def _is_fake_or_dry(self) -> bool:
        import os

        return os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes") or self._is_fake

    def _dry_run_output(self) -> Any:
        output = super()._dry_run_output()
        if hasattr(output, "answer"):
            output.answer = (
                "[MODE TEST] Configurez MISTRAL_API_KEY et indexez les tweets avec "
                "`python chroma_store.py` pour obtenir des réponses RAG."
            )
        return output
