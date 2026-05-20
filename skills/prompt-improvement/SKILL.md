---
name: prompt-improvement
description: Iterative feedback loop for improving a user's prompt — ask clarifying questions, identify weaknesses, suggest rewrites, re-evaluate.
---

# Prompt Improvement

Use this skill whenever the user asks to improve, refine, or rewrite a prompt.

## Protocol

### Step 1 — Receive the prompt
Ask the user to share the prompt they want improved if they haven't already.

### Step 2 — Ask targeted clarifying questions
Before rewriting, ask up to three focused questions to understand intent:
- What task should this prompt accomplish?
- Who is the intended audience of the AI's response?
- Are there format or length requirements?

Avoid asking all three if the prompt already makes the intent clear.

### Step 3 — Identify weaknesses
Review the prompt against the ReFlect components (see `reflect-framework` skill) and the nine evaluation dimensions (see `prompt-evaluation` skill). Note the two or three most impactful gaps.

### Step 4 — Propose a rewrite
Offer an improved version of the prompt. Structure your response as:

```
**Original:** [user's prompt]

**Issues identified:**
- [weakness 1]
- [weakness 2]

**Improved prompt:**
[rewritten prompt]

**What changed:**
- [brief explanation of each change]
```

### Step 5 — Invite iteration
Ask: "Does this rewrite capture what you need, or should we adjust [specific element]?"

Repeat from Step 3 until the user is satisfied.

## Guiding Principles

- Make the **fewest changes** needed to fix the identified weaknesses — don't rewrite for style alone.
- Preserve the user's voice and domain vocabulary.
- If a constraint is ambiguous, surface it rather than silently resolve it.
- A prompt that scores 4/5 across all dimensions is better than a 5 on three and a 2 on one.
