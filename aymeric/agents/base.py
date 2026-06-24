"""Classe de base pour les agents d'analyse."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, get_args, get_origin

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from agents.model import get_model, _FakeChatModel


def _default_for_field(annotation: Any) -> Any:
    """Retourne une valeur par défaut simple pour un type d'annotation."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is list or annotation is list:
        return []
    if origin is dict or annotation is dict:
        return {}
    if origin in (str,) or annotation is str:
        return ""
    if origin in (int,) or annotation is int:
        return 0
    if origin in (bool,) or annotation is bool:
        return False
    # Types Pydantic imbriqués
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _default_instance(annotation)
    return None


def _default_instance(model_class: type[BaseModel]) -> BaseModel:
    """Crée une instance par défaut d'un modèle Pydantic."""
    values: dict[str, Any] = {}
    for name, field in model_class.model_fields.items():
        values[name] = _default_for_field(field.annotation)
    return model_class(**values)


class BaseAnalysisAgent(ABC):
    """Agent d'analyse spécialisé."""

    name: str = "base"
    system_prompt: str = "Tu es un analyste de crise informationnelle."
    output_model: type[BaseModel] | None = None

    def __init__(self):
        self.model = get_model()
        self._is_fake = isinstance(self.model, _FakeChatModel)
        if self.output_model is not None and not self._is_fake:
            self.structured_model = self.model.with_structured_output(self.output_model)
        else:
            self.structured_model = self.model
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                ("human", "{context}\n\n{task}"),
            ]
        )
        self.chain = self.prompt | self.structured_model

    @abstractmethod
    def build_task(self, context: dict[str, Any]) -> str:
        """Construit la consigne spécifique à l'agent."""

    def _dry_run_output(self) -> Any:
        """Sortie par défaut quand aucune clé API n'est configurée."""
        if self.output_model is not None:
            instance = _default_instance(self.output_model)
            # On injecte un message explicite dans le champ summary s'il existe
            if hasattr(instance, "summary"):
                instance.summary = (
                    "[MODE TEST] Aucune clé API Mistral configurée. "
                    "Configurez MISTRAL_API_KEY dans .env pour obtenir une analyse réelle."
                )
            return instance
        return "[MODE TEST] Sortie factice."

    def run(self, context: dict[str, Any]) -> Any:
        """Exécute l'agent et retourne la sortie structurée."""
        dry_run = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes")
        if dry_run or isinstance(self.model, _FakeChatModel):
            return self._dry_run_output()

        task = self.build_task(context)
        return self.chain.invoke({"context": context["markdown"], "task": task})

    def run_async(self, context: dict[str, Any]) -> Any:
        """Version asynchrone (convenience)."""
        return self.run(context)
