# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

ReFlect Prompting Guide Agent — guides users in creating, evaluating, and improving AI prompts using the Gartner ReFlect framework (Role, Format, Language, Example, Context, Task). Built on AWS Strands Agents SDK.

## Commands

All commands assume the virtual environment is active (`source .venv/bin/activate`) or invoked via `.venv/bin/python`.

```sh
make install      # uv pip install -r requirements.txt && uv pip install -e .
make lint         # ruff check + ruff format --check (reports only)
make format       # ruff format . (auto-fixes formatting)
make typecheck    # mypy .
make test         # pytest
make run          # python main.py
```

Run the webchat UI directly:

```sh
python ui/webchat.py   # FastAPI server on http://localhost:8000
```

Run a single test:

```sh
pytest tests/test_foo.py::test_bar -v
```

## Environment

Requires a `.env` file (copy from `.env.example`). Two required variables:

- `DATABASE_URL`
- `SECRET_KEY`

Optional: `APP_ENV` (default: `development`), `DEBUG` (default: `true`).

## Architecture

```strcture
agent/
  __init__.py      # Agent instantiation — single `agent` export
  tools.py         # @tool-decorated functions (prompt_rubric_tool)
  skills.py        # @tool-decorated functions + Skill metadata instances
  system_prompt.md # System prompt text (not yet wired into agent.__init__)
ui/
  webchat.py       # FastAPI app that imports `agent` and exposes /chat endpoint
deploy/
  Dockerfile       # Container image build
  docker-compose.yml  # Local compose; run from repo root: docker compose -f deploy/docker-compose.yml up
  .dockerignore
config.py          # Pydantic BaseSettings (loads .env); exports `settings`
```

### Strands SDK patterns used

- **Tools** — plain functions decorated with `@tool` (from `strands`). Schema is inferred from type annotations and docstrings. Pass tool functions in `Agent(tools=[...])`.
- **Skills** — `Skill(name, description, instructions)` data objects wired to an agent via `AgentSkills` plugin (`Agent(plugins=[AgentSkills(skills=[...])])`). Skills are activated by the agent on demand via a built-in `skills` tool; they are not called directly.
- **Agent** is composed, not subclassed. All configuration goes into `Agent(...)` constructor parameters.

### Key dependency: `agent` module import

`ui/webchat.py` and any entry point import the live agent instance via `from agent import agent`. The module-level `agent = Agent(...)` in `agent/__init__.py` runs at import time, which means `.env` must be present before starting the server.

### Known gaps

- `ui/webchat.py` still calls `agent.skills[0].execute(...)` — this is stale code from the old `strands_agents` API and will raise `AttributeError`. The `/chat` endpoint needs to be rewritten to call the agent conversationally (`agent(user_msg)`).
- `agent/system_prompt.md` exists but is not loaded into the agent; wire it in `agent/__init__.py` via `system_prompt=Path("agent/system_prompt.md").read_text()`.
- `config.py` uses deprecated Pydantic v1 `BaseSettings` / inner `Config` class; should migrate to `pydantic-settings` with `model_config = SettingsConfigDict(...)`.
