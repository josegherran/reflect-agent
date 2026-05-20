from strands_agents.agent import Agent
from agent.skills import PromptEvaluationSkill, PromptTemplateSkill
from agent.tools import PromptRubricTool

class ReflectPromptingAgent(Agent):
    """
    Agent to guide users in creating, evaluating, and improving AI prompts using the Gartner ReFlect framework and advanced prompt engineering techniques.
    """
    def __init__(self):
        super().__init__(
            name="ReFlectPromptingAgent",
            description="Guides users in prompt engineering using the ReFlect framework.",
            skills=[PromptEvaluationSkill(), PromptTemplateSkill()],
            tools=[PromptRubricTool()]
        )

agent = ReflectPromptingAgent()
