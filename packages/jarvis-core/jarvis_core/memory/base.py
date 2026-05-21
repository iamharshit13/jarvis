from __future__ import annotations

from typing import Protocol

from jarvis_core.conversation.message import Message
from jarvis_core.memory.session import ConversationSession


class ConversationMemory(Protocol):
    def create_session(self, session_id: str, title: str | None = None) -> None:
        """Create a conversation session if it does not exist."""

    def add_message(self, session_id: str, message: Message) -> None:
        """Persist a message in a conversation session."""

    def list_messages(self, session_id: str) -> list[Message]:
        """Return messages for a conversation session in chronological order."""

    def list_sessions(self, limit: int = 10) -> list[ConversationSession]:
        """Return recent conversation sessions."""

    def clear_session(self, session_id: str) -> None:
        """Delete messages from a conversation session."""
