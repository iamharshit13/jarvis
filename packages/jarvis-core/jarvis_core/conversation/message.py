from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


MessageRole = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class Message:
    role: MessageRole
    content: str

