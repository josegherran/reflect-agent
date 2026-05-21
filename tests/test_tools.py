"""Unit tests for @tool-decorated functions in agent/skills.py and agent/tools.py."""

import json
from unittest.mock import MagicMock, patch

import anthropic
import pytest

import agent.skills as skills_module
from agent.skills import evaluate_prompt, generate_prompt_template
from agent.tools import prompt_rubric_tool


def _make_text_response(text: str) -> MagicMock:
    """Build a minimal Anthropic Message mock whose content[0] is a TextBlock."""
    block = MagicMock(spec=anthropic.types.TextBlock)
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


# ---------------------------------------------------------------------------
# evaluate_prompt
# ---------------------------------------------------------------------------


class TestEvaluatePrompt:
    def test_returns_nine_dimension_scores(self) -> None:
        scores = {
            "relevance": 4,
            "accuracy": 5,
            "fluency": 3,
            "coherence": 4,
            "completeness": 3,
            "safety": 5,
            "groundedness": 4,
            "instruction_following": 5,
            "verbosity": 3,
        }
        mock_resp = _make_text_response(json.dumps(scores))
        with patch.object(skills_module._client.messages, "create", return_value=mock_resp):
            result = evaluate_prompt("Write a haiku about Python.")
        assert set(result.keys()) == set(skills_module._RUBRIC_DIMENSIONS)
        assert result["relevance"] == 4

    def test_strips_markdown_fences(self) -> None:
        scores = {dim: 3 for dim in skills_module._RUBRIC_DIMENSIONS}
        fenced = f"```json\n{json.dumps(scores)}\n```"
        mock_resp = _make_text_response(fenced)
        with patch.object(skills_module._client.messages, "create", return_value=mock_resp):
            result = evaluate_prompt("test prompt")
        assert all(v == 3 for v in result.values())

    def test_json_parse_error_returns_parse_error_values(self) -> None:
        mock_resp = _make_text_response("This is not JSON at all.")
        with patch.object(skills_module._client.messages, "create", return_value=mock_resp):
            result = evaluate_prompt("bad prompt")
        assert all(v == "parse_error" for v in result.values())

    def test_empty_content_returns_parse_error(self) -> None:
        response = MagicMock()
        response.content = []
        with patch.object(skills_module._client.messages, "create", return_value=response):
            result = evaluate_prompt("empty")
        assert all(v == "parse_error" for v in result.values())

    def test_uses_haiku_model(self) -> None:
        mock_resp = _make_text_response(
            json.dumps({dim: 1 for dim in skills_module._RUBRIC_DIMENSIONS})
        )
        with patch.object(
            skills_module._client.messages, "create", return_value=mock_resp
        ) as mock_create:
            evaluate_prompt("prompt")
        assert mock_create.call_args.kwargs["model"] == "claude-haiku-4-5-20251001"

    def test_sends_cache_control_on_system_prompt(self) -> None:
        mock_resp = _make_text_response(
            json.dumps({dim: 1 for dim in skills_module._RUBRIC_DIMENSIONS})
        )
        with patch.object(
            skills_module._client.messages, "create", return_value=mock_resp
        ) as mock_create:
            evaluate_prompt("prompt")
        system = mock_create.call_args.kwargs["system"]
        assert system[0]["cache_control"] == {"type": "ephemeral"}


# ---------------------------------------------------------------------------
# generate_prompt_template
# ---------------------------------------------------------------------------


class TestGeneratePromptTemplate:
    def test_returns_string(self) -> None:
        mock_resp = _make_text_response("## Role\nYou are an expert...")
        with patch.object(skills_module._client.messages, "create", return_value=mock_resp):
            result = generate_prompt_template("summarise a document")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_fallback_on_empty_content(self) -> None:
        response = MagicMock()
        response.content = []
        with patch.object(skills_module._client.messages, "create", return_value=response):
            result = generate_prompt_template("my task")
        assert "my task" in result

    def test_style_parameter_forwarded(self) -> None:
        mock_resp = _make_text_response("template")
        with patch.object(
            skills_module._client.messages, "create", return_value=mock_resp
        ) as mock_create:
            generate_prompt_template("task", style="few-shot")
        user_content = mock_create.call_args.kwargs["messages"][0]["content"]
        assert "few-shot" in user_content

    def test_context_parameter_forwarded(self) -> None:
        mock_resp = _make_text_response("template")
        with patch.object(
            skills_module._client.messages, "create", return_value=mock_resp
        ) as mock_create:
            generate_prompt_template("task", context="B2B SaaS")
        user_content = mock_create.call_args.kwargs["messages"][0]["content"]
        assert "B2B SaaS" in user_content

    def test_sends_cache_control_on_system_prompt(self) -> None:
        mock_resp = _make_text_response("template")
        with patch.object(
            skills_module._client.messages, "create", return_value=mock_resp
        ) as mock_create:
            generate_prompt_template("task")
        system = mock_create.call_args.kwargs["system"]
        assert system[0]["cache_control"] == {"type": "ephemeral"}


# ---------------------------------------------------------------------------
# prompt_rubric_tool
# ---------------------------------------------------------------------------


class TestPromptRubricTool:
    def test_returns_rubrics_key(self) -> None:
        result = prompt_rubric_tool("any prompt")
        assert "rubrics" in result

    def test_rubrics_contains_nine_dimensions(self) -> None:
        result = prompt_rubric_tool("any prompt")
        assert len(result["rubrics"]) == 9

    @pytest.mark.parametrize(
        "dim",
        [
            "relevance",
            "accuracy",
            "fluency",
            "coherence",
            "completeness",
            "safety",
            "groundedness",
            "instruction_following",
            "verbosity",
        ],
    )
    def test_rubrics_contains_expected_dimension(self, dim: str) -> None:
        result = prompt_rubric_tool("any prompt")
        assert dim in result["rubrics"]
