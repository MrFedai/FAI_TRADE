"""Base AI provider interface — all providers must implement this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from backend.logging_config import get_logger

logger = get_logger("ai.providers")


@dataclass
class AIResponse:
    """Standardized AI provider response."""

    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetStatus:
    """Current budget status."""

    mode: str  # normal, reduced_cloud, minimal_cloud, local_only
    remaining: float
    spent: float
    ratio: float
    message: str


class AIProvider(ABC):
    """Abstract base class for all AI providers.

    All providers (local, OpenAI, Gemini, Claude, Grok) must implement
    this interface. The system uses this abstraction to switch providers
    without coupling to any specific company.
    """

    provider_name: str = "base"
    is_local: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: str | None = None,
    ) -> AIResponse:
        """Generate a text completion.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt for context.
            temperature: Sampling temperature (0=deterministic, 1=creative).
            max_tokens: Maximum tokens to generate.
            response_format: Optional format hint (e.g. "json").

        Returns:
            AIResponse with content and metadata.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available.

        Returns:
            True if the provider is reachable and operational.
        """
        pass

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate the cost of a request.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        return (input_tokens / 1000 * self.cost_per_1k_input) + (
            output_tokens / 1000 * self.cost_per_1k_output
        )

    async def classify(self, text: str, categories: list[str]) -> AIResponse:
        """Classify text into one of the given categories.

        Default implementation uses generate() with a classification prompt.
        """
        prompt = f"""Classify the following text into exactly one of these categories: {", ".join(categories)}.

Text: {text}

Respond with only the category name, nothing else."""
        return await self.generate(prompt=prompt, temperature=0.0, max_tokens=50)

    async def summarize(self, text: str, max_words: int = 100) -> AIResponse:
        """Summarize the given text.

        Default implementation uses generate() with a summarization prompt.
        """
        prompt = f"""Summarize the following text in at most {max_words} words. Focus on key facts and market-relevant information.

Text: {text}"""
        return await self.generate(prompt=prompt, temperature=0.3, max_tokens=256)
