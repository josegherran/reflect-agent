from strands_agents.tool import Tool

class PromptRubricTool(Tool):
    """
    Tool to provide rubrics and metrics for evaluating prompt effectiveness.
    """
    def use(self, prompt: str):
        # Placeholder: Add rubric logic here
        return {
            "rubrics": [
                "relevance", "accuracy", "fluency", "coherence", "completeness",
                "safety", "groundedness", "instruction_following", "verbosity"
            ]
        }
