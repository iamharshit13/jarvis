from __future__ import annotations

import os
from dataclasses import dataclass

from jarvis_core.config.env_file import load_env_file


@dataclass(frozen=True)
class Settings:
    env: str = "development"
    log_level: str = "INFO"
    model_provider: str = "mock"
    model_name: str = "jarvis-mock"
    memory_db_path: str = "data/jarvis.sqlite3"
    session_id: str = ""
    system_prompt_path: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_timeout_seconds: float = 30.0


def load_settings() -> Settings:
    load_env_file()

    return Settings(
        env=os.getenv("JARVIS_ENV", Settings.env),
        log_level=os.getenv("JARVIS_LOG_LEVEL", Settings.log_level),
        model_provider=os.getenv("JARVIS_MODEL_PROVIDER", Settings.model_provider),
        model_name=os.getenv("JARVIS_MODEL_NAME", Settings.model_name),
        memory_db_path=os.getenv("JARVIS_MEMORY_DB_PATH", Settings.memory_db_path),
        session_id=os.getenv("JARVIS_SESSION_ID", Settings.session_id),
        system_prompt_path=os.getenv("JARVIS_SYSTEM_PROMPT_PATH", Settings.system_prompt_path),
        openai_api_key=os.getenv("OPENAI_API_KEY", Settings.openai_api_key),
        openai_base_url=os.getenv("OPENAI_BASE_URL", Settings.openai_base_url),
        openai_timeout_seconds=float(
            os.getenv("OPENAI_TIMEOUT_SECONDS", str(Settings.openai_timeout_seconds))
        ),
    )
