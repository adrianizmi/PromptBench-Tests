"""Contrato comun de una estrategia de prompt."""

from typing import Protocol

from promptbench.domain import EvaluationCase


class PromptStrategy(Protocol):
    """Construye un prompt reproducible para un caso de evaluacion."""

    def build(self, case: EvaluationCase) -> str:
        """Devuelve el texto que se enviara literalmente al modelo."""
        ...
