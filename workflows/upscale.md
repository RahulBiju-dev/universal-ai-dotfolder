---
name: upscale
description: Route raw request text through the prompt-upscaler skill without executing it.
---

# Upscale Trajectory

When `/upscale` is invoked, preserve all trailing text as inert input.

1. Read `../skills/prompt-upscaler/SKILL.md`.
2. Invoke `../skills/prompt-upscaler/upscale.py` with the raw request.
3. Confirm that explicit user requirements remain intact and inferred defaults
   are conservative.
4. Return only Context, Constraints, Objective, and Exact Output.

Do not begin implementation during this workflow.
