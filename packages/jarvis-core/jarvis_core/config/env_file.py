from __future__ import annotations

import os
from pathlib import Path


def load_env_file(start_dir: Path | None = None, file_name: str = ".env") -> Path | None:
    env_path = find_env_file(start_dir=start_dir, file_name=file_name)
    if env_path is None:
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        key, value = parse_env_line(raw_line)
        if key and key not in os.environ:
            os.environ[key] = value

    return env_path


def find_env_file(start_dir: Path | None = None, file_name: str = ".env") -> Path | None:
    current = (start_dir or Path.cwd()).resolve()

    for directory in (current, *current.parents):
        candidate = directory / file_name
        if candidate.is_file():
            return candidate

    return None


def parse_env_line(line: str) -> tuple[str | None, str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None, ""

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()

    if not key:
        return None, ""

    if value.startswith(("'", '"')) and value.endswith(value[0]):
        value = value[1:-1]

    return key, value

