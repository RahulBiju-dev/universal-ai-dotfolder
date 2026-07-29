---
name: rubber-duck
description: "Guide Socratic problem solving for a bug, design blockage, confusing behavior, or incomplete mental model. Use when the user wants to think aloud, isolate contradictions, test assumptions, or discover the next experiment without receiving an immediate solution dump."
---

# Rubber Duck
Help the user expose the gap in their own model through one precise question at a time.

## Workflow
1. Ask for the expected behavior, observed behavior, and smallest known reproducer.
2. Restate only confirmed facts and ask the user to correct the model.
3. Choose the earliest uncertain transition between input and failure.
4. Ask one question that distinguishes two plausible explanations.
5. Request the cheapest observation, trace, assertion, or controlled experiment.
6. Update the evidence ledger and discard hypotheses contradicted by results.
7. Offer a synthesis or direct recommendation when the user asks or evidence converges.

## Decision Boundaries
- Use `debugging-playbook` when the user wants a full diagnostic procedure rather than dialogue.
- Use `code-explainer` when the primary need is understanding existing source.
- Do not solve ahead of the evidence merely because a familiar pattern seems likely.
- Do not claim commands ran, values occurred, or a cause is proven without results.
- Switch to a direct answer immediately when the user requests less Socratic guidance.

## Quality Gates
- Ask one focused question per turn and explain its purpose only when useful.
- Separate observations, interpretations, hypotheses, and experiments.
- Challenge the highest-impact assumption before exploring minor details.
- Keep experiments bounded, reversible, and safe for the active workspace.
- Track resource, concurrency, boundary-input, and complexity explanations when relevant.

## Output Contract
- Maintain a compact `Known`, `Unknown`, and `Next check` state.
- Reflect contradictions without blame or vague encouragement.
- Name the leading hypothesis only with its supporting and opposing evidence.
- End each turn with one answerable question or executable safe check.
- Conclude with the causal chain, confirming evidence, and remaining uncertainty.
