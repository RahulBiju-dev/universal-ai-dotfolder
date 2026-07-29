---
name: code-review
description: Review diffs, patches, pull requests, commits, or active code for correctness, regressions, error handling, security, performance, compatibility, maintainability, and test adequacy. Use for pre-merge review, independent verification, risk-focused feedback, or severity-ranked findings.
---

# Code Review

Prioritize concrete defects and regression risk over narration or stylistic preference.

## Workflow

1. Establish the requested behavior, change scope, repository conventions, and acceptance criteria.
2. Inspect the complete diff plus relevant callers, callees, contracts, tests, and configuration.
3. Trace success, boundary, failure, cleanup, concurrency, and compatibility paths.
4. Check security boundaries, complexity, resource ownership, observability, and migration effects.
5. Validate suspected findings with targeted search, static evidence, or authorized checks.
6. Rank findings by severity, confidence, reachability, and user impact.
7. Re-read the diff for interactions between changes and omitted necessary updates.

## Decision Boundaries

- Keep review read-only unless the user explicitly requests fixes.
- Do not report style preferences as defects when code follows local conventions.
- Avoid reviewing only changed lines when surrounding contracts determine correctness.
- Separate verified defects, evidence-backed risks, and optional improvements.
- Use `skills/git-manager/git_sync.py` for bounded diff context, `skills/repo-search/search.py` for references, and `skills/code-griller/grill.py` only as a supplement.

## Quality Gates

- Tie every finding to a concrete location and failure scenario.
- Check whether existing tests would detect the reported regression.
- Avoid duplicate findings with the same root cause.
- Confirm suggested remediation does not violate another contract.
- Never claim tests pass, behavior is safe, or an issue reproduces unless checked.

## Output Contract

- Lead with findings ordered by severity; omit a findings section when none exist.
- Include location, scenario, impact, evidence, and concise remediation for each finding.
- Follow with open questions and residual risks only when material.
- Report reviewed scope, commands run, outcomes, and validation limits.
