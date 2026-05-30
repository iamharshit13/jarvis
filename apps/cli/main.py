from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

ROOT_DIR = Path(__file__).resolve().parents[2]
CORE_PACKAGE_DIR = ROOT_DIR / "packages" / "jarvis-core"
if str(CORE_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_PACKAGE_DIR))

from jarvis_core.assistant import JarvisAssistant
from jarvis_core.config import load_settings
from jarvis_core.config.settings import Settings
from jarvis_core.conversation import ContextWindow
from jarvis_core.llm import build_model_provider
from jarvis_core.logging import configure_logging
from jarvis_core.memory import SQLiteConversationMemory
from jarvis_core.prompts import load_system_prompt


@dataclass(frozen=True)
class CliRuntime:
    assistant: JarvisAssistant
    settings: Settings
    memory: SQLiteConversationMemory


def build_runtime(session_id_override: str | None = None) -> CliRuntime:
    settings = load_settings()
    configure_logging(settings.log_level)

    provider = build_model_provider(settings)
    system_prompt = load_system_prompt(settings.system_prompt_path)
    memory = SQLiteConversationMemory(settings.memory_db_path)
    session_id = session_id_override or settings.session_id or str(uuid4())
    assistant = JarvisAssistant(
        model_provider=provider,
        system_prompt=system_prompt,
        context_window=ContextWindow(
            max_messages=settings.context_max_messages,
            max_chars=settings.context_max_chars,
        ),
        memory=memory,
        session_id=session_id,
    )
    return CliRuntime(assistant=assistant, settings=settings, memory=memory)


def main() -> None:
    args = parse_args()
    try:
        runtime = build_runtime(session_id_override=args.session_id)
    except ValueError as error:
        print(f"J.A.R.V.I.S. startup failed: {error}")
        return

    assistant = runtime.assistant

    print(
        "J.A.R.V.I.S. online. "
        f"Session: {assistant.session_id}. Type '/help', 'exit', or 'quit'."
    )
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit", "/exit", "/quit"}:
            print("J.A.R.V.I.S.: Session closed.")
            return

        if not user_input:
            continue

        if user_input.startswith("/"):
            handle_command(user_input, runtime)
            continue

        try:
            response = assistant.respond(user_input)
        except RuntimeError as error:
            print(f"J.A.R.V.I.S.: Model provider error: {error}")
            continue

        print(f"J.A.R.V.I.S.: {response}")


def handle_command(command: str, runtime: CliRuntime) -> None:
    normalized = command.strip().lower()
    assistant = runtime.assistant
    settings = runtime.settings

    if normalized == "/help":
        print(
            "J.A.R.V.I.S.: Commands: /help, /status, /model, /history, "
            "/session, /sessions, /clear, /exit"
        )
        return

    if normalized == "/status":
        context = assistant.context_stats()
        print(
            "J.A.R.V.I.S.: "
            f"provider={settings.model_provider}, "
            f"model={settings.model_name}, "
            f"session={assistant.session_id}, "
            f"messages={len(assistant.history)}, "
            f"model_context={context['model_messages']}/{context['stored_messages']}, "
            f"memory={settings.memory_db_path}"
        )
        return

    if normalized == "/model":
        print(
            "J.A.R.V.I.S.: "
            f"provider={settings.model_provider}, "
            f"model={settings.model_name}, "
            f"base_url={settings.openai_base_url}"
        )
        return

    if normalized == "/history":
        print_history(assistant)
        return

    if normalized == "/session":
        context = assistant.context_stats()
        print(
            "J.A.R.V.I.S.: "
            f"session={assistant.session_id}, "
            f"messages={len(assistant.history)}, "
            f"model_context={context['model_messages']} messages, "
            f"{context['model_chars']} chars"
        )
        return

    if normalized == "/sessions":
        print_sessions(runtime)
        return

    if normalized == "/clear":
        assistant.clear_history()
        print("J.A.R.V.I.S.: Conversation history cleared for this session.")
        return

    print("J.A.R.V.I.S.: Unknown command. Type /help for available commands.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. CLI.")
    parser.add_argument(
        "--session-id",
        help="Resume or create a specific conversation session.",
    )
    return parser.parse_args()


def print_history(assistant: JarvisAssistant) -> None:
    if not assistant.history:
        print("J.A.R.V.I.S.: No conversation history in this session yet.")
        return

    print("J.A.R.V.I.S.: Current session history:")
    for index, message in enumerate(assistant.history, start=1):
        content = message.content.replace("\n", " ")
        if len(content) > 120:
            content = f"{content[:117]}..."
        print(f"{index}. {message.role}: {content}")


def print_sessions(runtime: CliRuntime) -> None:
    sessions = runtime.memory.list_sessions()
    if not sessions:
        print("J.A.R.V.I.S.: No saved sessions yet.")
        return

    print("J.A.R.V.I.S.: Recent sessions:")
    for session in sessions:
        marker = "*" if session.id == runtime.assistant.session_id else " "
        title = session.title or "Untitled"
        print(
            f"{marker} {session.id} | messages={session.message_count} | "
            f"updated={session.updated_at} | {title}"
        )


if __name__ == "__main__":
    main()
