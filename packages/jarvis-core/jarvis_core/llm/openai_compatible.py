from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass

from jarvis_core.conversation.message import Message


@dataclass(frozen=True)
class OpenAICompatibleProvider:
    model_name: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required when JARVIS_MODEL_PROVIDER=openai.")

    def complete(self, messages: list[Message]) -> str:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
                if message.role in {"system", "user", "assistant"}
            ],
        }

        request = urllib.request.Request(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except TimeoutError as error:
            raise RuntimeError(
                f"Model provider request timed out after {self.timeout_seconds:g} seconds. "
                "For local LM Studio models, increase OPENAI_TIMEOUT_SECONDS in .env."
            ) from error
        except socket.timeout as error:
            raise RuntimeError(
                f"Model provider request timed out after {self.timeout_seconds:g} seconds. "
                "For local LM Studio models, increase OPENAI_TIMEOUT_SECONDS in .env."
            ) from error
        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Model provider request failed: {error.code} {error_body}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"Model provider request failed: {error.reason}") from error

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError(f"Unexpected model provider response: {data}") from error

        if not isinstance(content, str):
            raise RuntimeError(f"Unexpected model provider message content: {content}")

        return content
