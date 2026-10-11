"""Minimal HTTP client for a local Ollama instance."""

import time

import httpx

from promptbench.domain import GeneratedResponse, GenerationConfig


class OllamaProvider:
    """Adapter for the local API exposed by Docker Compose."""

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self._base_url = base_url

    def generate(self, prompt: str, config: GenerationConfig) -> GeneratedResponse:
        """Call POST /api/generate and normalize the response."""
        start = time.perf_counter()

        with httpx.Client(timeout=config.timeout_seconds) as client:
            response = client.post(
                f"{self._base_url}/api/generate",
                json={
                    "model": config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": config.temperature,
                        "num_predict": config.max_tokens,
                    },
                },
            )

            latency_ms = (time.perf_counter() - start) * 1000

            response.raise_for_status()

            payload = response.json()
            if not isinstance(payload, dict):
                raise TypeError("Ollama response is not a JSON object.")

            if "response" not in payload:
                raise ValueError("Ollama response does not contain the 'response' field.")

            generated_text = payload["response"]
            if not isinstance(generated_text, str):
                raise TypeError("Ollama 'response' field is not text.")

            return GeneratedResponse(
                text=generated_text,
                latency_ms=latency_ms,
            )
