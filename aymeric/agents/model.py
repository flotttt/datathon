"""Factory de modèle LLM pour les agents."""
from __future__ import annotations

import os
from typing import Any

from langchain_core.callbacks import Callbacks
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_mistralai import ChatMistralAI


class _FakeChatModel(BaseChatModel):
    """Modèle factice pour tester le pipeline sans clé API."""

    response: str = (
        "Réponse factice : le pipeline est en mode test. "
        "Ajoutez MISTRAL_API_KEY dans .env et mettez DRY_RUN=false pour obtenir une vraie analyse."
    )

    @property
    def _llm_type(self) -> str:
        return "fake_chat_model"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        message = AIMessage(content=self.response)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> Any:
        yield ChatGeneration(message=AIMessage(content=self.response))


def _build_rate_limiter() -> InMemoryRateLimiter:
    """Rate limiter par défaut : 1 requête/seconde, adapté au free tier Mistral."""
    requests_per_second = float(os.getenv("MISTRAL_RPS", "1.0"))
    return InMemoryRateLimiter(
        requests_per_second=requests_per_second,
        check_every_n_seconds=0.1,
        max_bucket_size=1,
    )


def get_model() -> BaseChatModel:
    """
    Retourne le modèle configuré :
    - Mistral si MISTRAL_API_KEY est présent (et DRY_RUN != true)
    - FakeChatModel sinon, pour tester le pipeline sans clé API.
    """
    dry_run = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes")
    api_key = os.getenv("MISTRAL_API_KEY")

    if dry_run or not api_key:
        return _FakeChatModel()

    model_name = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    max_retries = int(os.getenv("MISTRAL_MAX_RETRIES", "5"))
    return ChatMistralAI(
        model=model_name,
        temperature=0.2,
        max_retries=max_retries,
        timeout=60,
        rate_limiter=_build_rate_limiter(),
    )
