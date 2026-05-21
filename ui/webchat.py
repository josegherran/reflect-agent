import json
import logging
import os
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent import agent
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

REQUESTS = Counter("chat_requests_total", "Total /chat requests", ["status", "endpoint"])
LATENCY = Histogram("chat_duration_seconds", "End-to-end /chat latency in seconds", ["endpoint"])
TOKEN_COUNTER = Counter("chat_tokens_total", "Tokens billed across all /chat calls", ["type"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup complete")
    yield
    logger.info("shutdown initiated")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "allowed_origins", ["http://localhost:8000"]),
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    latency = time.monotonic() - start
    logger.info(
        '{"method":"%s","path":"%s","status":%d,"latency_s":%.3f}',
        request.method,
        request.url.path,
        response.status_code,
        latency,
    )
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
    <head><title>ReFlect Agent Webchat</title></head>
    <body>
        <h2>ReFlect Agent Webchat</h2>
        <div id='chat' style='height:400px;overflow:auto;border:1px solid #ccc;padding:10px;'></div>
        <input id='msg' style='width:80%' placeholder='Type your message...'/>
        <button onclick='sendMsg()'>Send</button>
        <script>
        let chat = document.getElementById('chat');

        function appendLabel(tag, text) {
            let el = document.createElement(tag);
            el.textContent = text;
            return el;
        }

        function sendMsg() {
            let msg = document.getElementById('msg').value.trim();
            if (!msg) return;
            document.getElementById('msg').value = '';

            let userDiv = document.createElement('div');
            userDiv.appendChild(appendLabel('b', 'You: '));
            let userSpan = document.createElement('span');
            userSpan.textContent = msg;
            userDiv.appendChild(userSpan);
            chat.appendChild(userDiv);

            let agentDiv = document.createElement('div');
            agentDiv.appendChild(appendLabel('b', 'Agent: '));
            let agentSpan = document.createElement('span');
            agentDiv.appendChild(agentSpan);
            chat.appendChild(agentDiv);

            fetch('/chat/stream', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            }).then(response => {
                let reader = response.body.getReader();
                let decoder = new TextDecoder();
                let buffer = '';
                function pump() {
                    return reader.read().then(({done, value}) => {
                        if (done) return;
                        buffer += decoder.decode(value, {stream: true});
                        let lines = buffer.split('\\n');
                        buffer = lines.pop();
                        lines.forEach(line => {
                            if (line.startsWith('data: ')) {
                                let chunk = line.slice(6);
                                if (chunk !== '[DONE]') {
                                    agentSpan.textContent += chunk;
                                    chat.scrollTop = chat.scrollHeight;
                                }
                            }
                        });
                        return pump();
                    });
                }
                return pump();
            }).catch(() => {
                agentSpan.textContent = '[error — see server logs]';
            });
        }

        document.getElementById('msg').addEventListener('keydown', e => {
            if (e.key === 'Enter') sendMsg();
        });
        </script>
    </body>
    </html>
    """


@app.post("/chat")
async def chat(req: ChatRequest):
    """Non-streaming JSON endpoint for API clients."""
    t0 = time.monotonic()
    try:
        result = agent(req.message)
        elapsed = time.monotonic() - t0
        REQUESTS.labels(status="success", endpoint="sync").inc()
        LATENCY.labels(endpoint="sync").observe(elapsed)
        _log_token_usage(result)
        logger.info(
            '{"event":"chat","input_preview":"%s","latency_s":%.3f}',
            req.message[:100].replace('"', '\\"'),
            elapsed,
        )
        return JSONResponse({"reply": str(result)})
    except Exception:
        elapsed = time.monotonic() - t0
        REQUESTS.labels(status="error", endpoint="sync").inc()
        LATENCY.labels(endpoint="sync").observe(elapsed)
        logger.exception("Agent call failed")
        return JSONResponse({"error": "Service unavailable"}, status_code=503)


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """Streaming SSE endpoint — yields text chunks as they arrive from the model."""

    async def generate():
        t0 = time.monotonic()
        try:
            async for event in agent.stream_async(req.message):
                if "data" in event:
                    chunk = event["data"]
                    if chunk:
                        yield f"data: {chunk}\n\n"
            elapsed = time.monotonic() - t0
            REQUESTS.labels(status="success", endpoint="stream").inc()
            LATENCY.labels(endpoint="stream").observe(elapsed)
            _log_token_usage_from_metrics(elapsed)
            yield "data: [DONE]\n\n"
        except Exception:
            elapsed = time.monotonic() - t0
            REQUESTS.labels(status="error", endpoint="stream").inc()
            LATENCY.labels(endpoint="stream").observe(elapsed)
            logger.exception("Streaming agent call failed")
            yield f"data: {json.dumps({'error': 'Service unavailable'})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


def _log_token_usage(result: object) -> None:
    """Log and count token usage from a synchronous AgentResult."""
    try:
        metrics = getattr(result, "metrics", None)
        if metrics is None:
            return
        usage = getattr(metrics, "accumulated_usage", {})
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)
        if input_tokens or output_tokens:
            TOKEN_COUNTER.labels(type="input").inc(input_tokens)
            TOKEN_COUNTER.labels(type="output").inc(output_tokens)
            logger.info(
                '{"event":"token_usage","input_tokens":%d,"output_tokens":%d}',
                input_tokens,
                output_tokens,
            )
    except Exception:
        pass


def _log_token_usage_from_metrics(elapsed: float) -> None:
    """Log token usage from the agent's event_loop_metrics after a streaming call."""
    try:
        metrics = agent.event_loop_metrics
        usage = getattr(metrics, "accumulated_usage", {})
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)
        if input_tokens or output_tokens:
            TOKEN_COUNTER.labels(type="input").inc(input_tokens)
            TOKEN_COUNTER.labels(type="output").inc(output_tokens)
            logger.info(
                '{"event":"token_usage","endpoint":"stream","input_tokens":%d,'
                '"output_tokens":%d,"latency_s":%.3f}',
                input_tokens,
                output_tokens,
                elapsed,
            )
    except Exception:
        pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
