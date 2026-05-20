---
name: prompt-evaluation
description: Step-by-step instructions for scoring a prompt across nine quality dimensions using the evaluate_prompt tool.
---

# Prompt Evaluation

Use this skill whenever a user asks to evaluate, score, or critique a prompt.

## Evaluation Process

1. Ask the user to share the prompt they want evaluated (if not already provided).
2. Call the `evaluate_prompt` tool with the prompt text.
3. For each dimension in the result, provide a brief qualitative explanation alongside the score.
4. Summarise the two or three weakest dimensions and offer concrete rewrites.

## The Nine Dimensions

| Dimension | What to assess |
|-----------|---------------|
| **Relevance** | Does the prompt stay on topic and avoid unnecessary content? |
| **Accuracy** | Are facts, instructions, or constraints stated correctly? |
| **Fluency** | Is the prompt grammatically correct and easy to read? |
| **Coherence** | Do the parts of the prompt fit together logically? |
| **Completeness** | Does the prompt include all information needed to respond well? |
| **Safety** | Does the prompt avoid eliciting harmful, biased, or misleading output? |
| **Groundedness** | Are claims and context anchored to verifiable or provided information? |
| **Instruction Following** | Are the instructions clear enough that an AI could follow them precisely? |
| **Verbosity** | Is the prompt appropriately concise — neither too sparse nor too padded? |

## Scoring Guide

When providing scores, use a 1–5 scale:
- **5** — Excellent, no improvements needed
- **4** — Good, minor tweaks would help
- **3** — Adequate, notable gaps present
- **2** — Weak, significant revision needed
- **1** — Poor, fundamental rework required

## Output Format

Present evaluations as a table followed by a "Top improvements" section with specific, actionable rewrites.
