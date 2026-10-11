"""Interface separating the application from a specific LLM provider."""

from typing import Protocol

from promptbench.domain import GeneratedResponse, GenerationConfig


class LLMProvider(Protocol):
    """Generate text from a prompt."""

    def generate(self, prompt: str, config: GenerationConfig) -> GeneratedResponse:
        """Run a generation and return it in the shared format."""
        ...
