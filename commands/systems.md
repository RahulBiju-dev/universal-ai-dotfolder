---
description: Design, implement, or review low-level software with explicit ownership and bounds.
argument-hint: C, C++, Rust, POSIX, IPC, binary, or resource-lifecycle task
---

# Engineer Systems Code

Preserve all text following `/systems` as task input. When empty, use the active
low-level target and stated objective.

Resolve the configuration root as the parent of this command file's directory.

1. Read its `skills/systems-programming/SKILL.md`.
2. Inspect platform contracts, ownership, pointer and size arithmetic, syscalls,
   partial I/O, concurrency, cleanup, ABI, tests, and complexity.
3. Follow the skill's implementation or review workflow, decision boundaries,
   safety gates, and output contract.
4. Mutate code only when implementation is requested; require approval for
   privileged, hardware-facing, or external execution.

Report ownership, failure behavior, complexity, changed interfaces, and
validation evidence concisely. Never claim sanitizer, platform, or runtime
results that did not run.
