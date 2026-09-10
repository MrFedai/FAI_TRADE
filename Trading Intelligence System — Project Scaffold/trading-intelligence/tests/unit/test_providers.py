"""Tests for AI provider abstraction."""

import pytest

from ai.providers.base import AIProvider, AIResponse


class DummyProvider(AIProvider):
    """Test implementation of AIProvider."""

    provider_name = "dummy"
    is_local = True

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: str | None = None,
    ) -> AIResponse:
        return AIResponse(
            content="test response",
            provider=self.provider_name,
            model="dummy-model",
            input_tokens=10,
            output_tokens=5,
            estimated_cost=0.0,
            latency_ms=100,
        )

    async def health_check(self) -> bool:
        return True


def test_ai_response_creation() -> None:
    """AIResponse should be created with required fields."""
    response = AIResponse(
        content="hello",
        provider="test",
        model="test-model",
    )
    assert response.content == "hello"
    assert response.provider == "test"
    assert response.input_tokens == 0
    assert response.estimated_cost == 0.0


def test_provider_estimate_cost() -> None:
    """estimate_cost should calculate correctly for zero-cost local provider."""
    provider = DummyProvider()
    cost = provider.estimate_cost(input_tokens=1000, output_tokens=500)
    assert cost == 0.0  # Local provider is free


@pytest.mark.asyncio
async def test_provider_generate() -> None:
    """generate should return an AIResponse."""
    provider = DummyProvider()
    response = await provider.generate(prompt="test")
    assert response.content == "test response"
    assert response.provider == "dummy"


@pytest.mark.asyncio
async def test_provider_classify() -> None:
    """classify should use generate with a classification prompt."""
    provider = DummyProvider()
    response = await provider.classify("test text", ["positive", "negative"])
    assert response.content == "test response"


@pytest.mark.asyncio
async def test_provider_summarize() -> None:
    """summarize should use generate with a summarization prompt."""
    provider = DummyProvider()
    response = await provider.summarize("test text to summarize")
    assert response.content == "test response"


@pytest.mark.asyncio
async def test_provider_health_check() -> None:
    """health_check should return True."""
    provider = DummyProvider()
    assert await provider.health_check() is True
