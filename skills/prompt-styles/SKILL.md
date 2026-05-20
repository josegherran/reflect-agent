---
name: prompt-styles
description: Reference guide for zero-shot, few-shot, chain-of-thought, and prompt chaining styles with before/after examples for each.
---

# Prompt Styles

Use this skill when the user asks about prompt techniques, wants examples of a specific style, or needs help choosing the right approach for their task.

## Zero-Shot

No examples provided — the model relies entirely on its training knowledge.

**When to use:** Simple, well-understood tasks with a clear output shape.

**Example:**
```
Summarise the following article in three bullet points.

[article text]
```

---

## Few-Shot

One or more input/output examples precede the real request, teaching the model the expected pattern.

**When to use:** Tasks with a precise output format, domain-specific tone, or non-obvious structure.

**Example:**
```
Classify the sentiment of each sentence as Positive, Negative, or Neutral.

Sentence: "The product exceeded my expectations." → Positive
Sentence: "Delivery was two weeks late." → Negative
Sentence: "The package arrived on Tuesday." → Neutral

Sentence: "I can't believe how fast the support team responded." → 
```

**Tips:**
- Use 2–5 examples; more rarely helps and increases token cost.
- Examples should cover edge cases, not just the easy case.

---

## Chain-of-Thought (CoT)

Ask the model to reason step-by-step before giving its final answer. Dramatically improves accuracy on multi-step reasoning tasks.

**When to use:** Maths, logic, analysis, or any task where intermediate reasoning matters.

**Example:**
```
A store sells apples for $0.50 each and bags for $3.00. 
A customer buys 6 apples and 2 bags. How much do they spend in total?
Think through this step by step before giving your answer.
```

**Zero-shot CoT trigger phrases:**
- "Think step by step."
- "Let's reason through this."
- "Show your working."

---

## Prompt Chaining

Break a complex task into a sequence of linked prompts where the output of each step feeds into the next.

**When to use:** Long documents, multi-stage workflows, or tasks that exceed a single context window.

**Pattern:**
```
Step 1 prompt → output A
Step 2 prompt: "Given this output: [A], now do X..." → output B
Step 3 prompt: "Using [B], produce the final Y..."
```

**See the `prompt-chaining` skill for a full orchestration protocol.**
