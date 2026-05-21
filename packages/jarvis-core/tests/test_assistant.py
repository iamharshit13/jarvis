import unittest

from jarvis_core.assistant import JarvisAssistant
from jarvis_core.llm.mock import MockModelProvider


class AssistantTests(unittest.TestCase):
    def test_assistant_responds_and_records_history(self) -> None:
        assistant = JarvisAssistant(model_provider=MockModelProvider())

        response = assistant.respond("Run diagnostics")

        self.assertIn("Run diagnostics", response)
        self.assertEqual(len(assistant.history), 2)
        self.assertEqual(assistant.history[0].role, "user")
        self.assertEqual(assistant.history[1].role, "assistant")


if __name__ == "__main__":
    unittest.main()
