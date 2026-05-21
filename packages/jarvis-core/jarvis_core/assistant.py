from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from jarvis_core.conversation.message import Message
from jarvis_core.llm.base import ModelProvider
from jarvis_core.memory import ConversationMemory
from jarvis_core.prompts import DEFAULT_SYSTEM_PROMPT


@dataclass
class JarvisAssistant:
    """Minimal assistant loop for the first alive version."""

    model_provider: ModelProvider
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    memory: ConversationMemory | None = None
    session_id: str = field(default_factory=lambda: str(uuid4()))
    history: list[Message] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.memory is None:
            return

        self.memory.create_session(self.session_id)
        if not self.history:
            self.history.extend(self.memory.list_messages(self.session_id))

    def respond(self, user_input: str) -> str:
        user_message = Message(role="user", content=user_input)
        self.history.append(user_message)
        if self.memory is not None:
            self.memory.add_message(self.session_id, user_message)

        assistant_text = self.model_provider.complete(self.messages_for_model())
        assistant_message = Message(role="assistant", content=assistant_text)
        self.history.append(assistant_message)
        if self.memory is not None:
            self.memory.add_message(self.session_id, assistant_message)

        return assistant_text

    def messages_for_model(self) -> list[Message]:
        system_message = Message(role="system", content=self.system_prompt)
        return [system_message, *self.history]

    def clear_history(self) -> None:
        self.history.clear()
        if self.memory is not None:
            self.memory.clear_session(self.session_id)
