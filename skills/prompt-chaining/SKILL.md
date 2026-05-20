---
name: prompt-chaining
description: Protocol for decomposing complex tasks into a sequence of linked prompts, passing output from each step as context to the next.
---

# Prompt Chaining

Use this skill when the user's task is too complex for a single prompt, involves multiple distinct stages, or requires output from one step to inform the next.

## When to Chain

- The task has clearly separable stages (e.g. research → outline → draft → review).
- A single prompt would exceed the model's context window.
- Different steps require different roles or formats (e.g. analyst → editor → summariser).
- You need to validate or transform intermediate output before proceeding.

## Chain Design Protocol

### 1 — Decompose the task
Break the goal into a sequence of atomic steps. Each step should:
- Have a single, clear output
- Be completable independently given only its inputs
- Produce output that can be passed as-is to the next step

### 2 — Define handoffs
For each step, specify:
- **Input:** what it receives (user data, prior step output, external context)
- **Output:** what it produces and in what format
- **Validation:** what makes the output acceptable before passing it on

### 3 — Write the chain

**Template per step:**
```
[Role/context for this step]

Input:
[paste prior step output or raw data here]

Task:
[specific instruction for this step]

Output format:
[exact format required — this becomes the next step's input]
```

### 4 — Handle errors in the chain
If a step produces unexpected output:
- Do not silently pass bad output downstream.
- Return to that step with a correction prompt: "The previous output was [issue]. Revise it to [requirement]."

## Example: Blog Post Pipeline

```
Step 1 — Research
Role: You are a research assistant.
Task: List 5 key facts about [topic] with source types (no URLs needed).
Output: Numbered list of facts.

Step 2 — Outline  
Input: [Step 1 output]
Task: Create a 5-section blog outline using these facts. Each section gets one fact.
Output: Numbered outline with one-sentence section summaries.

Step 3 — Draft
Input: [Step 2 output]
Task: Write a 400-word blog post following this outline. Tone: conversational.
Output: Full draft.

Step 4 — Review
Input: [Step 3 output]
Task: Identify any factual gaps, unclear sentences, or tone inconsistencies. 
Output: Bullet list of issues with suggested fixes.
```

## Tips

- **Keep steps small** — a step that does two things is a bug waiting to happen.
- **Fix formats early** — if Step 1 outputs prose but Step 2 expects a list, define the list format in Step 1.
- **Name your chain steps** — label each block so the user can re-run a single step without rerunning the whole chain.
