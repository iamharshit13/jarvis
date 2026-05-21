from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    env: str = "development"
    log_level: str = "INFO"
    model_provider: str = "mock"
    model_name: str = "jarvis-mock"
    memory_db_path: str = "data/jarvis.sqlite3"


def load_settings() -> Settings:
    return Settings(
        env=os.getenv("JARVIS_ENV", Settings.env),
        log_level=os.getenv("JARVIS_LOG_LEVEL", Settings.log_level),
        model_provider=os.getenv("JARVIS_MODEL_PROVIDER", Settings.model_provider),
        model_name=os.getenv("JARVIS_MODEL_NAME", Settings.model_name),
        memory_db_path=os.getenv("JARVIS_MEMORY_DB_PATH", Settings.memory_db_path),
    )

