"""Local LLM provider using Ollama."""

from __future__ import annotations

import time

import httpx

from ai.providers.base import AIProvider, AIResponse
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("ai.providers.local")


class LocalProvider(AIProvider):
    """Local LLM provider using Ollama REST API.

    This is the default provider. It runs entirely on local hardware
    and costs nothing beyond electricity.
    """

    provider_name = "local"
    is_local = True
    cost_per_1k_input = 0.0
    cost_per_1k_output = 0.0

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.base_url = base_url or settings.ollama_url
        self.model = model or settings.ollama_model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: str | None = None,
    ) -> AIResponse:
        """Generate text using the local Ollama model."""
        start_time = time.monotonic()

        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        if response_format == "json":
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            elapsed_ms = int((time.monotonic() - start_time) * 1000)

            return AIResponse(
                content=data.get("response", ""),
                provider=self.provider_name,
                model=self.model,
                input_tokens=data.get("prompt_eval_count", 0),
                output_tokens=data.get("eval_count", 0),
                estimated_cost=0.0,
                latency_ms=elapsed_ms,
            )

        except httpx.ConnectError:
            logger.error("ollama_connection_failed", url=self.base_url)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("ollama_http_error", status=e.response.status_code)
            raise
        except Exception as e:
            logger.error("ollama_unknown_error", error=str(e))
            raise

    async def health_check(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code != 200:
                    return False
                models = response.json().get("models", [])
                return any(
                    self.model in m.get("name", "")
                    for m in models
                )
        except Exception:
            return False

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings using the local embedding model.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector as a list of floats.
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": settings.ollama_embed_model,
                        "prompt": text,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("embedding", [])
        except Exception as e:
            logger.error("embedding_failed", error=str(e))
            raise
