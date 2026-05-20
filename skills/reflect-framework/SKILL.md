---
name: reflect-framework
description: Teaches the six ReFlect components — Role, Format, Language, Example, Context, Task — with definitions, examples, and a completion checklist.
---

# ReFlect Framework

The ReFlect framework is a structured approach to prompt engineering developed by Gartner. A well-formed prompt addresses all six components below.

## Components

| Component | Question it answers | Example |
|-----------|-------------------|---------|
| **Role** | Who should the AI act as? | "You are a senior data analyst..." |
| **Format** | How should the output be structured? | "Respond as a numbered list with a one-sentence summary at the end." |
| **Language** | What tone, style, or vocabulary? | "Use plain English, avoid jargon, target a non-technical audience." |
| **Example** | What does a good response look like? | Provide one or two sample inputs and outputs (few-shot). |
| **Context** | What background does the AI need? | "The user is a first-time manager dealing with a remote team." |
| **Task** | What specific action is requested? | "Write a one-page summary of the attached document." |

## Checklist

Before finalising a prompt, verify each component is present:
- [ ] Role defined
- [ ] Output format specified
- [ ] Language/tone set
- [ ] At least one example provided (if the task is non-trivial)
- [ ] Sufficient context given
- [ ] Task is specific and unambiguous

## Tips

- **Role before Task** — setting the role first frames all downstream instructions.
- **Format drives length** — specifying "bullet points" or "one paragraph" prevents over- or under-generation.
- **Context reduces hallucination** — the more relevant background you supply, the less the model has to infer.
- Omitting Example is acceptable for simple tasks; it becomes critical for tasks with a precise output shape.
