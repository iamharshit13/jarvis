from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.conversation.message import Message


@dataclass(frozen=True)
class MockModelProvider:
    model_name: str = "jarvis-mock"

    def complete(self, messages: list[Message]) -> str:
        latest_user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            "",
        )
        return (
            "I am online. "
            f"You said: {latest_user_message}. "
            "The first conversational core is ready for expansion."
        )

