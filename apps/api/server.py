from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
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
from jarvis_core.llm.base import ModelProvider
from jarvis_core.logging import configure_logging
from jarvis_core.memory import SQLiteConversationMemory
from jarvis_core.prompts import load_system_prompt

WEB_DIR = ROOT_DIR / "apps" / "web"


@dataclass(frozen=True)
class WebRuntime:
    settings: Settings
    model_provider: ModelProvider
    memory: SQLiteConversationMemory
    system_prompt: str
    default_session_id: str

    def build_assistant(self, session_id: str) -> JarvisAssistant:
        return JarvisAssistant(
            model_provider=self.model_provider,
            system_prompt=self.system_prompt,
            context_window=ContextWindow(
                max_messages=self.settings.context_max_messages,
                max_chars=self.settings.context_max_chars,
            ),
            memory=self.memory,
            session_id=session_id,
        )


def build_runtime(session_id: str | None = None) -> WebRuntime:
    settings = load_settings()
    configure_logging(settings.log_level)
    return WebRuntime(
        settings=settings,
        model_provider=build_model_provider(settings),
        memory=SQLiteConversationMemory(settings.memory_db_path),
        system_prompt=load_system_prompt(settings.system_prompt_path),
        default_session_id=session_id or settings.session_id or str(uuid4()),
    )


class JarvisRequestHandler(BaseHTTPRequestHandler):
    runtime: WebRuntime

    def do_GET(self) -> None:
        if self.path == "/api/status":
            self.write_json(
                {
                    "provider": self.runtime.settings.model_provider,
                    "model": self.runtime.settings.model_name,
                    "base_url": self.runtime.settings.openai_base_url,
                    "memory_db_path": self.runtime.settings.memory_db_path,
                    "default_session_id": self.runtime.default_session_id,
                    "context_max_messages": self.runtime.settings.context_max_messages,
                    "context_max_chars": self.runtime.settings.context_max_chars,
                }
            )
            return

        if self.path == "/api/sessions":
            self.write_json(
                {
                    "sessions": [
                        {
                            "id": session.id,
                            "title": session.title,
                            "message_count": session.message_count,
                            "created_at": session.created_at,
                            "updated_at": session.updated_at,
                        }
                        for session in self.runtime.memory.list_sessions()
                    ]
                }
            )
            return

        self.serve_static_file()

    def do_POST(self) -> None:
        if self.path == "/api/message":
            payload = self.read_json()
            message = str(payload.get("message", "")).strip()
            session_id = str(payload.get("session_id") or self.runtime.default_session_id)

            if not message:
                self.write_json({"error": "Message is required."}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                assistant = self.runtime.build_assistant(session_id)
                response = assistant.respond(message)
            except RuntimeError as error:
                self.write_json(
                    {"error": f"Model provider error: {error}"},
                    status=HTTPStatus.BAD_GATEWAY,
                )
                return

            self.write_json(
                {
                    "session_id": assistant.session_id,
                    "response": response,
                    "messages": [
                        {"role": item.role, "content": item.content}
                        for item in assistant.history
                    ],
                }
            )
            return

        if self.path == "/api/history":
            payload = self.read_json()
            session_id = str(payload.get("session_id") or self.runtime.default_session_id)
            messages = self.runtime.memory.list_messages(session_id)
            self.write_json(
                {
                    "session_id": session_id,
                    "messages": [
                        {"role": item.role, "content": item.content}
                        for item in messages
                    ],
                }
            )
            return

        if self.path == "/api/clear":
            payload = self.read_json()
            session_id = str(payload.get("session_id") or self.runtime.default_session_id)
            self.runtime.memory.clear_session(session_id)
            self.write_json({"session_id": session_id, "messages": []})
            return

        self.write_json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def serve_static_file(self) -> None:
        relative_path = "index.html" if self.path in {"/", ""} else self.path.lstrip("/")
        file_path = (WEB_DIR / relative_path).resolve()

        if not file_path.is_file() or WEB_DIR.resolve() not in file_path.parents:
            self.write_json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)
            return

        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
        }.get(file_path.suffix, "application/octet-stream")

        body = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length == 0:
            return {}
        raw_body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(raw_body)

    def write_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


def create_server(host: str, port: int, runtime: WebRuntime) -> ThreadingHTTPServer:
    handler = type(
        "ConfiguredJarvisRequestHandler",
        (JarvisRequestHandler,),
        {"runtime": runtime},
    )
    return ThreadingHTTPServer((host, port), handler)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. local web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--session-id", help="Resume or create a specific session.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        runtime = build_runtime(session_id=args.session_id)
    except ValueError as error:
        print(f"J.A.R.V.I.S. web startup failed: {error}")
        return

    server = create_server(args.host, args.port, runtime)
    print(f"J.A.R.V.I.S. web online: http://{args.host}:{args.port}")
    print(f"Session: {runtime.default_session_id}")
    server.serve_forever()


if __name__ == "__main__":
    main()
