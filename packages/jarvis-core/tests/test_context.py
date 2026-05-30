import unittest

from jarvis_core.conversation import ContextWindow, Message


class ContextWindowTests(unittest.TestCase):
    def test_selects_recent_messages_by_count(self) -> None:
        messages = [
            Message(role="user", content=f"message-{index}")
            for index in range(5)
        ]

        selected = ContextWindow(max_messages=2, max_chars=1000).select(messages)

        self.assertEqual([message.content for message in selected], ["message-3", "message-4"])

    def test_selects_recent_messages_by_char_budget(self) -> None:
        messages = [
            Message(role="user", content="old"),
            Message(role="assistant", content="medium"),
            Message(role="user", content="latest"),
        ]

        selected = ContextWindow(max_messages=10, max_chars=8).select(messages)

        self.assertEqual([message.content for message in selected], ["latest"])


if __name__ == "__main__":
    unittest.main()
