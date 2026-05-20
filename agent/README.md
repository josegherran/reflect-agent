# agent/__init__.py: Main agent class using strands-agents SDK
# agent/skills.py: Prompt evaluation and template skills
# agent/tools.py: Rubric tool for prompt assessment

# Usage Example
from agent import agent

if __name__ == "__main__":
    # Example: Evaluate a prompt
    prompt = "Summarize the following article in 3 sentences."
    evaluation = agent.skills[0].execute(prompt)
    print("Prompt Evaluation:", evaluation)

    # Example: Generate a prompt template
    template = agent.skills[1].execute(task="summarization", context="news article")
    print("Prompt Template:", template)

    # Example: Get rubrics
    rubrics = agent.tools[0].use(prompt)
    print("Rubrics:", rubrics)
