import tempfile
import unittest
from pathlib import Path

from jarvis_core.conversation.message import Message
from jarvis_core.memory import SQLiteConversationMemory


class SQLiteConversationMemoryTests(unittest.TestCase):
    def test_persists_messages_for_session(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "jarvis.sqlite3"
            memory = SQLiteConversationMemory(str(db_path))

            memory.create_session("session-1")
            memory.add_message("session-1", Message(role="user", content="Hello"))
            memory.add_message("session-1", Message(role="assistant", content="Online"))

            messages = memory.list_messages("session-1")

            self.assertEqual([message.role for message in messages], ["user", "assistant"])
            self.assertEqual([message.content for message in messages], ["Hello", "Online"])

    def test_clear_session_deletes_messages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "jarvis.sqlite3"
            memory = SQLiteConversationMemory(str(db_path))

            memory.add_message("session-1", Message(role="user", content="Hello"))
            memory.clear_session("session-1")

            self.assertEqual(memory.list_messages("session-1"), [])

    def test_lists_recent_sessions_with_message_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "jarvis.sqlite3"
            memory = SQLiteConversationMemory(str(db_path))

            memory.add_message("session-1", Message(role="user", content="Hello"))
            memory.add_message("session-2", Message(role="user", content="Status"))
            memory.add_message("session-2", Message(role="assistant", content="Online"))

            sessions = memory.list_sessions()

            session_counts = {session.id: session.message_count for session in sessions}
            self.assertEqual(session_counts["session-1"], 1)
            self.assertEqual(session_counts["session-2"], 2)


if __name__ == "__main__":
    unittest.main()
