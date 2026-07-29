---
description: Perform a severity-ranked, uncompromising static critique of active code.
argument-hint: target files or directories
---

# Grill Code

Suspend feature generation. Treat the text following `/grill` as target paths;
when it is empty, use the active file or current diff.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/code-griller/SKILL.md`.
2. Collect only relevant code, tests, public interfaces, and diff context.
3. Run the sibling skill's `grill.py` against the resolved targets.
4. Verify high-severity findings against source before reporting them.
5. Rank findings by correctness, memory or resource safety, security,
   scalability, architecture, and test risk.

Return no praise and no style trivia. For every finding provide severity,
`path:line`, failure mode, impact, and the smallest durable correction. End with
the top three fixes and a ship or block verdict. Do not modify code unless the
user also requests fixes.
