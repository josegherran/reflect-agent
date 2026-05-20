from pathlib import Path
from strands import Agent, AgentSkills
from agent.skills import evaluate_prompt, generate_prompt_template
from agent.tools import prompt_rubric_tool

_skills_dir = Path(__file__).parent.parent / "skills"
_skills_plugin = AgentSkills(skills=[str(_skills_dir)])
_system_prompt = (Path(__file__).parent / "system_prompt.md").read_text()

agent = Agent(
    name="ReFlectPromptingAgent",
    description="Guides users in prompt engineering using the ReFlect framework.",
    tools=[evaluate_prompt, generate_prompt_template, prompt_rubric_tool],
    plugins=[_skills_plugin],
    system_prompt=_system_prompt,
)
