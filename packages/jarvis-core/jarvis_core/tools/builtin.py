from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jarvis_core.tools.base import ToolContext, ToolDefinition, ToolResult
from jarvis_core.tools.registry import ToolRegistry


SENSITIVE_NAMES = {".env"}
SENSITIVE_SUFFIXES = {".db", ".sqlite", ".sqlite3"}


@dataclass(frozen=True)
class CurrentTimeTool:
    definition: ToolDefinition = ToolDefinition(
        name="current_time",
        description="Return the current local date and time.",
    )

    def run(self, args: dict[str, str], context: ToolContext) -> ToolResult:
        now = datetime.now().astimezone()
        return ToolResult(content=now.isoformat(timespec="seconds"))


@dataclass(frozen=True)
class ListDirectoryTool:
    definition: ToolDefinition = ToolDefinition(
        name="list_directory",
        description="List files and directories under the project root.",
        parameters={"path": "Relative directory path. Defaults to the project root."},
    )

    def run(self, args: dict[str, str], context: ToolContext) -> ToolResult:
        directory = resolve_safe_path(context.root_dir, args.get("path", "."))
        root = context.root_dir.resolve()
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory.relative_to(root)}")

        entries = []
        for child in sorted(directory.iterdir(), key=lambda item: (not item.is_dir(), item.name)):
            if is_sensitive_path(child):
                continue
            suffix = "/" if child.is_dir() else ""
            entries.append(f"{child.name}{suffix}")

        return ToolResult(
            content="\n".join(entries) if entries else "(empty)",
            metadata={"path": str(directory.relative_to(root))},
        )


@dataclass(frozen=True)
class ReadFileTool:
    max_chars: int = 40000
    definition: ToolDefinition = ToolDefinition(
        name="read_file",
        description="Read a text file under the project root.",
        parameters={"path": "Relative file path under the project root."},
    )

    def run(self, args: dict[str, str], context: ToolContext) -> ToolResult:
        raw_path = args.get("path")
        if not raw_path:
            raise ValueError("Missing required argument: path.")

        file_path = resolve_safe_path(context.root_dir, raw_path)
        root = context.root_dir.resolve()
        assert_not_sensitive(file_path)

        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path.relative_to(root)}")

        content = file_path.read_text(encoding="utf-8")
        truncated = len(content) > self.max_chars
        if truncated:
            content = content[: self.max_chars]

        metadata = {
            "path": str(file_path.relative_to(root)),
            "truncated": str(truncated).lower(),
        }
        return ToolResult(content=content, metadata=metadata)


@dataclass(frozen=True)
class ProjectStatusTool:
    definition: ToolDefinition = ToolDefinition(
        name="project_status",
        description="Return repository branch and short git status.",
    )

    def run(self, args: dict[str, str], context: ToolContext) -> ToolResult:
        branch = run_git(context.root_dir, ["branch", "--show-current"]) or "(unknown)"
        status = run_git(context.root_dir, ["status", "--short"]) or "clean"
        return ToolResult(content=f"branch: {branch}\nstatus:\n{status}")


def build_builtin_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CurrentTimeTool())
    registry.register(ListDirectoryTool())
    registry.register(ReadFileTool())
    registry.register(ProjectStatusTool())
    return registry


def resolve_safe_path(root_dir: Path, raw_path: str) -> Path:
    root = root_dir.resolve()
    candidate = (root / raw_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Path escapes the project root.")
    return candidate


def assert_not_sensitive(path: Path) -> None:
    if is_sensitive_path(path):
        raise ValueError("Refusing to read environment files.")
    if path.suffix in SENSITIVE_SUFFIXES:
        raise ValueError(f"Refusing to read generated database file: {path.name}")
    if path.name in SENSITIVE_NAMES:
        raise ValueError(f"Refusing to read sensitive file: {path.name}")


def is_sensitive_path(path: Path) -> bool:
    return any(part == ".env" or part.startswith(".env.") for part in path.parts)


def run_git(root_dir: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root_dir,
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        return result.stderr.strip()
    return result.stdout.strip()
