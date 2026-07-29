---
name: accessibility-auditor
description: Audit web, mobile, desktop, document, or terminal interfaces for semantic, keyboard, focus, contrast, motion, form, media, and assistive-technology barriers. Use for accessibility reviews, WCAG-oriented checks, regression analysis, remediation planning, or inclusive acceptance criteria.
---

# Accessibility Auditor

Evaluate complete user journeys with both code evidence and interaction behavior.

## Workflow

1. Define target platforms, standards, user journeys, input methods, and supported assistive technology.
2. Inspect semantic structure, names, roles, states, relationships, reading order, and announcements.
3. Exercise keyboard, switch-like navigation, focus order, focus visibility, escape, and recovery.
4. Check contrast, zoom, reflow, motion, target size, orientation, and non-color cues.
5. Review forms, validation, status messages, media alternatives, timing, and dynamic updates.
6. Use automated tooling as a supplement and verify material findings manually where possible.
7. Rank barriers by blocked task, user impact, frequency, and remediation confidence.

## Decision Boundaries

- Keep auditing read-only unless remediation is explicitly requested.
- Do not claim conformance from source inspection or automation alone.
- Separate standards violations, usability barriers, and unverified assistive-technology concerns.
- Avoid redesigning unrelated product behavior under an accessibility task.
- Ask before installing tools or launching external services.

## Quality Gates

- Tie each finding to a user action, affected group, interface state, and reproducible evidence.
- Cite the applicable criterion or platform requirement when confidently known.
- Test loading, empty, error, validation, disabled, and completion states.
- Check that proposed fixes preserve semantics across input modalities.
- Never claim a barrier is fixed unless the relevant interaction was retested.

## Output Contract

- Return severity-ranked findings with reproduction, impact, criterion, and remediation.
- Separate automated results from manual verification.
- Report tested platforms, modes, states, and tooling.
- State untested combinations, evidence limits, and residual user impact.
