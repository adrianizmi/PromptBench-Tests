"""Interfaz que separa la aplicacion del proveedor concreto de LLM."""

from typing import Protocol

from promptbench.domain import GeneratedResponse, GenerationConfig


class LLMProvider(Protocol):
    """Genera texto a partir de un prompt."""

    def generate(self, prompt: str, config: GenerationConfig) -> GeneratedResponse:
        """Ejecuta una generacion y la devuelve en el formato comun."""
        ...
