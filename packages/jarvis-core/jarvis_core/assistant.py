from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.conversation.message import Message
from jarvis_core.llm.base import ModelProvider


@dataclass
class JarvisAssistant:
    """Minimal assistant loop for the first alive version."""

    model_provider: ModelProvider
    history: list[Message] = field(default_factory=list)

    def respond(self, user_input: str) -> str:
        user_message = Message(role="user", content=user_input)
        self.history.append(user_message)

        assistant_text = self.model_provider.complete(self.history)
        assistant_message = Message(role="assistant", content=assistant_text)
        self.history.append(assistant_message)

        return assistant_text

