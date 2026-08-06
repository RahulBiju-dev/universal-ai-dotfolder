#!/usr/bin/env python3
"""Regression tests for the workspace structural validator."""

from __future__ import annotations

import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import validate_workspace  # noqa: E402


AGENT = """---
name: {name}
description: Routing sentence describing the work this persona owns for tests.
model: inherit
---

# Role
Test persona.

# Scope
- Own the fixture.

# Guardrails
- Obey the root policy.

# Workflow
1. Inspect.

# Output Contract
- Report evidence.
"""

SKILL = """---
name: {name}
description: "Structural fixture skill for validator regression tests. Use when a test needs a valid skill package."
---

# Fixture Skill
Provide a valid skill contract.

## Workflow
1. Inspect the fixture.

## Output Contract
- Report findings.
"""

OPENAI = """interface:
  display_name: "Fixture Skill"
  short_description: "Structural fixture for validator tests"
  default_prompt: "Use ${name} to exercise the validator."
"""

COMMAND = """---
description: Fixture route used by validator regression tests.
argument-hint: fixture input
---

# Fixture Route

Read its `skills/{skill}/SKILL.md` and follow its contract.
"""

WORKFLOW = """---
name: {name}
description: Fixture trajectory used by validator regression tests.
---

# Fixture Trajectory

Read `../skills/{skill}/SKILL.md` and follow its contract.
"""

RULE = """---
description: Fixture rule used by validator regression tests.
globs: "*"
alwaysApply: true
---

# Fixture Rule

- Keep changes inside the requested surface.
"""

AGENTS_MD = """# Fixture Context

## Specialized Agent Registry

{agent_lines}

## Ambiguity Upscaling

Expand safe defaults silently.

## Skill Routing Registry

### Declared Skills

{skill_lines}
"""


def build_workspace(root: Path) -> None:
    """Write a minimal workspace that the validator accepts."""
    for directory in ("agents", "commands", "workflows", "rules", "scripts", "tests"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    (root / "skills" / "fixture-skill" / "agents").mkdir(parents=True, exist_ok=True)

    (root / "agents" / "fixture-engineer.md").write_text(
        AGENT.format(name="fixture-engineer"), encoding="utf-8"
    )
    (root / "skills" / "fixture-skill" / "SKILL.md").write_text(
        SKILL.format(name="fixture-skill"), encoding="utf-8"
    )
    (root / "skills" / "fixture-skill" / "agents" / "openai.yaml").write_text(
        OPENAI.format(name="fixture-skill"), encoding="utf-8"
    )
    (root / "commands" / "fixture.md").write_text(
        COMMAND.format(skill="fixture-skill"), encoding="utf-8"
    )
    (root / "workflows" / "fixture.md").write_text(
        WORKFLOW.format(name="fixture", skill="fixture-skill"), encoding="utf-8"
    )
    (root / "rules" / "01-fixture-guard.mdc").write_text(RULE, encoding="utf-8")
    (root / "AGENTS.md").write_text(
        AGENTS_MD.format(
            agent_lines="- `@fixture-engineer` → `agents/fixture-engineer.md` — fixture.",
            skill_lines="- `fixture-skill` — fixture.",
        ),
        encoding="utf-8",
    )


class ValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        build_workspace(self.root)

    def validate(self) -> validate_workspace.Validation:
        validation = validate_workspace.Validation(self.root)
        validation.run()
        return validation

    def assertFailure(self, fragment: str) -> None:
        errors = self.validate().errors
        self.assertTrue(
            any(fragment in error for error in errors),
            f"expected an error containing {fragment!r}, got {errors}",
        )


class CleanWorkspaceTests(ValidatorTestCase):
    def test_clean_workspace_passes(self) -> None:
        validation = self.validate()
        self.assertEqual(validation.errors, [])

    def test_counts_reported(self) -> None:
        validation = self.validate()
        self.assertEqual(
            validation.counts,
            {"agents": 1, "skills": 1, "commands": 1, "workflows": 1, "rules": 1},
        )

    def test_templates_are_skipped(self) -> None:
        (self.root / "agents" / "_TEMPLATE.md").write_text(
            "no frontmatter here at all", encoding="utf-8"
        )
        (self.root / "skills" / "_template").mkdir()
        validation = self.validate()
        self.assertEqual(validation.errors, [])
        self.assertEqual(validation.counts["agents"], 1)
        self.assertEqual(validation.counts["skills"], 1)


class AgentTests(ValidatorTestCase):
    def test_name_must_match_filename(self) -> None:
        (self.root / "agents" / "fixture-engineer.md").write_text(
            AGENT.format(name="other-engineer"), encoding="utf-8"
        )
        self.assertFailure("must match filename stem")

    def test_model_must_be_inherit(self) -> None:
        path = self.root / "agents" / "fixture-engineer.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "model: inherit", "model: claude-opus-5"
            ),
            encoding="utf-8",
        )
        self.assertFailure("model must be 'inherit'")

    def test_missing_heading_detected(self) -> None:
        path = self.root / "agents" / "fixture-engineer.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("# Guardrails", "# Limits"),
            encoding="utf-8",
        )
        self.assertFailure("missing required heading 'Guardrails'")

    def test_registry_drift_detected(self) -> None:
        (self.root / "agents" / "second-engineer.md").write_text(
            AGENT.format(name="second-engineer"), encoding="utf-8"
        )
        self.assertFailure("agent registry drift")


class SkillTests(ValidatorTestCase):
    def test_description_needs_activation_phrase(self) -> None:
        path = self.root / "skills" / "fixture-skill" / "SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Use when a test needs a valid skill package.", "Nothing else."
            ),
            encoding="utf-8",
        )
        self.assertFailure("activation context")

    def test_missing_openai_metadata_detected(self) -> None:
        (self.root / "skills" / "fixture-skill" / "agents" / "openai.yaml").unlink()
        self.assertFailure("missing skill UI metadata")

    def test_default_prompt_must_invoke_skill(self) -> None:
        path = self.root / "skills" / "fixture-skill" / "agents" / "openai.yaml"
        path.write_text(
            path.read_text(encoding="utf-8").replace("$fixture-skill", "$other-skill"),
            encoding="utf-8",
        )
        self.assertFailure("must explicitly invoke $fixture-skill")

    def test_short_description_length_enforced(self) -> None:
        path = self.root / "skills" / "fixture-skill" / "agents" / "openai.yaml"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Structural fixture for validator tests", "Too short"
            ),
            encoding="utf-8",
        )
        self.assertFailure("25 to 64 characters")


class RouteTests(ValidatorTestCase):
    def test_unpaired_command_detected(self) -> None:
        (self.root / "workflows" / "fixture.md").unlink()
        self.assertFailure("missing routes: ['fixture']")

    def test_missing_skill_target_detected(self) -> None:
        (self.root / "commands" / "fixture.md").write_text(
            COMMAND.format(skill="absent-skill"), encoding="utf-8"
        )
        self.assertFailure("route references missing skill 'absent-skill'")

    def test_divergent_targets_detected(self) -> None:
        (self.root / "skills" / "other-skill" / "agents").mkdir(parents=True)
        (self.root / "skills" / "other-skill" / "SKILL.md").write_text(
            SKILL.format(name="other-skill"), encoding="utf-8"
        )
        (self.root / "skills" / "other-skill" / "agents" / "openai.yaml").write_text(
            OPENAI.format(name="other-skill"), encoding="utf-8"
        )
        (self.root / "commands" / "fixture.md").write_text(
            COMMAND.format(skill="other-skill"), encoding="utf-8"
        )
        self.assertFailure("skill targets differ from the paired workflow")

    def test_route_without_skill_reference_detected(self) -> None:
        (self.root / "commands" / "fixture.md").write_text(
            "---\ndescription: No target here at all.\nargument-hint: none\n---\n\nBody.\n",
            encoding="utf-8",
        )
        self.assertFailure("does not reference a skill contract")


class RuleTests(ValidatorTestCase):
    def test_noncontiguous_prefixes_detected(self) -> None:
        (self.root / "rules" / "05-second-guard.mdc").write_text(
            RULE.replace("alwaysApply: true", "alwaysApply: false"), encoding="utf-8"
        )
        self.assertFailure("rule prefixes must be contiguous")

    def test_always_apply_must_be_boolean(self) -> None:
        path = self.root / "rules" / "01-fixture-guard.mdc"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "alwaysApply: true", "alwaysApply: yes"
            ),
            encoding="utf-8",
        )
        self.assertFailure("alwaysApply must be true or false")

    def test_at_least_one_global_rule_required(self) -> None:
        path = self.root / "rules" / "01-fixture-guard.mdc"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "alwaysApply: true", "alwaysApply: false"
            ),
            encoding="utf-8",
        )
        self.assertFailure("at least one rule must always apply")


class TextAndPythonTests(ValidatorTestCase):
    def test_unfinished_marker_detected(self) -> None:
        path = self.root / "agents" / "fixture-engineer.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nTODO: finish this.\n",
            encoding="utf-8",
        )
        self.assertFailure("unfinished marker")

    def test_broken_local_link_detected(self) -> None:
        path = self.root / "skills" / "fixture-skill" / "SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nSee [guide](references/absent.md).\n",
            encoding="utf-8",
        )
        self.assertFailure("broken local link")

    def test_utility_syntax_error_detected(self) -> None:
        (self.root / "skills" / "fixture-skill" / "util.py").write_text(
            "def broken(:\n", encoding="utf-8"
        )
        self.assertFailure("invalid Python source")

    def test_utility_must_be_executable(self) -> None:
        path = self.root / "skills" / "fixture-skill" / "util.py"
        path.write_text("print('ok')\n", encoding="utf-8")
        path.chmod(0o644)
        self.assertFailure("utility must be executable")

    def test_executable_utility_passes(self) -> None:
        path = self.root / "skills" / "fixture-skill" / "util.py"
        path.write_text("print('ok')\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        self.assertEqual(self.validate().errors, [])


class EntryPointTests(ValidatorTestCase):
    def test_main_returns_zero_on_clean_workspace(self) -> None:
        self.assertEqual(
            validate_workspace.main(["--root", str(self.root)]),
            validate_workspace.EXIT_OK,
        )

    def test_main_returns_failure_on_broken_workspace(self) -> None:
        (self.root / "workflows" / "fixture.md").unlink()
        self.assertEqual(
            validate_workspace.main(["--root", str(self.root)]),
            validate_workspace.EXIT_FAILED,
        )


if __name__ == "__main__":
    unittest.main()
