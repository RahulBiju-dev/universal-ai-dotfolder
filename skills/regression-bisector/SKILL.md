---
name: regression-bisector
description: Locate the first change that introduced a reproducible regression using a deterministic predicate and safe history traversal. Use for git bisect investigations, performance regressions, flaky introduction ranges, dependency history, or narrowing known-good and known-bad revisions.
---

# Regression Bisector

## Prove the Predicate

1. Record the exact symptom, environment, input, expected result, and failure threshold.
2. Verify the candidate bad revision fails and a defensible good revision passes using the same bounded command.
3. Repeat noisy predicates and define a deterministic classification rule.
4. Separate build failure, unavailable dependency, and untestable revision from good or bad.
5. Estimate the search cost as logarithmic revisions times predicate runtime.

## Protect the Workspace

- Inspect repository status and preserve every user change.
- Prefer a disposable worktree or clone for history traversal.
- Pin dependencies and keep generated artifacts revision-local.
- Avoid hooks, install scripts, network calls, and unfamiliar historical binaries unless explicitly approved.
- Define cleanup before starting and never reset or discard user data.

## Bisect and Confirm

- Traverse only the known-good to known-bad ancestry range.
- Automate the predicate with explicit exit semantics and bounded output.
- Mark genuinely untestable revisions as skipped and record why.
- Inspect the first bad change, its parents, adjacent revisions, and relevant dependency updates.
- Reproduce the transition on both sides after the search.
- Confirm causality with a focused revert, patch, or invariant analysis when safe.

## Teach the Method

- Explain binary search assumptions and how skipped or flaky revisions weaken certainty.
- Show the student why commit correlation is not yet root cause.
- Identify the smallest changed invariant that explains the observed transition.

## Safety Boundaries

- Never run destructive historical migrations, touch production state, or execute untrusted revisions without isolation and approval.
- Never use hard reset, force checkout, or cleanup that can erase user work.
- Do not name a culprit until the boundary and predicate have been rechecked.

## Output Contract

- Report good and bad bounds, predicate, environment, tested revisions, skips, and first bad revision.
- Distinguish confirmed cause, correlated change, uncertainty, and validation not performed.
