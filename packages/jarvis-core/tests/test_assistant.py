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

    def test_messages_for_model_include_system_prompt_without_storing_it_in_history(self) -> None:
        assistant = JarvisAssistant(
            model_provider=MockModelProvider(),
            system_prompt="You are test J.A.R.V.I.S.",
        )

        assistant.respond("Run diagnostics")
        model_messages = assistant.messages_for_model()

        self.assertEqual(model_messages[0].role, "system")
        self.assertEqual(model_messages[0].content, "You are test J.A.R.V.I.S.")
        self.assertEqual(len(assistant.history), 2)


if __name__ == "__main__":
    unittest.main()
