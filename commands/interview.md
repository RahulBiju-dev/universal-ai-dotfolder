---
description: Run a calibrated mock technical interview with rubric-based feedback.
argument-hint: role level, topic, format, duration, and interview constraints
---

# Run Mock Interview

Preserve all text following `/interview` as task input. When empty, ask for role
level and topic before starting.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/interview-coach/SKILL.md`.
2. Inspect any supplied resume context, code, or target rubric without inventing
   employer-specific criteria.
3. Follow the skill's question cadence, progressive hints, decision boundaries,
   evaluation gates, and output contract.
4. Keep the session read-only and withhold full solutions until the configured
   feedback stage.

Return prompts one stage at a time, then concise evidence-based scoring and a
practice plan. Never fabricate timing, performance, or interviewer consensus.
