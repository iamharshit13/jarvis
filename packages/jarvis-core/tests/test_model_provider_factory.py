import unittest

from jarvis_core.config import Settings
from jarvis_core.llm.factory import build_model_provider
from jarvis_core.llm.mock import MockModelProvider
from jarvis_core.llm.openai_compatible import OpenAICompatibleProvider


class ModelProviderFactoryTests(unittest.TestCase):
    def test_builds_mock_provider_from_settings(self) -> None:
        provider = build_model_provider(
            Settings(model_provider="mock", model_name="jarvis-test-model")
        )

        self.assertIsInstance(provider, MockModelProvider)
        self.assertEqual(provider.model_name, "jarvis-test-model")

    def test_rejects_unsupported_provider(self) -> None:
        with self.assertRaises(ValueError):
            build_model_provider(Settings(model_provider="unknown"))

    def test_builds_openai_compatible_provider_from_settings(self) -> None:
        provider = build_model_provider(
            Settings(
                model_provider="openai",
                model_name="gpt-test",
                openai_api_key="test-key",
                openai_base_url="https://example.test/v1",
            )
        )

        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertEqual(provider.model_name, "gpt-test")

    def test_openai_provider_requires_api_key(self) -> None:
        with self.assertRaises(ValueError):
            build_model_provider(Settings(model_provider="openai", openai_api_key=""))


if __name__ == "__main__":
    unittest.main()
