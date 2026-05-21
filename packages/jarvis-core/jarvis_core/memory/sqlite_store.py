from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from jarvis_core.conversation.message import Message
from jarvis_core.memory.session import ConversationSession


@dataclass(frozen=True)
class SQLiteConversationMemory:
    db_path: str

    def __post_init__(self) -> None:
        path = self._resolved_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def create_session(self, session_id: str, title: str | None = None) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions (id, title, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, title),
            )

    def add_message(self, session_id: str, message: Message) -> None:
        self.create_session(session_id)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages (session_id, role, content, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (session_id, message.role, message.content),
            )
            connection.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,),
            )

    def list_messages(self, session_id: str) -> list[Message]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        return [Message(role=row["role"], content=row["content"]) for row in rows]

    def list_sessions(self, limit: int = 10) -> list[ConversationSession]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    sessions.id,
                    sessions.title,
                    sessions.created_at,
                    sessions.updated_at,
                    COUNT(messages.id) AS message_count
                FROM sessions
                LEFT JOIN messages ON messages.session_id = sessions.id
                GROUP BY sessions.id
                ORDER BY sessions.updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            ConversationSession(
                id=row["id"],
                title=row["title"],
                message_count=row["message_count"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def clear_session(self, session_id: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            connection.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,),
            )

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(id)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_session_id
                ON messages(session_id, id)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sessions_updated_at
                ON sessions(updated_at)
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._resolved_path())
        connection.row_factory = sqlite3.Row
        return connection

    def _resolved_path(self) -> Path:
        path = Path(self.db_path).expanduser()
        if path.is_absolute():
            return path
        return Path.cwd() / path
