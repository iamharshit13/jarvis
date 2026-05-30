# J.A.R.V.I.S.

Just A Rather Very Intelligent System

J.A.R.V.I.S. is an experimental AI operating system project inspired by Iron Man. The long-term vision lives in [docs/vision.md](https://github.com/iamharshit13/jarvis/blob/main/docs/vision.md). This README is focused on development: how the project is structured, how to run it, and what to build next.

Current status: **Milestone 1 — First Alive Version** has started. The repository contains a runnable CLI, a mock model provider, a core assistant loop, basic configuration, logging, and a standard-library test.

---

## Quick Start

Run the local CLI:

```bash
python3 apps/cli/main.py
```

Run the local web app:

```bash
./scripts/web.sh
```

Then open:

```text
http://127.0.0.1:8765
```

Resume or create a specific session:

```bash
python3 apps/cli/main.py --session-id main
```

Or use the helper script:

```bash
./scripts/dev.sh
```

Run tests:

```bash
./scripts/test.sh
```

Run a quick non-interactive smoke test:

```bash
printf 'hello\nexit\n' | python3 apps/cli/main.py
```

The first version uses a mock model provider by default, so it works without API keys.

CLI commands:

```text
/help
/status
/model
/history
/session
/sessions
/tools
/tool
/clear
/exit
```

---

## Development Goals

The project should grow through small runnable slices. Each slice should add a real capability without hiding complexity behind fragile demos.

Current priorities:

1. Keep the project runnable from the terminal.
2. Add model providers behind a stable interface.
3. Add memory without coupling it to one model vendor.
4. Add tools with safety checks and audit logs.
5. Add voice, agents, and multimodal perception after the core loop is stable.

---

## Current Architecture

The current implementation is intentionally small:

```text
User input
  -> CLI app
  -> JarvisAssistant
  -> ModelProvider interface
  -> MockModelProvider or OpenAICompatibleProvider
  -> SQLite conversation memory
  -> assistant response
```

Key files:

* [apps/cli/main.py](https://github.com/iamharshit13/jarvis/blob/main/apps/cli/main.py) — terminal entry point
* [apps/api/server.py](https://github.com/iamharshit13/jarvis/blob/main/apps/api/server.py) — local web/API server
* [apps/web/index.html](https://github.com/iamharshit13/jarvis/blob/main/apps/web/index.html) — browser interface
* [packages/jarvis-core/jarvis_core/assistant.py](https://github.com/iamharshit13/jarvis/blob/main/packages/jarvis-core/jarvis_core/assistant.py) — core assistant loop
* [packages/jarvis-core/jarvis_core/llm/base.py](https://github.com/iamharshit13/jarvis/blob/main/packages/jarvis-core/jarvis_core/llm/base.py) — model provider contract
* [packages/jarvis-core/jarvis_core/llm/factory.py](https://github.com/iamharshit13/jarvis/blob/main/packages/jarvis-core/jarvis_core/llm/factory.py) — provider selection
* [packages/jarvis-core/jarvis_core/llm/mock.py](https://github.com/iamharshit13/jarvis/blob/main/packages/jarvis-core/jarvis_core/llm/mock.py) — offline mock provider
* [packages/jarvis-core/jarvis_core/llm/openai_compatible.py](https://github.com/iamharshit13/jarvis/blob/main/packages/jarvis-core/jarvis_core/llm/openai_compatible.py) — OpenAI-compatible provider
* [packages/jarvis-core/jarvis_core/config/settings.py](https://github.com/iamharshit13/jarvis/blob/main/packages/jarvis-core/jarvis_core/config/settings.py) — environment-based settings
* [packages/jarvis-core/jarvis_core/memory/sqlite_store.py](https://github.com/iamharshit13/jarvis/blob/main/packages/jarvis-core/jarvis_core/memory/sqlite_store.py) — SQLite conversation memory
* [packages/jarvis-core/tests/test_assistant.py](https://github.com/iamharshit13/jarvis/blob/main/packages/jarvis-core/tests/test_assistant.py) — first test

---

## Repository Structure

```text
jarvis/
  README.md
  pyproject.toml
  .env.example
  .gitignore

  apps/
    cli/
      README.md
      main.py
    api/
      README.md
      server.py
    web/
      README.md
      index.html
      styles.css
      app.js

  packages/
    jarvis-core/
      jarvis_core/
        config/
        conversation/
        llm/
        logging/
        memory/
        planning/
        safety/
        tools/
      tests/

  docs/
    agents.md
    architecture.md
    memory.md
    roadmap.md
    safety.md
    tools.md
    vision.md
    voice.md

  scripts/
    dev.sh
    test.sh
    lint.sh

  data/
    .gitkeep

  logs/
    .gitkeep
```

Planned packages:

* `jarvis-core` — conversation, model providers, memory contracts, tool contracts, planning contracts, safety
* `jarvis-voice` — speech-to-text, text-to-speech, wake word, interruption handling
* `jarvis-vision` — OCR, screenshot understanding, camera and image analysis
* `jarvis-agents` — planners, workers, background workflows
* `jarvis-integrations` — filesystem, shell, browser, calendar, email, Home Assistant, MQTT, robotics

---

## Configuration

Copy [.env.example](https://github.com/iamharshit13/jarvis/blob/main/.env.example) to `.env` when real providers are added.

Current environment variables:

```bash
JARVIS_ENV=development
JARVIS_LOG_LEVEL=INFO
JARVIS_MODEL_PROVIDER=mock
JARVIS_MODEL_NAME=jarvis-mock
JARVIS_MEMORY_DB_PATH=data/jarvis.sqlite3
JARVIS_SESSION_ID=
JARVIS_SYSTEM_PROMPT_PATH=
JARVIS_CONTEXT_MAX_MESSAGES=20
JARVIS_CONTEXT_MAX_CHARS=12000
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TIMEOUT_SECONDS=120
```

The project loads `.env` automatically from the current directory or a parent directory. Shell environment variables still take priority over values in `.env`.

Keep real secrets only in `.env` or your shell environment. Do not commit API keys, local tokens, generated databases, or logs.

---

## Buildable Slices

### Slice 0 — Project Foundation

Goal: create the base repository, development workflow, configuration system, and documentation.

Status: in progress.

Delivered:

* project structure
* Python project config
* environment variable defaults
* logging setup
* basic test
* helper scripts
* development-oriented README
* separate vision document

Next:

* add dependency installation workflow
* add linting dependencies or standardize on no-dependency checks for now
* add contribution notes

### Slice 1 — Text-Based Conversational Core

Goal: build the first usable assistant loop through a terminal or simple local interface.

Status: started.

Delivered:

* user input loop
* CLI commands
* local web chat interface
* model provider interface
* mock provider
* OpenAI-compatible provider
* provider selection from settings
* default J.A.R.V.I.S. system prompt
* optional custom system prompt path
* conversation history in memory
* SQLite-backed conversation persistence
* session resume by id
* context window limits for local model performance
* safe read-only tool registry

Next:

* streaming responses
* conversation summarization after context limits are reached

### Slice 2 — Tool Calling & Local Actions

Goal: allow J.A.R.V.I.S. to execute approved local tools safely.

Planned:

* tool registry
* typed tool schemas
* confirmation flow for risky actions
* safe file reading tool
* guarded shell command tool
* audit log of actions

### Slice 3 — Memory System

Goal: make conversations persistent and personalized.

Planned:

* short-term memory
* SQLite-backed conversation history
* user preferences
* searchable conversation history
* vector search later
* memory review and deletion controls

### Slice 4 — Planning Engine

Goal: convert broad user goals into structured plans and task execution.

Planned:

* task decomposition
* planner state
* step-by-step execution
* progress tracking
* interruption and resume support
* plan explanation

### Slice 5 — Voice Interface

Goal: make J.A.R.V.I.S. conversational through speech.

Planned:

* speech-to-text interface
* text-to-speech interface
* push-to-talk mode
* wake-word support
* interruption handling
* low-latency streaming

### Slice 6 — Desktop & App Automation

Goal: allow J.A.R.V.I.S. to help with real workflows on the local machine.

Planned:

* app launching
* file organization
* browser automation
* local task workflows
* calendar and email integrations
* permissioned desktop actions

### Slice 7 — Agentic Workflows

Goal: allow J.A.R.V.I.S. to run longer tasks through specialized agents.

Planned:

* agent roles
* task queues
* background jobs
* progress updates
* tool-specific agents
* failure recovery

### Slice 8 — Multimodal Perception

Goal: allow J.A.R.V.I.S. to understand images, screenshots, camera input, documents, and audio context.

Planned:

* screenshot understanding
* OCR
* document parsing
* camera feed analysis
* object recognition
* environment summaries

### Slice 9 — Smart Home & IoT Integration

Goal: connect J.A.R.V.I.S. to physical environments.

Planned:

* Home Assistant integration
* MQTT messaging
* device registry
* automation routines
* environment monitoring
* permission policies for physical actions

### Slice 10 — Robotics & Embodied Intelligence

Goal: extend J.A.R.V.I.S. into robotics and spatial intelligence.

Planned:

* ROS2 integration
* robot command interface
* telemetry ingestion
* mapping and navigation support
* drone or robotic arm experiments
* safety constraints

---

## Technical Stack

The stack should stay modular so pieces can be replaced as the system evolves.

Current:

* Python 3.11+
* standard library configuration and tests
* mock model provider
* terminal CLI

Near-term:

* Pydantic for typed settings and tool schemas
* SQLite for local memory
* FastAPI for local API
* WebSockets for streaming events
* Ruff for linting

Future:

* TypeScript for web and desktop surfaces
* PostgreSQL for larger deployments
* Redis for queues and short-lived state
* ChromaDB, Qdrant, Weaviate, or Pinecone for vector search
* Neo4j or Memgraph for knowledge graphs
* LangGraph, AutoGen, CrewAI, or a custom planner/executor loop
* OpenAI, Anthropic, Gemini, Ollama, llama.cpp, or vLLM model backends
* Whisper, Deepgram, AssemblyAI, OpenAI speech-to-text, ElevenLabs, Azure Neural Voices, or local TTS
* OpenCV, OCR engines, and multimodal models for perception
* Home Assistant, MQTT, ROS2, Docker, Kubernetes, REST APIs, and browser automation

---

## Development Process

Each feature should move through the same loop:

1. Define the slice.
2. Write the smallest useful interface.
3. Add typed schemas and configuration.
4. Implement the core behavior.
5. Add tests for the important paths.
6. Add logging and audit visibility.
7. Document usage.
8. Run the feature locally.
9. Tighten safety rules.
10. Move to the next slice.

Development rules:

* Keep every slice runnable.
* Prefer stable contracts over early framework commitment.
* Keep model providers replaceable.
* Keep tools permissioned and auditable.
* Keep memory inspectable and deletable.
* Add dependencies only when they earn their place.

---

## Immediate Next Tasks

1. Add audit logging for model calls and tool calls.
2. Add web UI support for manual tools.
3. Add conversation summarization after context limits are reached.

The first goal is still simple: make J.A.R.V.I.S. reliable as a local text assistant before expanding into voice, agents, perception, and automation.
