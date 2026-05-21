from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CORE_PACKAGE_DIR = ROOT_DIR / "packages" / "jarvis-core"
if str(CORE_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_PACKAGE_DIR))

from jarvis_core.assistant import JarvisAssistant
from jarvis_core.config import load_settings
from jarvis_core.llm.mock import MockModelProvider
from jarvis_core.logging import configure_logging


def build_assistant() -> JarvisAssistant:
    settings = load_settings()
    configure_logging(settings.log_level)

    provider = MockModelProvider(model_name=settings.model_name)
    return JarvisAssistant(model_provider=provider)


def main() -> None:
    assistant = build_assistant()

    print("J.A.R.V.I.S. online. Type 'exit' or 'quit' to end the session.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("J.A.R.V.I.S.: Session closed.")
            return

        if not user_input:
            continue

        response = assistant.respond(user_input)
        print(f"J.A.R.V.I.S.: {response}")


if __name__ == "__main__":
    main()
