import json
import re

import anthropic
from strands import tool

_client = anthropic.Anthropic()

_RUBRIC_DIMENSIONS = [
    "relevance",
    "accuracy",
    "fluency",
    "coherence",
    "completeness",
    "safety",
    "groundedness",
    "instruction_following",
    "verbosity",
]

_RUBRIC_SYSTEM = (
    "You are a prompt quality evaluator. Score the given prompt on each of these nine dimensions "
    "from 1 (poor) to 5 (excellent): "
    + ", ".join(_RUBRIC_DIMENSIONS)
    + ". Return ONLY a JSON object with those nine keys and integer values."
    " No prose, no markdown fences."
)

_TEMPLATE_SYSTEM = (
    "You are an expert prompt engineer. Generate a clear, modular prompt template using the"
    " ReFlect framework: Role, Format, Language, Example, Context, Task."
    " Return ONLY the prompt template text, no extra explanation."
)


@tool
def evaluate_prompt(prompt: str) -> dict[str, int | str]:
    """
    Evaluate a prompt using ReFlect rubrics across nine quality dimensions.

    Uses the Anthropic API to score the prompt on: relevance, accuracy, fluency,
    coherence, completeness, safety, groundedness, instruction_following, verbosity.
    Each dimension is scored 1 (poor) to 5 (excellent).

    Args:
        prompt: The prompt text to evaluate.

    Returns:
        A dict mapping each rubric dimension to its integer score (1-5).
    """
    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": _RUBRIC_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": prompt}],
    )
    first = response.content[0] if response.content else None
    raw = first.text if isinstance(first, anthropic.types.TextBlock) else "{}"
    # Strip markdown fences if the model wraps the JSON despite instructions
    raw = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()
    try:
        scores: dict[str, int | str] = json.loads(raw)
    except json.JSONDecodeError:
        scores = {dim: "parse_error" for dim in _RUBRIC_DIMENSIONS}
    return scores


@tool
def generate_prompt_template(task: str, context: str = "", style: str = "zero-shot") -> str:
    """
    Generate a ReFlect-structured prompt template for a given task.

    Supports prompt styles: zero-shot, few-shot, chain-of-thought, chaining.
    Uses the ReFlect framework: Role, Format, Language, Example, Context, Task.

    Args:
        task: The task the prompt should accomplish.
        context: Optional additional context or constraints for the template.
        style: Prompting style — one of zero-shot, few-shot, chain-of-thought, chaining.

    Returns:
        A ReFlect-structured prompt template string.
    """
    user_msg = (
        f"Generate a {style} prompt template for the following task:\n"
        f"Task: {task}\n"
        f"Context: {context}\n\n"
        "Structure your output using ReFlect sections: "
        "Role, Format, Language, Example, Context, Task."
    )
    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": _TEMPLATE_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    )
    first = response.content[0] if response.content else None
    return first.text if isinstance(first, anthropic.types.TextBlock) else f"Template for: {task}"
