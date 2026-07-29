# Universal AI Dotfolder

A portable, bounded engineering toolkit for Cursor, Claude Code, and Google
Antigravity. It combines a strict workspace contract, reusable slash workflows,
an on-demand software-engineering persona registry, an always-on architecture
guard, and eight executable skills for systems, algorithm, and pipeline work.

## Native placement

This repository is the canonical payload. Copy only the artifacts a host
discovers after reviewing destination conflicts:

| Host | Project placement |
|---|---|
| Cursor | `agents/*.md` → `.cursor/agents/`, `commands/` → `.cursor/commands/`, `rules/` → `.cursor/rules/`, `skills/` → `.cursor/skills/` |
| Claude Code | `agents/*.md` → `.claude/agents/`, `commands/` → `.claude/commands/`, `skills/` → `.claude/skills/` |
| Antigravity | `agents/*.md` → `.agents/agents/`, `workflows/` → `.agents/workflows/`, `skills/` → `.agents/skills/` |

For machine-wide reuse, copy reviewed profiles to `~/.cursor/agents/`,
`~/.claude/agents/`, or `~/.gemini/config/agents/` respectively. Prefer
project placement when a persona encodes repository-specific constraints.

Keep `AGENTS.md` at the project root. Cursor and Antigravity load it as
workspace context. The included `CLAUDE.md` imports it for Claude Code, avoiding
a duplicated policy body.

## Layout

```text
AGENTS.md
CLAUDE.md
agents/
  accessibility-engineer.md
  ai-systems-engineer.md
  algorithm-engineer.md
  application-engineer.md
  backend-engineer.md
  build-release-engineer.md
  cloud-infrastructure-engineer.md
  code-reviewer.md
  compiler-toolchain-engineer.md
  contract-compatibility-engineer.md
  data-engineer.md
  database-storage-engineer.md
  debugging-investigator.md
  desktop-engineer.md
  developer-experience-engineer.md
  distributed-systems-engineer.md
  documentation-engineer.md
  embedded-firmware-engineer.md
  engineering-manager.md
  frontend-engineer.md
  full-stack-engineer.md
  game-engineer.md
  generalist-software-engineer.md
  graphics-realtime-engineer.md
  kernel-engineer.md
  machine-learning-engineer.md
  mlops-engineer.md
  mobile-engineer.md
  networking-protocol-engineer.md
  performance-engineer.md
  platform-devops-engineer.md
  principal-software-architect.md
  repository-maintainer.md
  research-engineer.md
  robotics-controls-engineer.md
  security-engineer.md
  site-reliability-engineer.md
  solutions-architect.md
  staff-software-engineer.md
  systems-programming-engineer.md
  technical-interviewer.md
  technical-lead.md
  test-reliability-engineer.md
commands/
  audit.md
  grill.md
  map.md
  test.md
  upscale.md
workflows/
  audit.md
  grill.md
  map.md
  test.md
  upscale.md
rules/
  01-architecture-guard.mdc
skills/
  architecture-mapper/
  code-griller/
  git-manager/
  mem-leak-auditor/
  prompt-upscaler/
  repo-search/
  shell-exec/
  test-generator/
```

## Agent Registry

The flat `agents/` directory is the source of truth. Flat files are deliberate:
all three hosts can consume the same minimal YAML and Markdown body without
category-path rewriting. Each profile contains:

- a unique lowercase `name`;
- a routing-focused `description`;
- `model: inherit` for host-selected model policy;
- Role, Scope, Guardrails, Workflow, and Output Contract sections.

Host-specific tool lists are intentionally omitted because tool identifiers and
permission semantics differ. Apply least-privilege tool restrictions in the
deployed native copy; the workspace permission policy remains authoritative.

`AGENTS.md` declares every alias and defines resolution order. It routes by
responsibility rather than programming language, keeping the always-loaded
registry compact while the full persona is loaded only when needed.

Common title variants compose existing profiles:

| Title or task | Primary profile | Optional supporting profile |
|---|---|---|
| Product engineer | `@application-engineer` | `@full-stack-engineer` for web vertical slices |
| API engineer | `@backend-engineer` | `@contract-compatibility-engineer` |
| SDET, QA, or test engineer | `@test-reliability-engineer` | relevant implementation profile |
| Application security engineer | `@security-engineer` | relevant application profile |
| DevSecOps engineer | `@platform-devops-engineer` | `@security-engineer` |
| Data scientist | `@machine-learning-engineer` | `@research-engineer` |
| Application database or migration engineer | `@backend-engineer` | `@contract-compatibility-engineer` |
| Storage-engine or query engineer | `@database-storage-engineer` | `@performance-engineer` |
| Database administrator or reliability engineer | `@database-storage-engineer` | `@site-reliability-engineer` |
| Infrastructure engineer | `@cloud-infrastructure-engineer`, `@platform-devops-engineer`, or `@site-reliability-engineer` by dominant risk | `@security-engineer` |
| MLOps engineer | `@mlops-engineer` | `@machine-learning-engineer` or `@platform-devops-engineer` |
| Blockchain or smart-contract engineer | `@distributed-systems-engineer` | `@security-engineer` |
| AR, VR, audio, or video engineer | `@graphics-realtime-engineer` | relevant application profile |
| Privacy engineer | `@security-engineer` | `@contract-compatibility-engineer` |

Language and framework expertise is task context, not a separate persona.
For example, a Rust network service routes to
`@networking-protocol-engineer`, while a React interface routes to
`@frontend-engineer`.

## How Platforms Use the Registry

Behavior below was verified against official documentation on 2026-07-29.

| Platform | Workspace contract | Native profile discovery | Native selection or delegation | Portable `@file` use |
|---|---|---|---|---|
| Antigravity | Reads root `AGENTS.md` automatically. | Copy profiles to `.agents/agents/` as flat Markdown files. Folder-based `agent.md` profiles are also supported. | `/agents` lists and switches primary agents; the planner can delegate to profiles using their descriptions. | `@agents/backend-engineer.md` attaches file context. It does not natively switch agents. |
| Cursor | Reads root `AGENTS.md` automatically alongside `.cursor/rules`. | Copy profiles to `.cursor/agents/`. | The parent can delegate automatically from `description`; `/backend-engineer` explicitly invokes the profile. | `@agents/backend-engineer.md` attaches file context. It does not register a subagent. |
| Claude Code | Loads `CLAUDE.md`, which imports root `AGENTS.md`. | Copy profiles to `.claude/agents/`; discovery is recursive. | Automatic delegation uses `description`; agent typeahead or `@agent-backend-engineer` guarantees one-task use; `claude --agent backend-engineer` applies it session-wide. | Plain `@agents/backend-engineer.md` imports file context. Native agent mentions are distinct typed entries. |

Without native installation, prompt with
`Use @agents/backend-engineer.md for this API change`. The file is attached as
context and the root registry instructs the active model to adopt that profile
for the task. This portable path does not create an isolated subagent.

Before copying profiles into a host directory, inspect existing definitions for
name collisions. Project-level native profiles may override user-level profiles
with the same name. Recopy intentionally when the canonical `agents/` profile
changes.

Official references:

- [Antigravity custom agents](https://antigravity.google/docs/subagents) and
  [root workspace context](https://antigravity.google/docs/cli/best-practices)
- [Cursor custom subagents](https://cursor.com/docs/subagents.md),
  [rules and `AGENTS.md`](https://cursor.com/docs/rules.md), and
  [`@` context](https://cursor.com/docs/agent/prompting.md)
- [Claude Code custom subagents](https://code.claude.com/docs/en/sub-agents) and
  [workspace memory imports](https://code.claude.com/docs/en/memory)

Every skill contains a router-compatible `SKILL.md` and one executable,
standard-library Python entry point. The scripts use direct argument vectors,
bounded traversal or output, deterministic ordering, explicit workspace roots,
and structured failures.

## Slash workflows

- `/upscale` converts loose text into a four-part execution specification.
- `/grill` produces a severity-ranked static engineering critique.
- `/audit` combines static ownership analysis with strict C and Valgrind checks.
- `/test` generates a non-overwriting Python or C regression smoke harness.
- `/map` emits a deterministic Mermaid dependency and inferred-call graph.

## Runtime requirements

- Python 3.10 or newer
- Git for `git-manager`
- A C compiler and Valgrind for live `mem-leak-auditor` runs

Run a utility with `--help` for its bounded interface. Memory auditing and
generated test execution run local code with the user's ordinary access; their
timeouts and resource limits are safeguards, not a security sandbox.
