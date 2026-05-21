from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.conversation.message import Message
from jarvis_core.llm.base import ModelProvider
from jarvis_core.prompts import DEFAULT_SYSTEM_PROMPT


@dataclass
class JarvisAssistant:
    """Minimal assistant loop for the first alive version."""

    model_provider: ModelProvider
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    history: list[Message] = field(default_factory=list)

    def respond(self, user_input: str) -> str:
        user_message = Message(role="user", content=user_input)
        self.history.append(user_message)

        assistant_text = self.model_provider.complete(self.messages_for_model())
        assistant_message = Message(role="assistant", content=assistant_text)
        self.history.append(assistant_message)

        return assistant_text

    def messages_for_model(self) -> list[Message]:
        system_message = Message(role="system", content=self.system_prompt)
        return [system_message, *self.history]
