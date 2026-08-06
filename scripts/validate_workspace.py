#!/usr/bin/env python3
"""Validate the portable agent, skill, command, workflow, and rule registries.

Files and directories whose name starts with an underscore are authoring
templates. They are copy sources, never routed to, and are skipped everywhere.
"""

from __future__ import annotations

import argparse
import ast
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

FRONTMATTER_KEYS = {
    "agent": {"name", "description", "model"},
    "skill": {"name", "description"},
    "command": {"description", "argument-hint"},
    "workflow": {"name", "description"},
    "rule": {"description", "globs", "alwaysApply"},
}
AGENT_HEADINGS = ("Role", "Scope", "Guardrails", "Workflow", "Output Contract")
TEXT_SUFFIXES = {".md", ".mdc", ".yaml", ".yml"}
KEBAB = r"[a-z0-9]+(?:-[a-z0-9]+)*"
PLACEHOLDER_PATTERNS = (
    re.compile(r"\b(?:TODO|FIXME|TBD)\b"),
    re.compile(r"\.\.\."),
)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SKILL_REFERENCE = re.compile(rf"(?:\.\./)?skills/({KEBAB})/SKILL\.md")
AGENT_DECLARATION = re.compile(
    rf"(?m)^- `@(?P<alias>{KEBAB})`\s+→\s+`(?P<path>agents/(?P<stem>{KEBAB})\.md)`"
)
SKILL_DECLARATION = re.compile(rf"(?m)^- `(?P<name>{KEBAB})`\s+—")

EXIT_OK = 0
EXIT_FAILED = 1


def is_template(name: str) -> bool:
    return name.startswith("_")


@dataclass(frozen=True)
class Document:
    path: Path
    metadata: dict[str, str]
    body: str


class Validation:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []
        self.counts: dict[str, int] = {}

    # -- helpers ---------------------------------------------------------

    def fail(self, path: Path, message: str) -> None:
        try:
            label = path.relative_to(self.root).as_posix()
        except ValueError:
            label = str(path)
        self.errors.append(f"{label}: {message}")

    @staticmethod
    def unquote(value: str) -> str:
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            return value[1:-1]
        return value

    def entries(self, directory: str, pattern: str) -> list[Path]:
        """Sorted non-template files matching pattern inside a registry."""
        target = self.root / directory
        if not target.is_dir():
            self.fail(target, "missing registry directory")
            return []
        return sorted(
            path
            for path in target.glob(pattern)
            if path.is_file() and not is_template(path.name)
        )

    def parse_document(self, path: Path, kind: str) -> Document | None:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.fail(path, f"cannot read UTF-8 text: {exc}")
            return None
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            self.fail(path, "missing opening YAML frontmatter delimiter")
            return None
        try:
            boundary = lines.index("---", 1)
        except ValueError:
            self.fail(path, "missing closing YAML frontmatter delimiter")
            return None
        metadata: dict[str, str] = {}
        for number, line in enumerate(lines[1:boundary], start=2):
            match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):(?:[ \t]*(.*))?", line)
            if not match:
                self.fail(path, f"unsupported frontmatter syntax on line {number}")
                continue
            key, value = match.group(1), (match.group(2) or "").strip()
            if key in metadata:
                self.fail(path, f"duplicate frontmatter key {key!r}")
            metadata[key] = self.unquote(value)
        expected = FRONTMATTER_KEYS[kind]
        if set(metadata) != expected:
            self.fail(
                path,
                f"frontmatter keys must be {sorted(expected)}, got {sorted(metadata)}",
            )
        body = "\n".join(lines[boundary + 1 :]).strip()
        if not body:
            self.fail(path, "empty document body")
        return Document(path, metadata, body)

    # -- registries ------------------------------------------------------

    def validate_agents(self) -> set[str]:
        paths = self.entries("agents", "*.md")
        names: set[str] = set()
        for path in paths:
            document = self.parse_document(path, "agent")
            if document is None:
                continue
            name = document.metadata.get("name", "")
            if name != path.stem:
                self.fail(path, f"name {name!r} must match filename stem")
            if name in names:
                self.fail(path, f"duplicate agent name {name!r}")
            names.add(name)
            if document.metadata.get("model") != "inherit":
                self.fail(path, "model must be 'inherit' for portable routing")
            for heading in AGENT_HEADINGS:
                if not re.search(rf"(?m)^#{{1,2}} {re.escape(heading)}$", document.body):
                    self.fail(path, f"missing required heading {heading!r}")
        self.counts["agents"] = len(paths)
        return names

    def validate_skills(self) -> set[str]:
        directory = self.root / "skills"
        if not directory.is_dir():
            self.fail(directory, "missing registry directory")
            self.counts["skills"] = 0
            return set()
        skill_dirs = sorted(
            path
            for path in directory.iterdir()
            if path.is_dir() and not is_template(path.name)
        )
        names: set[str] = set()
        for skill_dir in skill_dirs:
            path = skill_dir / "SKILL.md"
            if not path.is_file():
                self.fail(skill_dir, "missing SKILL.md")
                continue
            document = self.parse_document(path, "skill")
            if document is None:
                continue
            name = document.metadata.get("name", "")
            if name != skill_dir.name:
                self.fail(path, f"name {name!r} must match directory name")
            if name in names:
                self.fail(path, f"duplicate skill name {name!r}")
            names.add(name)
            description = document.metadata.get("description", "")
            if len(description) < 25 or not re.search(
                r"\bUse (?:when|for|before|after|to|implicitly)\b", description
            ):
                self.fail(
                    path, "description must state capability and activation context"
                )
            self.validate_openai_metadata(skill_dir, name)
        self.counts["skills"] = len(skill_dirs)
        return names

    def validate_openai_metadata(self, skill_dir: Path, name: str) -> None:
        path = skill_dir / "agents" / "openai.yaml"
        if not path.is_file():
            self.fail(path, "missing skill UI metadata")
            return
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.fail(path, f"cannot read UTF-8 text: {exc}")
            return
        if not re.search(r"(?m)^interface:\s*$", text):
            self.fail(path, "missing interface mapping")
        values: dict[str, str] = {}
        for key in ("display_name", "short_description", "default_prompt"):
            match = re.search(rf'(?m)^  {key}:\s*["\'](.*)["\']\s*$', text)
            if not match:
                self.fail(path, f"missing quoted interface field {key!r}")
                continue
            values[key] = match.group(1)
        short_description = values.get("short_description", "")
        if short_description and not 25 <= len(short_description) <= 64:
            self.fail(path, "short_description must contain 25 to 64 characters")
        prompt = values.get("default_prompt", "")
        if prompt and f"${name}" not in prompt:
            self.fail(path, f"default_prompt must explicitly invoke ${name}")

    def validate_routes(self) -> set[str]:
        command_paths = self.entries("commands", "*.md")
        workflow_paths = self.entries("workflows", "*.md")
        command_names = {path.stem for path in command_paths}
        workflow_names = {path.stem for path in workflow_paths}
        command_targets: dict[str, list[str]] = {}
        workflow_targets: dict[str, list[str]] = {}

        for path in command_paths:
            document = self.parse_document(path, "command")
            if document:
                command_targets[path.stem] = self.route_targets(path, document.body)
        for path in workflow_paths:
            document = self.parse_document(path, "workflow")
            if document is None:
                continue
            if document.metadata.get("name") != path.stem:
                self.fail(path, "workflow name must match filename stem")
            workflow_targets[path.stem] = self.route_targets(path, document.body)

        missing_workflows = command_names - workflow_names
        missing_commands = workflow_names - command_names
        if missing_workflows:
            self.fail(
                self.root / "workflows", f"missing routes: {sorted(missing_workflows)}"
            )
        if missing_commands:
            self.fail(
                self.root / "commands", f"missing routes: {sorted(missing_commands)}"
            )
        for name in sorted(command_names & workflow_names):
            if command_targets.get(name) != workflow_targets.get(name):
                self.fail(
                    self.root / "commands" / f"{name}.md",
                    "skill targets differ from the paired workflow: "
                    f"{command_targets.get(name)} != {workflow_targets.get(name)}",
                )
        self.counts["commands"] = len(command_paths)
        self.counts["workflows"] = len(workflow_paths)
        return command_names

    def route_targets(self, path: Path, body: str) -> list[str]:
        names = list(dict.fromkeys(SKILL_REFERENCE.findall(body)))
        if not names:
            self.fail(path, "route does not reference a skill contract")
        for name in names:
            if not (self.root / "skills" / name / "SKILL.md").is_file():
                self.fail(path, f"route references missing skill {name!r}")
        return names

    def validate_rules(self) -> None:
        paths = self.entries("rules", "*.mdc")
        prefixes: list[int] = []
        always_count = 0
        for path in paths:
            document = self.parse_document(path, "rule")
            match = re.fullmatch(rf"(\d{{2}})-{KEBAB}\.mdc", path.name)
            if not match:
                self.fail(path, "rule filename must start with a two-digit order")
            else:
                prefixes.append(int(match.group(1)))
            if document:
                value = document.metadata.get("alwaysApply")
                if value not in {"true", "false"}:
                    self.fail(path, "alwaysApply must be true or false")
                always_count += value == "true"
        if len(prefixes) != len(set(prefixes)):
            self.fail(self.root / "rules", "rule order prefixes must be unique")
        expected = list(range(1, len(paths) + 1))
        if sorted(prefixes) != expected:
            self.fail(
                self.root / "rules", f"rule prefixes must be contiguous: {expected}"
            )
        if paths and always_count == 0:
            self.fail(self.root / "rules", "at least one rule must always apply")
        self.counts["rules"] = len(paths)

    def validate_root_registry(
        self, agent_names: set[str], skill_names: set[str]
    ) -> None:
        path = self.root / "AGENTS.md"
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.fail(path, f"cannot read UTF-8 text: {exc}")
            return

        agent_region = self.document_region(
            path, text, "## Specialized Agent Registry", "## Ambiguity Upscaling"
        )
        declarations = list(AGENT_DECLARATION.finditer(agent_region))
        aliases = [match.group("alias") for match in declarations]
        declared_paths = [match.group("path") for match in declarations]
        alias_set = set(aliases)
        if len(aliases) != len(alias_set):
            duplicates = sorted(name for name in alias_set if aliases.count(name) > 1)
            self.fail(path, f"duplicate declared aliases: {duplicates}")
        if len(declared_paths) != len(set(declared_paths)):
            self.fail(path, "multiple aliases declare the same profile path")
        for match in declarations:
            alias, stem = match.group("alias"), match.group("stem")
            if alias != stem:
                self.fail(path, f"alias @{alias} points to mismatched profile {stem!r}")
            if not (self.root / match.group("path")).is_file():
                self.fail(
                    path,
                    f"alias @{alias} points to missing path {match.group('path')!r}",
                )
        if alias_set != agent_names:
            self.fail(
                path,
                f"agent registry drift; missing={sorted(agent_names - alias_set)}, "
                f"unknown={sorted(alias_set - agent_names)}",
            )

        skill_region = self.document_region(
            path, text, "### Declared Skills", None
        )
        declared_skills = SKILL_DECLARATION.findall(skill_region)
        declared_set = set(declared_skills)
        if len(declared_skills) != len(declared_set):
            duplicates = sorted(
                name for name in declared_set if declared_skills.count(name) > 1
            )
            self.fail(path, f"duplicate declared skills: {duplicates}")
        if declared_set != skill_names:
            self.fail(
                path,
                f"skill registry drift; missing={sorted(skill_names - declared_set)}, "
                f"unknown={sorted(declared_set - skill_names)}",
            )

    def document_region(
        self, path: Path, text: str, start_heading: str, end_heading: str | None
    ) -> str:
        marker = f"{start_heading}\n"
        if marker not in text:
            self.fail(path, f"missing section {start_heading!r}")
            return ""
        region = text.split(marker, 1)[1]
        if end_heading is not None:
            if end_heading not in region:
                self.fail(path, f"missing section {end_heading!r}")
                return ""
            region = region.split(end_heading, 1)[0]
        return region

    # -- cross-cutting ---------------------------------------------------

    def text_files(self) -> list[Path]:
        paths: list[Path] = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            relative = path.relative_to(self.root)
            if any(part.startswith(".") for part in relative.parts):
                continue
            paths.append(path)
        return paths

    def validate_text(self) -> None:
        for path in self.text_files():
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                self.fail(path, f"cannot read UTF-8 text: {exc}")
                continue
            if not is_template(path.name):
                for pattern in PLACEHOLDER_PATTERNS:
                    match = pattern.search(text)
                    if match:
                        self.fail(path, f"unfinished marker {match.group(0)!r}")
            if path.suffix not in {".md", ".mdc"}:
                continue
            for target in MARKDOWN_LINK.findall(text):
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith(
                    "#"
                ):
                    continue
                resolved = (path.parent / target.split("#", 1)[0]).resolve()
                if not resolved.exists():
                    self.fail(path, f"broken local link {target!r}")

    def validate_python(self) -> None:
        utility_paths = sorted(self.root.glob("skills/*/*.py"))
        utility_paths.extend(sorted(self.root.glob("scripts/*.py")))
        for path in utility_paths:
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (OSError, UnicodeError, SyntaxError) as exc:
                self.fail(path, f"invalid Python source: {exc}")
        for path in utility_paths:
            if not path.stat().st_mode & stat.S_IXUSR:
                self.fail(path, "utility must be executable")

    def run(self) -> bool:
        agent_names = self.validate_agents()
        skill_names = self.validate_skills()
        self.validate_routes()
        self.validate_rules()
        self.validate_root_registry(agent_names, skill_names)
        self.validate_text()
        self.validate_python()
        return not self.errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parent.parent,
        type=Path,
        help="workspace root to validate",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"root is not a directory: {root}", file=sys.stderr)
        return EXIT_FAILED

    validation = Validation(root)
    ok = validation.run()
    summary = ", ".join(
        f"{key}={validation.counts[key]}" for key in sorted(validation.counts)
    )

    if ok:
        print(f"workspace valid: {summary}")
        return EXIT_OK
    for error in validation.errors:
        print(f"error: {error}", file=sys.stderr)
    print(
        f"{len(validation.errors)} error(s); checked {summary}",
        file=sys.stderr,
    )
    return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
