import unittest

from jarvis_core.assistant import JarvisAssistant
from jarvis_core.conversation import ContextWindow
from jarvis_core.conversation.message import Message
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

    def test_messages_for_model_are_context_limited(self) -> None:
        assistant = JarvisAssistant(
            model_provider=MockModelProvider(),
            system_prompt="system",
            context_window=ContextWindow(max_messages=1, max_chars=1000),
        )
        assistant.history.extend(
            [
                Message(role="user", content="old"),
                Message(role="assistant", content="new"),
            ]
        )

        model_messages = assistant.messages_for_model()

        self.assertEqual([message.content for message in model_messages], ["system", "new"])
        self.assertEqual(len(assistant.history), 2)

    def test_assistant_loads_existing_session_history(self) -> None:
        class InMemoryStore:
            def __init__(self) -> None:
                self.messages = [Message(role="user", content="Previous question")]

            def create_session(self, session_id: str, title: str | None = None) -> None:
                self.session_id = session_id

            def add_message(self, session_id: str, message: Message) -> None:
                self.messages.append(message)

            def list_messages(self, session_id: str) -> list[Message]:
                return list(self.messages)

            def list_sessions(self, limit: int = 10) -> list[object]:
                return []

            def clear_session(self, session_id: str) -> None:
                self.messages.clear()

        assistant = JarvisAssistant(
            model_provider=MockModelProvider(),
            memory=InMemoryStore(),
            session_id="existing-session",
        )

        self.assertEqual(len(assistant.history), 1)
        self.assertEqual(assistant.history[0].content, "Previous question")


if __name__ == "__main__":
    unittest.main()
