---
name: architecture-decision
description: "Evaluate consequential software architecture choices and recommend one option from evidence and explicit quality attributes. Use when component boundaries, data flow, deployment shape, technology selection, or long-lived tradeoffs need a reversible, decision-ready analysis."
---

# Architecture Decision
Choose an architecture direction by making forces, evidence, and consequences explicit.

## Workflow
1. Inspect current architecture, constraints, affected consumers, and authoritative project evidence.
2. Define the decision question narrowly and list measurable quality attributes in priority order.
3. Establish hard constraints, reversible preferences, expected scale, and failure assumptions.
4. Compare at least two viable options plus the status quo when it is genuinely available.
5. Evaluate complexity, coupling, operability, security, performance, cost, and migration risk.
6. Recommend one option only when the evidence discriminates; otherwise identify the blocking experiment.
7. Define adoption stages, compatibility controls, rollback, and a review trigger.

## Decision Boundaries
- Use `adr-writer` to record an accepted decision; do not treat a recommendation as approval.
- Use `task-planner` after the direction is chosen and implementation sequencing is needed.
- Do not select technology from popularity, novelty, or unsupported benchmark claims.
- Do not invent traffic, budget, compliance, staffing, or platform constraints.
- Prefer reversible choices when evidence is weak and defer irreversible commitments.

## Quality Gates
- Tie every comparison criterion to an actual requirement or named assumption.
- Include operational and failure behavior, not only the happy-path component diagram.
- Expose hidden state, ownership, dependency direction, and cross-boundary data movement.
- Quantify time, space, latency, capacity, or cost only from stated models or measured evidence.
- Test the recommendation against one credible failure scenario and one future-change scenario.

## Output Contract
- State the decision question, drivers, constraints, and evidence sources.
- Provide a compact option matrix with benefits, liabilities, and disqualifiers.
- Give the recommendation, confidence, rejected alternatives, and decisive reasoning.
- List migration stages, rollback conditions, and unresolved risks.
- Mark the result as proposed, accepted, or blocked without fabricating consensus.
