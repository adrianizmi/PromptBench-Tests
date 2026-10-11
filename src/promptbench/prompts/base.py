"""Contract shared by prompt strategies."""

from typing import Protocol

from promptbench.domain import EvaluationCase


class PromptStrategy(Protocol):
    """Build a reproducible prompt for an evaluation case."""

    def build(self, case: EvaluationCase) -> str:
        """Return the literal text sent to the model."""
        ...
