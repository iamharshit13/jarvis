from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.tools.base import Tool, ToolContext, ToolDefinition, ToolResult


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self.tools[tool.definition.name] = tool

    def definitions(self) -> list[ToolDefinition]:
        return [tool.definition for tool in self.tools.values()]

    def run(self, name: str, args: dict[str, str], context: ToolContext) -> ToolResult:
        tool = self.tools.get(name)
        if tool is None:
            available = ", ".join(sorted(self.tools)) or "none"
            raise ValueError(f"Unknown tool '{name}'. Available tools: {available}.")
        return tool.run(args, context)

