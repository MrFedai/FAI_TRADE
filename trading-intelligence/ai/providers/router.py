"""AI provider router — selects the best provider based on task and budget."""

from __future__ import annotations

from ai.providers.base import AIProvider, AIResponse, BudgetStatus
from ai.providers.local import LocalProvider
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger("ai.router")


# Task type → provider priority (first available wins)
TASK_PRIORITY: dict[str, list[str]] = {
    "classification": ["local"],
    "summarization": ["local"],
    "sentiment": ["local"],
    "basic_reasoning": ["local"],
    "complex_reasoning": ["openai", "gemini", "claude"],
    "deep_research": ["claude", "openai"],
    "final_synthesis": ["claude", "openai"],
    "second_opinion": ["gemini", "claude"],
}


class ProviderRouter:
    """Routes AI requests to the appropriate provider based on task type and budget."""

    def __init__(self):
        self._providers: dict[str, AIProvider] = {}
        self._local = LocalProvider()
        self._providers["local"] = self._local
        self._init_cloud_providers()

    def _init_cloud_providers(self) -> None:
        """Initialize cloud providers if API keys are configured."""
        if settings.openai_api_key:
            try:
                from ai.providers.openai import OpenAIProvider
                self._providers["openai"] = OpenAIProvider()
            except ImportError:
                logger.warning("openai_provider_unavailable")
        if settings.gemini_api_key:
            try:
                from ai.providers.gemini import GeminiProvider
                self._providers["gemini"] = GeminiProvider()
            except ImportError:
                logger.warning("gemini_provider_unavailable")
        if settings.anthropic_api_key:
            try:
                from ai.providers.claude import ClaudeProvider
                self._providers["claude"] = ClaudeProvider()
            except ImportError:
                logger.warning("claude_provider_unavailable")

    def select_provider(self, task_type: str, budget: BudgetStatus | None = None) -> AIProvider:
        """Select the best provider for a given task type.

        Args:
            task_type: Type of task (classification, summarization, etc.)
            budget: Current budget status. If None or local_only, only local is used.

        Returns:
            An AIProvider instance.
        """
        if budget and budget.mode == "local_only":
            return self._local

        priority = TASK_PRIORITY.get(task_type, ["local"])

        for provider_name in priority:
            if provider_name in self._providers:
                provider = self._providers[provider_name]
                if provider_name == "local":
                    return provider
                # For cloud providers, check budget
                if budget and budget.mode == "minimal_cloud" and task_type not in (
                    "complex_reasoning", "deep_research", "final_synthesis",
                ):
                    continue
                return provider

        return self._local

    def get_provider(self, name: str) -> AIProvider | None:
        """Get a specific provider by name."""
        return self._providers.get(name)

    @property
    def local_provider(self) -> LocalProvider:
        """Get the local provider."""
        return self._local

    @property
    def available_providers(self) -> list[str]:
        """List available provider names."""
        return list(self._providers.keys())


# Singleton instance
router = ProviderRouter()
