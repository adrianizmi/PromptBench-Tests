"""Cliente HTTP minimo para la instancia local de Ollama."""

import time

import httpx

from promptbench.domain import GeneratedResponse, GenerationConfig


class OllamaProvider:
    """Adaptador para la API local expuesta por Docker Compose."""

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self._base_url = base_url

    def generate(self, prompt: str, config: GenerationConfig) -> GeneratedResponse:
        """Llama a POST /api/generate y normaliza la respuesta."""
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
                raise TypeError("La respuesta de Ollama no es un objeto JSON.")

            if "response" not in payload:
                raise ValueError("La respuesta de Ollama no contiene el campo 'response'.")

            generated_text = payload["response"]
            if not isinstance(generated_text, str):
                raise TypeError("El campo 'response' de Ollama no es texto.")

            return GeneratedResponse(
                text=generated_text,
                latency_ms=latency_ms,
            )
