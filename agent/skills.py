from strands import Skill, tool


@tool
def evaluate_prompt(prompt: str) -> dict:
    """
    Evaluate a prompt using ReFlect rubrics: relevance, accuracy, fluency,
    coherence, completeness, safety, groundedness, instruction_following, verbosity.

    Args:
        prompt: The prompt text to evaluate.

    Returns:
        A dict of rubric dimension scores.
    """
    # Placeholder: Add evaluation logic here
    return {
        "relevance": "TBD",
        "accuracy": "TBD",
        "fluency": "TBD",
        "coherence": "TBD",
        "completeness": "TBD",
        "safety": "TBD",
        "groundedness": "TBD",
        "instruction_following": "TBD",
        "verbosity": "TBD",
    }


@tool
def generate_prompt_template(task: str, context: str = "") -> str:
    """
    Generate a modular prompt template for a given task and optional context,
    demonstrating styles such as zero-shot, few-shot, chain-of-thought, and chaining.

    Args:
        task: The task the prompt should accomplish.
        context: Optional additional context for the template.

    Returns:
        A prompt template string.
    """
    # Placeholder: Add template generation logic here
    return f"Prompt template for task: {task} with context: {context}"


