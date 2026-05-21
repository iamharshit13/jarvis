from __future__ import annotations

from jarvis_core.config import Settings
from jarvis_core.llm.base import ModelProvider
from jarvis_core.llm.mock import MockModelProvider
from jarvis_core.llm.openai_compatible import OpenAICompatibleProvider


def build_model_provider(settings: Settings) -> ModelProvider:
    provider_name = settings.model_provider.strip().lower()

    if provider_name == "mock":
        return MockModelProvider(model_name=settings.model_name)

    if provider_name in {"openai", "openai-compatible"}:
        return OpenAICompatibleProvider(
            model_name=settings.model_name,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout_seconds=settings.openai_timeout_seconds,
        )

    supported_providers = "mock, openai, openai-compatible"
    raise ValueError(
        f"Unsupported model provider '{settings.model_provider}'. "
        f"Supported providers: {supported_providers}."
    )
