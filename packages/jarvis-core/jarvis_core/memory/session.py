from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationSession:
    id: str
    title: str | None
    message_count: int
    created_at: str
    updated_at: str

