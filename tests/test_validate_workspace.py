"""Regression tests for the repository structure validator."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_workspace import Validation  # noqa: E402


class WorkspaceValidationTests(unittest.TestCase):
    def test_current_workspace_is_valid(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = Validation(ROOT).run()

        self.assertEqual(result, 0, stderr.getvalue())
        self.assertIn("agents=50", stdout.getvalue())
        self.assertIn("skills=56", stdout.getvalue())
        self.assertIn("commands=53", stdout.getvalue())
        self.assertIn("workflows=53", stdout.getvalue())
        self.assertIn("rules=20", stdout.getvalue())

    def test_frontmatter_rejects_an_extra_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-skill.md"
            path.write_text(
                "---\n"
                "name: bad-skill\n"
                "description: Use for validation regression coverage.\n"
                "unexpected: value\n"
                "---\n"
                "# Bad Skill\n",
                encoding="utf-8",
            )
            validation = Validation(ROOT)

            document = validation.parse_document(path, "skill")

        self.assertIsNotNone(document)
        self.assertTrue(
            any("frontmatter keys must be" in error for error in validation.errors)
        )

    def test_command_and_workflow_target_the_same_skills(self) -> None:
        validation = Validation(ROOT)
        command = validation.parse_document(ROOT / "commands" / "audit.md", "command")
        workflow = validation.parse_document(
            ROOT / "workflows" / "audit.md", "workflow"
        )

        self.assertIsNotNone(command)
        self.assertIsNotNone(workflow)
        assert command is not None
        assert workflow is not None
        command_targets = validation.route_targets(command.path, command.body)
        workflow_targets = validation.route_targets(workflow.path, workflow.body)

        self.assertEqual(
            command_targets,
            ["code-griller", "mem-leak-auditor"],
        )
        self.assertEqual(command_targets, workflow_targets)
        self.assertEqual(validation.errors, [])

    def test_agent_registry_rejects_alias_path_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text(
                "# Context\n\n"
                "## Specialized Agent Registry\n\n"
                "- `@alpha-agent` → `agents/beta-agent.md` — wrong mapping.\n\n"
                "## Ambiguity Upscaling\n\n"
                "Keep work bounded.\n\n"
                "## Skill Routing Registry\n\n"
                "- `one-skill` — one bounded method.\n",
                encoding="utf-8",
            )
            validation = Validation(root)

            validation.validate_root_registry({"alpha-agent"}, {"one-skill"})

        self.assertTrue(
            any("mismatched profile" in error for error in validation.errors)
        )

    def test_readme_rejects_stale_count_statement(self) -> None:
        agent_names = {path.stem for path in (ROOT / "agents").glob("*.md")}
        skill_names = {
            path.name for path in (ROOT / "skills").iterdir() if path.is_dir()
        }
        command_names = {path.stem for path in (ROOT / "commands").glob("*.md")}
        workflow_names = {path.stem for path in (ROOT / "workflows").glob("*.md")}
        rule_names = {path.name for path in (ROOT / "rules").glob("*.mdc")}
        stale_readme = (ROOT / "README.md").read_text(encoding="utf-8").replace(
            "50 specialist",
            "49 specialist",
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(stale_readme, encoding="utf-8")
            validation = Validation(root)

            validation.validate_readme_catalogs(
                agent_names,
                skill_names,
                command_names,
                workflow_names,
                rule_names,
            )

        self.assertTrue(
            any("count statement" in error for error in validation.errors)
        )


if __name__ == "__main__":
    unittest.main()
