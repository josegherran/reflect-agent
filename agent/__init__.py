from pathlib import Path

from strands import Agent, AgentSkills, ModelRetryStrategy
from strands.models.anthropic import AnthropicModel

from agent.skills import evaluate_prompt, generate_prompt_template
from agent.tools import prompt_rubric_tool

_skills_dir = Path(__file__).parent.parent / "skills"
_skills_plugin = AgentSkills(skills=[str(_skills_dir)])
_system_prompt_text = (Path(__file__).parent / "system_prompt.md").read_text()

# Pass system prompt as a structured block with cache_control so Anthropic caches
# the ~700-token system prompt across repeated turns (saves ~40% on input tokens).
_model = AnthropicModel(
    model_id="claude-sonnet-4-6",
    max_tokens=4096,
    params={
        "system": [
            {
                "type": "text",
                "text": _system_prompt_text,
                "cache_control": {"type": "ephemeral"},
            }
        ]
    },
)

agent = Agent(
    model=_model,
    name="ReFlectPromptingAgent",
    description="Guides users in prompt engineering using the ReFlect framework.",
    tools=[evaluate_prompt, generate_prompt_template, prompt_rubric_tool],
    plugins=[_skills_plugin],
    system_prompt=_system_prompt_text,
    retry_strategy=ModelRetryStrategy(max_attempts=3),
)
