---
description: Trace sensitive-data lifecycles and identify concrete privacy risks and controls.
argument-hint: feature, data fields, users, flows, processors, retention, and deletion
---

# Review Privacy

Preserve all text following `/privacy` as task input. When empty, use the active
feature and ask which personal data it handles.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/privacy-review/SKILL.md`.
2. Inspect collection, purpose, transformations, stores, logs, recipients,
   access, retention, backups, exports, deletion, and user controls.
3. Follow the skill's lifecycle review, decision boundaries, quality gates, and
   output contract.
4. Keep review read-only unless controls are explicitly requested; do not expose
   real personal data or claim legal compliance.

Return a concise data-flow inventory, ranked gaps, technical controls, and open
policy questions. Separate repository evidence from policy assumptions and
never fabricate deletion or consent behavior.
