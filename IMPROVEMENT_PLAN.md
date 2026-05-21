# IMPROVEMENT_PLAN.md

## ReFlect Prompting Agent — Quality Improvement Plan

---

## Executive Summary

The ReFlect Prompting Agent is an early-stage proof-of-concept built on the AWS Strands SDK. It has a sound architectural direction — composable tools, skills-as-data, FastAPI webchat — but carries substantial gaps across every quality dimension before it can be considered production-worthy.

**Three findings demand immediate action before any other work proceeds:**

1. The webchat `/chat` endpoint is publicly accessible with no authentication, wildcard CORS with credentials enabled, and an XSS vulnerability — any browser tab on the internet can exploit it.
2. There is zero logging, no `/health` endpoint, and no error handling in API routes, making the service invisible and fragile in any deployed environment.
3. All three agent tools (`evaluate_prompt`, `generate_prompt_template`, `prompt_rubric_tool`) are stubs — the agent's core value proposition does not function.

This plan organises 30+ identified gaps into five phased waves, ordered by business value delivered per implementation hour. Each wave is independently deployable and builds on the previous.

**Estimated total effort:** 60–80 engineering hours to reach production-ready state.

---

## Current State and Gaps

### Codebase Snapshot

| File | LOC | Status |
|------|-----|--------|
| `agent/__init__.py` | 16 | Working but fragile |
| `agent/skills.py` | 57 | Stubs + unused Skill objects |
| `agent/tools.py` | 21 | Stub |
| `ui/webchat.py` | 62 | Multiple critical defects |
| `config.py` | 11 | Pydantic v2 migrated; unused required fields |
| `skills/*/SKILL.md` | 5 files | Complete and correct |
| `tests/` | — | Does not exist |
| `Dockerfile` | — | Does not exist |
| `.github/workflows/` | — | Does not exist |
| `main.py` | — | Does not exist (`make run` broken) |

### Gap Summary by Attribute

| Quality Attribute | Severity | Gap Count | Blocker for Production? |
|---|---|---|---|
| Security | Critical / High | 9 | Yes |
| Availability | High | 5 | Yes |
| Observability | Critical | 4 | Yes |
| Maintainability | High | 8 | No (but high risk) |
| Performance | High | 4 | No |
| Cost | High | 3 | No |
| Portability | Medium | 4 | No |
| Scalability | Medium | 4 | No |

---

## Quality Characteristics Matrix

| Attribute | Current Score | Target Score | Key Driver |
|---|---|---|---|
| **Security** | 1 / 10 | 8 / 10 | CORS + XSS + no auth |
| **Availability** | 2 / 10 | 8 / 10 | No health check, no error handling |
| **Observability** | 0 / 10 | 8 / 10 | Zero logging anywhere |
| **Maintainability** | 2 / 10 | 8 / 10 | No tests, no CI, stub tools |
| **Performance** | 3 / 10 | 7 / 10 | Sync blocking, no streaming |
| **Cost** | 3 / 10 | 7 / 10 | No caching, no token tracking |
| **Portability** | 2 / 10 | 8 / 10 | No container, fragile imports |
| **Scalability** | 2 / 10 | 6 / 10 | Single worker, no pooling |

---

## Detailed Waves

---

### Wave 1 — Critical Fixes and Foundation
**Effort:** ~10 hours | **Value:** Unblocks safe operation

This wave fixes everything that is actively harmful or broken. No new features; only correctness and safety.

#### 1.1 Fix CORS configuration (`ui/webchat.py`)

Replace the wildcard origin with an explicit allowlist, and remove `allow_credentials=True`
until authentication is in place (Wave 2):

```python
allow_origins=settings.allowed_origins,   # read from ALLOWED_ORIGINS env var
allow_credentials=False,
allow_methods=["POST", "GET"],
allow_headers=["Content-Type"],
```

**Risk of not doing:** Cross-site credential theft from any page on the internet.

#### 1.2 Fix XSS in frontend (`ui/webchat.py`)

The webchat uses `element.innerHTML` to render both user input and agent replies,
allowing injected JavaScript to execute in the browser.

Fix: replace `innerHTML` assignment with `textContent` for user messages and
safe DOM node construction for agent replies. For rich markdown output, add
[DOMPurify](https://github.com/cure53/DOMPurify) before assigning HTML.

**Risk:** JavaScript injection from either user input or agent output.

#### 1.3 Add Pydantic input validation (`ui/webchat.py`)

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)

@app.post("/chat")
async def chat(req: ChatRequest):
    result = agent(req.message)
    return JSONResponse({"reply": str(result)})
```

Eliminates DoS via oversized payloads and validates Content-Type automatically.

#### 1.4 Add error handling and `/health` endpoint (`ui/webchat.py`)

```python
import logging
logger = logging.getLogger(__name__)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        result = agent(req.message)
        return JSONResponse({"reply": str(result)})
    except Exception:
        logger.exception("Agent call failed")
        return JSONResponse({"error": "Service unavailable"}, status_code=503)
```

#### 1.5 Set `debug=False` default (`config.py`)

```python
debug: bool = False
```

Debug mode exposes full stack traces in HTTP responses.

#### 1.6 Create `main.py` entry point

```python
import uvicorn
if __name__ == "__main__":
    uvicorn.run("ui.webchat:app", host="0.0.0.0", port=8000, reload=False)
```

Fixes broken `make run`.

#### 1.7 Make config required fields optional

`DATABASE_URL` and `SECRET_KEY` are required today but no code uses them.
Until they are implemented, make them optional to prevent startup failures
on missing `.env` entries:

```python
database_url: str | None = None
secret_key: str | None = None
```

#### 1.8 Clean up dead code

- Remove `PromptEvaluationSkill` / `PromptTemplateSkill` Skill object definitions from
  `agent/skills.py` — they are constructed but never passed to the agent.
- Fix the `Makefile` `lint` target: remove the trailing `ruff check --fix` that runs
  after `ruff format --check` (circular and confusing).
- Remove unused dependencies `python-dotenv`, `aiohttp`, `httpx`, `anyio` from
  `pyproject.toml` after confirming they are not used by any Wave 3+ feature.

**Wave 1 success metrics:**
- `/health` responds 200
- `/chat` returns 400 on missing or oversized `message`
- No CORS errors in browser console on localhost
- `make run` starts without error

---

### Wave 2 — Security Hardening
**Effort:** ~12 hours | **Value:** Required before any external access

#### 2.1 API key authentication

```python
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException

api_key_header = APIKeyHeader(name="X-API-Key")

async def require_api_key(key: str = Security(api_key_header)):
    if key != settings.api_key:
        raise HTTPException(status_code=403)
```

Add `api_key: str` to `Settings`, sourced from `.env`.

#### 2.2 Rate limiting

```bash
uv add slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, req: ChatRequest, ...):
```

#### 2.3 Security headers middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline'"
        )
        return resp
```

#### 2.4 Prompt injection guard

```python
import re

_INJECTION = re.compile(
    r"(?i)(ignore|forget|override|disregard).{0,30}(system|prompt|instruction)"
    r"|(?i)(act as|pretend you are|you are now)"
)

def is_injection_attempt(text: str) -> bool:
    return bool(_INJECTION.search(text))
```

Log and reject (or surface to the agent's context) on match. This is a heuristic
guard, not a complete defence — combine with Anthropic's built-in guardrails in Wave 4.

#### 2.5 Pin dependency versions

```toml
"fastapi>=0.115.0,<1.0.0",
"uvicorn[standard]>=0.34.0,<1.0.0",
"strands-agents>=1.0.0,<2.0.0",
```

#### 2.6 Environment-aware CORS origins

```python
allowed_origins: list[str] = ["http://localhost:8000"]
```

Read from `ALLOWED_ORIGINS` (comma-separated) in production `.env`.

**Wave 2 success metrics:**
- Unauthenticated `/chat` returns 403
- Rate-limited client receives 429 after threshold
- Security headers present on all responses (`curl -I localhost:8000/health`)
- `pip-audit` returns zero critical CVEs

---

### Wave 3 — Observability and Reliability
**Effort:** ~10 hours | **Value:** Required for any operational visibility

#### 3.1 Structured logging

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
)
```

Log every request: method, path, status code, latency, first 100 chars of input.

#### 3.2 Enable Strands OpenTelemetry tracing

Add to `.env`:
```
STRANDS_OTEL_ENABLED=true
STRANDS_OTEL_ENDPOINT=http://localhost:4317
```

Zero code change — Strands emits per-tool latency and token counts automatically
when this variable is set.

#### 3.3 Prometheus metrics endpoint

```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

REQUESTS = Counter("chat_requests_total", "Total requests", ["status"])
LATENCY = Histogram("chat_duration_seconds", "Request latency")

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

#### 3.4 Agent retry strategy

```python
from strands import ModelRetryStrategy

agent = Agent(
    ...
    retry_strategy=ModelRetryStrategy(max_retries=3),
)
```

Handles transient Bedrock / Anthropic API failures transparently.

#### 3.5 Graceful shutdown via lifespan

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup complete")
    yield
    logger.info("shutdown initiated")

app = FastAPI(lifespan=lifespan)
```

**Wave 3 success metrics:**
- `GET /metrics` returns Prometheus counters and histograms
- Every `/chat` request produces a structured JSON log line with latency
- Agent retries visible in logs on transient errors
- OTEL spans visible in trace backend for per-tool latency

---

### Wave 4 — Core Functionality and Cost Optimisation
**Effort:** ~18 hours | **Value:** The agent's value proposition actually works

This is the most business-critical wave: replacing the stub tool implementations
with real LLM calls. It is intentionally deferred until Waves 1–3 are complete
because real LLM calls incur cost and require observability to detect problems.

#### 4.1 Implement `evaluate_prompt` with Anthropic SDK + prompt caching

```python
import anthropic, json

_client = anthropic.Anthropic()
_RUBRIC_SYSTEM = """You are a prompt quality evaluator. Score the given prompt on each of
these nine dimensions from 1 (poor) to 5 (excellent): relevance, accuracy, fluency,
coherence, completeness, safety, groundedness, instruction_following, verbosity.
Return ONLY a JSON object with those nine keys and integer values."""

@tool
def evaluate_prompt(prompt: str) -> dict:
    """Evaluate a prompt using ReFlect rubrics across nine quality dimensions."""
    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=[{
            "type": "text",
            "text": _RUBRIC_SYSTEM,
            "cache_control": {"type": "ephemeral"},  # cache the static rubric
        }],
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(response.content[0].text)
```

Use `claude-haiku-4-5-20251001` for this tool — it is faster and significantly cheaper
than Sonnet for structured extraction tasks with a fixed schema.

#### 4.2 Implement `generate_prompt_template` with Anthropic SDK

```python
@tool
def generate_prompt_template(task: str, context: str = "", style: str = "zero-shot") -> str:
    """Generate a ReFlect-structured prompt template for a given task."""
    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content":
            f"Generate a {style} prompt template for: {task}\n"
            f"Context: {context}\n"
            "Use the ReFlect framework: Role, Format, Language, Example, Context, Task."
        }],
    )
    return response.content[0].text
```

#### 4.3 Explicit model + system prompt caching on the main agent

```python
from strands.models.anthropic import AnthropicModel

_model = AnthropicModel(
    model_id="claude-sonnet-4-6",
    cache_prompt=True,   # caches system_prompt.md — saves ~40% on repeated turns
)

agent = Agent(model=_model, system_prompt=_system_prompt, ...)
```

**Cost impact:** `system_prompt.md` is ~700 tokens. Without caching, a 5-turn
conversation re-bills those tokens 5 times. With caching, only the first turn pays
full price. At 1,000 conversations/day × 5 turns, this saves ~3.5 M input tokens/day.

#### 4.4 Add streaming to the webchat

```python
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def generate():
        async for chunk in agent.stream_async(req.message):
            if "data" in chunk:
                yield f"data: {chunk['data']}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

Update the frontend to consume SSE instead of waiting for the full response.

#### 4.5 Token usage logging

```python
result = agent(req.message)
if hasattr(result, "metrics"):
    logger.info("token_usage", extra={
        "input_tokens": result.metrics.get("inputTokens"),
        "output_tokens": result.metrics.get("outputTokens"),
    })
```

**Wave 4 success metrics:**
- `evaluate_prompt("test prompt")` returns actual integer scores, not `"TBD"`
- System prompt cache hit rate ≥ 80% (visible in Anthropic usage dashboard)
- Average `/chat` P95 latency < 5 s; streaming first-token < 500 ms
- Cost per 1,000 conversations tracked in structured logs

---

### Wave 5 — Maintainability, Portability, and CI/CD
**Effort:** ~15 hours | **Value:** Enables safe team development and deployment

#### 5.1 Test suite

```
tests/
  test_tools.py      # Unit tests for all three @tool functions
  test_skills.py     # Verify all 5 SKILL.md files load via Skill.from_directory()
  test_webchat.py    # FastAPI TestClient: /health, /chat, /metrics, auth, rate limiting
  test_config.py     # Settings validation with and without .env
```

Target: 80% line coverage on `agent/` and `ui/`.

#### 5.2 GitHub Actions CI pipeline

`.github/workflows/ci.yml`:
```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.13' }
      - run: pip install uv && uv pip install --system -e ".[dev]"
      - run: ruff check . && ruff format --check .
      - run: mypy .
      - run: pytest --cov=agent --cov=ui --cov-fail-under=80
      - run: pip-audit   # dependency vulnerability scan
```

#### 5.3 Dockerfile + docker-compose

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv pip install --no-cache-dir --system -e .
COPY . .
EXPOSE 8000
CMD ["uvicorn", "ui.webchat:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

```yaml
# docker-compose.yml
services:
  agent:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      retries: 3
```

#### 5.4 Fix `sys.path` manipulation in `webchat.py`

Remove the `sys.path.append(...)` lines. Since the project is installed as a package
via `pip install -e .`, `from agent import agent` works without path hacks.

#### 5.5 Clean up `.env.example`

Strip it to only the variables the code actually reads. Annotate each as required vs.
optional. Add a pre-commit hook (`detect-secrets`) to prevent accidental `.env` commits.

**Wave 5 success metrics:**
- `pytest --cov` reports ≥ 80% coverage on `agent/` and `ui/`
- CI pipeline passes on every push to `main`
- `docker compose up` starts the service with zero manual steps
- New developer can go from `git clone` to running service in < 5 minutes

---

## Wave Dependencies

```
Wave 1 — Critical Fixes (unblocks safe operation)
  └── Wave 2 — Security Hardening (auth requires clean error handling from W1)
        └── Wave 3 — Observability (metrics/logging builds on secured endpoints)
              └── Wave 4 — Core Functionality (real LLM calls require observability to track cost)
                    └── Wave 5 — CI/CD (tests require real tools to have meaningful assertions)
```

Wave 5 scaffold (test files, CI config, Dockerfile) can begin in parallel with Wave 4
before real tool implementations are complete.

---

## Follow-up Metrics

| Metric | Baseline | After W1 | After W3 | After W4 | After W5 |
|--------|----------|----------|----------|----------|----------|
| `pip-audit` critical CVEs | Unknown | 0 | 0 | 0 | 0 (CI-gated) |
| Unauthenticated `/chat` blocked | 0% | — | 100% (W2) | 100% | 100% |
| Test line coverage | 0% | 0% | 0% | 0% | ≥ 80% |
| `/health` endpoint present | No | Yes | Yes | Yes | Yes |
| `evaluate_prompt` returns real scores | Never | Never | Never | Always | Regression-tested |
| System prompt cache hit rate | 0% | 0% | 0% | ≥ 80% | Tracked in logs |
| `/chat` P95 latency | Unknown | Unknown | Measured | < 5 s | Tracked |
| Time to first streaming token | N/A | N/A | N/A | < 500 ms | Tested |
| Cost per 1k conversations | Unknown | Unknown | Tracked | Tracked | Alerted |
| CI pass rate on `main` | N/A | N/A | N/A | N/A | ≥ 95% |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Strands SDK API breaks on minor update | Medium | High | Pin to minor version range; regression tests in Wave 5 |
| Bedrock default model lacks prompt caching | High | Medium | Switch to `AnthropicModel` in Wave 4 (already planned) |
| Prompt injection bypasses heuristic filter | Medium | High | Heuristic guard is not a complete defence — add Anthropic guardrails; log all flagged attempts |
| Real tools cause unexpected cost spike | Medium | High | Deploy Wave 3 observability first; set billing alerts before Wave 4 goes live |
| Port 8000 exposed externally before Wave 1 ships | Low (dev) → High (cloud) | Critical | Do not open firewall / security group on port 8000 until Wave 1 is complete |
| Single-worker uvicorn drops requests under load | Medium | Medium | Add `workers=2` in `main.py` as stop-gap; proper scaling deferred to post-Wave 5 |
| `.env` committed to git by accident | Low | High | Verify `.gitignore` covers `.env`; add `detect-secrets` pre-commit hook in Wave 5 |

---

## Conclusion

The ReFlect Prompting Agent has the right architectural bones: the Strands SDK composition model, a clean skills-as-files pattern, and a clear domain purpose. The gaps are almost entirely in the production-readiness layer — security, observability, and implementation completeness — rather than in fundamental design.

**The five-wave plan delivers:**
- A secure, observable, production-ready service by the end of Wave 3 (~32 hours)
- A fully functional agent with real tool implementations by Wave 4 (~50 hours)
- A maintainable, testable, containerised codebase by Wave 5 (~65 hours)

The recommended starting point is Wave 1 in its entirety — all eight items can be completed in a single focused session and eliminate the most acute risks without requiring new dependencies or architectural changes.
