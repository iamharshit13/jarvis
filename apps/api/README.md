# J.A.R.V.I.S. API

The API app exposes the assistant core to local web, desktop, and integration surfaces.

Current implementation:

* standard-library HTTP server
* static web app serving
* chat message endpoint
* history and session endpoints
* SQLite-backed session memory

Run:

```bash
python3 apps/api/server.py
```

Then open `http://127.0.0.1:8765`.

Planned stack later:

* FastAPI
* WebSockets for streaming events
* authenticated local endpoints
* audit-safe tool execution APIs
