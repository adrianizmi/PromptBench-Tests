"""Integration test for the Ollama provider."""

import pytest

from promptbench.domain import GenerationConfig
from promptbench.providers.ollama import OllamaProvider

pytestmark = pytest.mark.integration


def test_ollama_provider_returns_generated_text() -> None:
    provider = OllamaProvider()
    config = GenerationConfig(
        model="qwen2.5-coder:1.5b",
        timeout_seconds=30,
    )

    response = provider.generate("Reply with OK only", config)

    assert response.text
    assert response.latency_ms >= 0
