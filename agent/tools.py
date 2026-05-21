from strands import tool


@tool
def prompt_rubric_tool(prompt: str) -> dict[str, list[str]]:
    """
    Provide rubrics and metrics for evaluating prompt effectiveness.

    Args:
        prompt: The prompt text to evaluate.

    Returns:
        A dict containing the rubric categories applicable to the prompt.
    """
    # Placeholder: Add rubric logic here
    return {
        "rubrics": [
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
    }
