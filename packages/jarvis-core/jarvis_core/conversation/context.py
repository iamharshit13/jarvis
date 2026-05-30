from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.conversation.message import Message


@dataclass(frozen=True)
class ContextWindow:
    max_messages: int = 20
    max_chars: int = 12000

    def select(self, messages: list[Message]) -> list[Message]:
        selected: list[Message] = []
        total_chars = 0

        for message in reversed(messages[-self.max_messages :]):
            message_chars = len(message.content)
            if selected and total_chars + message_chars > self.max_chars:
                break
            selected.append(message)
            total_chars += message_chars

        selected.reverse()
        return selected

