---
name: assumption-auditor
description: "Extract, classify, and challenge hidden assumptions in requirements, plans, designs, estimates, and technical claims. Use before implementation or approval when unknown scale, behavior, ownership, compatibility, environment, or validation could invalidate the proposed work."
---

# Assumption Auditor
Convert implicit beliefs into explicit, testable risks without replacing missing facts with guesses.

## Workflow
1. Inspect the supplied artifact and its cited code, tests, telemetry, specifications, or decisions.
2. Extract explicit assumptions and infer only assumptions required for the reasoning to hold.
3. Classify each item as confirmed, contradicted, unverified, or decision-required.
4. Trace the consequence if each assumption fails, including architecture and complexity impact.
5. Rank assumptions by likelihood, blast radius, reversibility, and validation cost.
6. Identify the cheapest decisive check, authoritative source, or focused question for each risk.
7. Re-evaluate conclusions after removing or reversing the highest-risk assumption.

## Decision Boundaries
- Use `prompt-upscaler` to structure raw requests; audit an existing claim or plan here.
- Use `architecture-decision` when an assumption is actually an unresolved design choice.
- Do not call conventions, examples, or a single observed run contractual evidence.
- Do not manufacture user intent, production scale, deadlines, or environmental guarantees.
- Ask only when the unresolved answer would materially change or block the work.

## Quality Gates
- Quote or point to the reasoning that depends on every reported assumption.
- Separate absence of evidence from evidence of absence.
- Include boundary scale, concurrency, failure, compatibility, and resource-lifetime assumptions.
- Avoid low-impact trivia that cannot change a decision or validation plan.
- Never mark an assumption confirmed without a cited source or executed check.

## Output Contract
- Lead with the assumptions capable of invalidating the result.
- Provide `Assumption`, `Status`, `Evidence`, `Failure impact`, and `Validation` columns.
- State which conclusions remain valid under uncertainty.
- List focused questions only for decision-critical unknowns.
- Distinguish inspected evidence, inference, and proposed verification.
