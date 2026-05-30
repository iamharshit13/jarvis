from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ToolContext:
    root_dir: Path


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, str] = field(default_factory=dict)
    requires_confirmation: bool = False


@dataclass(frozen=True)
class ToolResult:
    content: str
    metadata: dict[str, str] = field(default_factory=dict)


class Tool(Protocol):
    definition: ToolDefinition

    def run(self, args: dict[str, str], context: ToolContext) -> ToolResult:
        """Execute a tool with string arguments."""

