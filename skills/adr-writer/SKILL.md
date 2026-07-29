---
name: adr-writer
description: "Record an accepted or proposed architecture decision as a concise Architecture Decision Record with context, options, consequences, and review triggers. Use when decision evidence already exists and must be preserved in a repository ADR format without reopening analysis or inventing consensus."
---

# ADR Writer
Turn decision evidence into a durable record that future maintainers can understand and revisit.

## Workflow
1. Inspect repository ADR conventions, numbering, status vocabulary, links, and ownership.
2. Gather the decision question, date if known, status, drivers, constraints, and evidence.
3. Capture materially considered options and the reason each was accepted or rejected.
4. State the decision in one testable sentence with scope and boundary conditions.
5. Record positive, negative, operational, security, compatibility, and migration consequences.
6. Add implementation notes only when they are part of the approved decision.
7. Define review triggers, supersession links, and unresolved follow-ups.

## Decision Boundaries
- Use `architecture-decision` when options still require evaluation or a recommendation.
- Do not fabricate approval, participants, dates, measurements, alternatives, or decision status.
- Do not rewrite historical rationale to match later outcomes.
- Preserve existing ADR identifiers and templates unless a format change is requested.
- Mark incomplete evidence explicitly rather than filling gaps with plausible prose.

## Quality Gates
- Keep the decision distinct from its implementation plan.
- Tie consequences to the chosen option and stated system forces.
- Include rejected alternatives only when evidence shows they were considered.
- Make status, scope, supersession, and review conditions unambiguous.
- Verify referenced paths, issues, metrics, and prior ADRs before citing them.

## Output Contract
- Provide `Title`, `Status`, `Context`, `Decision`, `Consequences`, and `Options considered`.
- Include evidence links, migration implications, and review triggers when available.
- State missing decision metadata in a short unresolved list.
- Report repository conventions preserved and checks performed.
- Distinguish recorded facts from proposed wording awaiting approval.
