# Memory

Memory will be introduced after the first conversational core is stable.

Initial memory goals:

* conversation sessions
* message persistence
* user preferences
* searchable history
* deletion and review controls

Current implementation:

* SQLite stores conversation sessions and messages at `data/jarvis.sqlite3` by default.
* The CLI writes each user and assistant message to the current session.
* `--session-id <id>` resumes or creates a named session.
* `JARVIS_SESSION_ID` can set a default session in `.env`.
* `/history` shows the active in-memory session history.
* `/session` shows the active session id.
* `/sessions` lists recent stored sessions.
* `/clear` deletes messages for the current session.
