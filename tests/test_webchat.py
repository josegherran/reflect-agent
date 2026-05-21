"""Integration tests for the FastAPI webchat endpoints."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_agent_result() -> MagicMock:
    """Minimal AgentResult-like object returned by agent(message)."""
    result = MagicMock()
    result.configure_mock(
        **{"__str__": lambda self: "The ReFlect framework stands for Role, Format, Language..."}
    )
    metrics = MagicMock()
    metrics.accumulated_usage = {"inputTokens": 100, "outputTokens": 50}
    result.metrics = metrics
    return result


@pytest.fixture()
def client(mock_agent_result: MagicMock) -> Generator[TestClient, None, None]:
    """TestClient with agent calls monkeypatched to avoid real LLM calls."""
    import ui.webchat as webchat_module

    with patch.object(webchat_module, "agent") as mock_agent:
        mock_agent.return_value = mock_agent_result
        mock_agent.event_loop_metrics = mock_agent_result.metrics

        async def fake_stream(*args: object, **kwargs: object) -> object:
            yield {"data": "The ReFlect "}
            yield {"data": "framework."}

        mock_agent.stream_async = fake_stream
        with TestClient(webchat_module.app) as c:
            yield c


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_returns_200(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.status_code == 200

    def test_returns_status_ok(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /metrics
# ---------------------------------------------------------------------------


class TestMetrics:
    def test_returns_200(self, client: TestClient) -> None:
        r = client.get("/metrics")
        assert r.status_code == 200

    def test_contains_chat_requests_total(self, client: TestClient) -> None:
        r = client.get("/metrics")
        assert "chat_requests_total" in r.text

    def test_contains_chat_duration_seconds(self, client: TestClient) -> None:
        r = client.get("/metrics")
        assert "chat_duration_seconds" in r.text

    def test_contains_chat_tokens_total(self, client: TestClient) -> None:
        r = client.get("/metrics")
        assert "chat_tokens_total" in r.text


# ---------------------------------------------------------------------------
# / (HTML index)
# ---------------------------------------------------------------------------


class TestIndex:
    def test_returns_200(self, client: TestClient) -> None:
        r = client.get("/")
        assert r.status_code == 200

    def test_returns_html(self, client: TestClient) -> None:
        r = client.get("/")
        assert "text/html" in r.headers["content-type"]

    def test_contains_webchat_title(self, client: TestClient) -> None:
        r = client.get("/")
        assert "ReFlect" in r.text


# ---------------------------------------------------------------------------
# POST /chat — validation
# ---------------------------------------------------------------------------


class TestChatValidation:
    def test_missing_message_returns_422(self, client: TestClient) -> None:
        r = client.post("/chat", json={})
        assert r.status_code == 422

    def test_empty_message_returns_422(self, client: TestClient) -> None:
        r = client.post("/chat", json={"message": ""})
        assert r.status_code == 422

    def test_oversized_message_returns_422(self, client: TestClient) -> None:
        r = client.post("/chat", json={"message": "x" * 5001})
        assert r.status_code == 422

    def test_max_length_message_is_accepted(self, client: TestClient) -> None:
        r = client.post("/chat", json={"message": "x" * 5000})
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# POST /chat — happy path
# ---------------------------------------------------------------------------


class TestChatSuccess:
    def test_returns_200(self, client: TestClient) -> None:
        r = client.post("/chat", json={"message": "What is ReFlect?"})
        assert r.status_code == 200

    def test_returns_reply_key(self, client: TestClient) -> None:
        r = client.post("/chat", json={"message": "What is ReFlect?"})
        assert "reply" in r.json()

    def test_reply_is_string(self, client: TestClient) -> None:
        r = client.post("/chat", json={"message": "What is ReFlect?"})
        assert isinstance(r.json()["reply"], str)


# ---------------------------------------------------------------------------
# POST /chat — error path
# ---------------------------------------------------------------------------


class TestChatError:
    def test_agent_exception_returns_503(self, client: TestClient) -> None:
        import ui.webchat as webchat_module

        with patch.object(webchat_module, "agent", side_effect=RuntimeError("boom")):
            r = client.post("/chat", json={"message": "hello"})
        assert r.status_code == 503

    def test_agent_exception_returns_error_key(self, client: TestClient) -> None:
        import ui.webchat as webchat_module

        with patch.object(webchat_module, "agent", side_effect=RuntimeError("boom")):
            r = client.post("/chat", json={"message": "hello"})
        assert "error" in r.json()


# ---------------------------------------------------------------------------
# POST /chat/stream
# ---------------------------------------------------------------------------


class TestChatStream:
    def test_missing_message_returns_422(self, client: TestClient) -> None:
        r = client.post("/chat/stream", json={})
        assert r.status_code == 422

    def test_returns_200_for_valid_message(self, client: TestClient) -> None:
        r = client.post("/chat/stream", json={"message": "hello"})
        assert r.status_code == 200

    def test_response_is_text_event_stream(self, client: TestClient) -> None:
        r = client.post("/chat/stream", json={"message": "hello"})
        assert "text/event-stream" in r.headers["content-type"]

    def test_response_contains_data_lines(self, client: TestClient) -> None:
        r = client.post("/chat/stream", json={"message": "hello"})
        lines = [ln for ln in r.text.splitlines() if ln.startswith("data: ")]
        assert len(lines) >= 1

    def test_response_terminates_with_done(self, client: TestClient) -> None:
        r = client.post("/chat/stream", json={"message": "hello"})
        assert "data: [DONE]" in r.text

    def test_response_text_content_present(self, client: TestClient) -> None:
        r = client.post("/chat/stream", json={"message": "hello"})
        data_lines = [
            ln[6:] for ln in r.text.splitlines() if ln.startswith("data: ") and ln != "data: [DONE]"
        ]
        content = "".join(data_lines)
        assert len(content) > 0
