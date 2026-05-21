from __future__ import annotations

from typing import Protocol

from jarvis_core.conversation.message import Message


class ModelProvider(Protocol):
    model_name: str

    def complete(self, messages: list[Message]) -> str:
        """Return an assistant response for the current conversation."""

