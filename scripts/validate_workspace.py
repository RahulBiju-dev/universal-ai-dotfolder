#!/usr/bin/env python3
"""Validate the portable agent, skill, command, workflow, and rule registries."""

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
TEXT_SUFFIXES = {".md", ".mdc", ".yaml", ".yml"}
PLACEHOLDER_PATTERNS = (
    re.compile(r"\b(?:TODO|FIXME|TBD)\b"),
    re.compile(
        r"\[(?:PROJECT|AI_ROLE|PRIMARY|CORE|WORKSPACE|ALLOWED|READ_ONLY|"
        r"EXCLUDED|APPROVED|VALIDATION|ACCEPTANCE)_[A-Z0-9_]+\]"
    ),
    re.compile(r"\.\.\."),
)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
AGENT_DECLARATION = re.compile(
    r"(?m)^- `@(?P<alias>[a-z0-9]+(?:-[a-z0-9]+)*)`\s+"
    r"→\s+`(?P<path>agents/(?P<stem>[a-z0-9]+(?:-[a-z0-9]+)*)\.md)`"
)
SKILL_DECLARATION = re.compile(
    r"(?m)^- `(?P<name>[a-z0-9]+(?:-[a-z0-9]+)*)`\s+—"
)


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

    def fail(self, path: Path, message: str) -> None:
        try:
            label = path.relative_to(self.root).as_posix()
        except ValueError:
            label = str(path)
        self.errors.append(f"{label}: {message}")

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

    @staticmethod
    def unquote(value: str) -> str:
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            return value[1:-1]
        return value

    def validate_agents(self) -> set[str]:
        directory = self.root / "agents"
        paths = sorted(directory.glob("*.md"))
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
            for heading in ("Role", "Scope", "Guardrails", "Workflow", "Output Contract"):
                if not re.search(rf"(?m)^#{{1,2}} {re.escape(heading)}$", document.body):
                    self.fail(path, f"missing required heading {heading!r}")
        self.counts["agents"] = len(paths)
        return names

    def validate_skills(self) -> set[str]:
        directory = self.root / "skills"
        skill_dirs = sorted(path for path in directory.iterdir() if path.is_dir())
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
                self.fail(path, "description must state capability and activation context")
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

    def validate_routes(self) -> tuple[set[str], set[str]]:
        command_paths = sorted((self.root / "commands").glob("*.md"))
        workflow_paths = sorted((self.root / "workflows").glob("*.md"))
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
            if document and document.metadata.get("name") != path.stem:
                self.fail(path, "workflow name must match filename stem")
            if document:
                workflow_targets[path.stem] = self.route_targets(path, document.body)
        missing_workflows = command_names - workflow_names
        missing_commands = workflow_names - command_names
        if missing_workflows:
            self.fail(self.root / "workflows", f"missing routes: {sorted(missing_workflows)}")
        if missing_commands:
            self.fail(self.root / "commands", f"missing routes: {sorted(missing_commands)}")
        for name in sorted(command_names & workflow_names):
            if command_targets.get(name) != workflow_targets.get(name):
                self.fail(
                    self.root / "commands" / f"{name}.md",
                    "skill targets differ from the paired workflow: "
                    f"{command_targets.get(name)} != {workflow_targets.get(name)}",
                )
        self.counts["commands"] = len(command_paths)
        self.counts["workflows"] = len(workflow_paths)
        return command_names, workflow_names

    def route_targets(self, path: Path, body: str) -> list[str]:
        names = list(
            dict.fromkeys(
                re.findall(
                    r"(?:\.\./)?skills/([a-z0-9]+(?:-[a-z0-9]+)*)/SKILL\.md",
                    body,
                )
            )
        )
        if not names:
            self.fail(path, "route does not reference a skill contract")
        for name in names:
            target = self.root / "skills" / name / "SKILL.md"
            if not target.is_file():
                self.fail(path, f"route references missing skill {name!r}")
        return names

    def validate_rules(self) -> set[str]:
        paths = sorted((self.root / "rules").glob("*.mdc"))
        prefixes: list[int] = []
        always_count = 0
        for path in paths:
            document = self.parse_document(path, "rule")
            match = re.fullmatch(r"(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.mdc", path.name)
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
            self.fail(self.root / "rules", f"rule prefixes must be contiguous: {expected}")
        if always_count == 0:
            self.fail(self.root / "rules", "at least one rule must always apply")
        self.counts["rules"] = len(paths)
        return {path.name for path in paths}

    def validate_root_registry(self, agent_names: set[str], skill_names: set[str]) -> None:
        path = self.root / "AGENTS.md"
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.fail(path, f"cannot read UTF-8 text: {exc}")
            return
        agent_region = self.document_region(
            path,
            text,
            "## Specialized Agent Registry",
            "## Ambiguity Upscaling",
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
            alias = match.group("alias")
            stem = match.group("stem")
            target = self.root / match.group("path")
            if alias != stem:
                self.fail(path, f"alias @{alias} points to mismatched profile {stem!r}")
            if not target.is_file():
                self.fail(path, f"alias @{alias} points to missing path {match.group('path')!r}")
        if alias_set != agent_names:
            self.fail(
                path,
                f"agent registry drift; missing={sorted(agent_names - alias_set)}, "
                f"unknown={sorted(alias_set - agent_names)}",
            )
        skill_region = self.document_region(
            path,
            text,
            "## Skill Routing Registry",
            None,
        )
        declared_skills = SKILL_DECLARATION.findall(skill_region)
        declared_skill_set = set(declared_skills)
        if len(declared_skills) != len(declared_skill_set):
            duplicates = sorted(
                name for name in declared_skill_set if declared_skills.count(name) > 1
            )
            self.fail(path, f"duplicate declared skills: {duplicates}")
        if declared_skill_set != skill_names:
            self.fail(
                path,
                f"skill registry drift; missing={sorted(skill_names - declared_skill_set)}, "
                f"unknown={sorted(declared_skill_set - skill_names)}",
            )

    def document_region(
        self,
        path: Path,
        text: str,
        start_heading: str,
        end_heading: str | None,
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

    def validate_readme_catalogs(
        self,
        agent_names: set[str],
        skill_names: set[str],
        command_names: set[str],
        workflow_names: set[str],
        rule_names: set[str],
    ) -> None:
        path = self.root / "README.md"
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.fail(path, f"cannot read UTF-8 text: {exc}")
            return
        count_match = re.search(
            r"It combines (\d+) specialist\s+agent personas, (\d+) on-demand "
            r"skills, (\d+) slash routes.*?,\s*(\d+) Cursor rules "
            r"\((\d+) global and (\d+) conditional\)",
            text,
            flags=re.DOTALL,
        )
        global_rule_count = 0
        for rule_name in rule_names:
            rule_path = self.root / "rules" / rule_name
            try:
                rule_text = rule_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                self.fail(rule_path, f"cannot read UTF-8 text: {exc}")
                continue
            global_rule_count += bool(
                re.search(r"(?m)^alwaysApply:\s*true\s*$", rule_text)
            )
        expected_counts = (
            len(agent_names),
            len(skill_names),
            len(command_names),
            len(rule_names),
            global_rule_count,
            len(rule_names) - global_rule_count,
        )
        if not count_match:
            self.fail(path, "missing canonical toolkit count statement")
        else:
            observed_counts = tuple(int(value) for value in count_match.groups())
            if observed_counts != expected_counts:
                self.fail(
                    path,
                    f"toolkit count statement is {observed_counts}, expected {expected_counts}",
                )
        tree_counts = {
            "agents": len(agent_names),
            "commands": len(command_names),
            "workflows": len(workflow_names),
            "rules": len(rule_names),
            "skills": len(skill_names),
        }
        for directory, expected in tree_counts.items():
            match = re.search(rf"(?m)^[├└]── {directory}/\s+(\d+)\b", text)
            if not match:
                self.fail(path, f"architecture tree omits the {directory}/ count")
            elif int(match.group(1)) != expected:
                self.fail(
                    path,
                    f"architecture tree reports {directory}={match.group(1)}, "
                    f"expected {expected}",
                )
        agent_region = self.document_region(
            path,
            text,
            "## Agent Persona Registry",
            "Route by dominant responsibility",
        )
        readme_agents = re.findall(
            r"`([a-z0-9]+(?:-[a-z0-9]+)+)`",
            agent_region,
        )
        self.compare_catalog(path, "agent", readme_agents, agent_names)
        skill_region = self.document_region(
            path,
            text,
            "## Skill Toolkit",
            "The `requirement-griller`",
        )
        readme_skills = re.findall(
            r"`([a-z0-9]+(?:-[a-z0-9]+)+)`",
            skill_region,
        )
        self.compare_catalog(path, "skill", readme_skills, skill_names)
        command_region = self.document_region(
            path,
            text,
            "## Slash Route Catalog",
            "Read-only review routes",
        )
        readme_commands = re.findall(
            r"`/([a-z0-9]+(?:-[a-z0-9]+)*)`",
            command_region,
        )
        self.compare_catalog(path, "command", readme_commands, command_names)
        rule_region = self.document_region(
            path,
            text,
            "## Rule Set",
            "## Validation",
        )
        readme_rules = re.findall(
            r"`(\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.mdc)`",
            rule_region,
        )
        self.compare_catalog(path, "rule", readme_rules, rule_names)

    def compare_catalog(
        self,
        path: Path,
        label: str,
        observed: list[str],
        expected: set[str],
    ) -> None:
        observed_set = set(observed)
        duplicates = sorted(name for name in observed_set if observed.count(name) > 1)
        if duplicates:
            self.fail(path, f"README {label} catalog duplicates: {duplicates}")
        if observed_set != expected:
            self.fail(
                path,
                f"README {label} catalog drift; missing={sorted(expected - observed_set)}, "
                f"unknown={sorted(observed_set - expected)}",
            )

    def validate_python(self) -> None:
        utility_paths = sorted((self.root / "skills").glob("*/*.py"))
        utility_paths.extend(sorted((self.root / "scripts").glob("*.py")))
        test_paths = sorted((self.root / "tests").rglob("*.py"))
        executable_paths = set(utility_paths)
        paths = utility_paths + test_paths
        for path in paths:
            try:
                source = path.read_text(encoding="utf-8")
                ast.parse(source, filename=str(path))
            except (OSError, UnicodeError, SyntaxError) as exc:
                self.fail(path, f"invalid Python source: {exc}")
                continue
            if path in executable_paths and not path.stat().st_mode & stat.S_IXUSR:
                self.fail(path, "Python utility is not owner-executable")
        self.counts["python utilities"] = len(utility_paths)
        self.counts["python tests"] = len(test_paths)

    def validate_text(self) -> None:
        roots = (
            self.root / "AGENTS.md",
            self.root / "CLAUDE.md",
            self.root / "README.md",
            self.root / "agents",
            self.root / "commands",
            self.root / "rules",
            self.root / "skills",
            self.root / "workflows",
        )
        paths: list[Path] = []
        for root in roots:
            if root.is_file():
                paths.append(root)
            elif root.is_dir():
                paths.extend(
                    path
                    for path in root.rglob("*")
                    if path.is_file() and path.suffix in TEXT_SUFFIXES
                )
        for path in sorted(paths):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                self.fail(path, f"cannot read UTF-8 text: {exc}")
                continue
            for pattern in PLACEHOLDER_PATTERNS:
                match = pattern.search(text)
                if match:
                    line = text.count("\n", 0, match.start()) + 1
                    self.fail(
                        path,
                        f"forbidden placeholder marker on line {line}: {match.group(0)!r}",
                    )
            for line_number, line in enumerate(text.splitlines(), start=1):
                if line.rstrip() != line:
                    self.fail(path, f"trailing whitespace on line {line_number}")
            self.validate_links(path, text)

    def validate_links(self, path: Path, text: str) -> None:
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip()
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = target.removeprefix("<").removesuffix(">")
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(self.root)
            except ValueError:
                self.fail(path, f"local link escapes workspace: {raw_target!r}")
                continue
            if not resolved.exists():
                self.fail(path, f"broken local link: {raw_target!r}")

    def run(self) -> int:
        required = (
            "AGENTS.md",
            "CLAUDE.md",
            "README.md",
            "agents",
            "commands",
            "rules",
            "scripts",
            "skills",
            "tests",
            "workflows",
        )
        for name in required:
            if not (self.root / name).exists():
                self.fail(self.root / name, "required workspace artifact is missing")
        agent_names = self.validate_agents()
        skill_names = self.validate_skills()
        command_names, workflow_names = self.validate_routes()
        rule_names = self.validate_rules()
        self.validate_root_registry(agent_names, skill_names)
        self.validate_readme_catalogs(
            agent_names,
            skill_names,
            command_names,
            workflow_names,
            rule_names,
        )
        self.validate_python()
        self.validate_text()
        if self.errors:
            for error in sorted(set(self.errors)):
                print(f"ERROR {error}", file=sys.stderr)
            print(f"FAILED {len(set(self.errors))} validation error(s)", file=sys.stderr)
            return 1
        summary = " ".join(f"{key}={value}" for key, value in self.counts.items())
        print(f"OK {summary}")
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="workspace root; defaults to the validator's parent repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR workspace root is not a directory: {root}", file=sys.stderr)
        return 2
    return Validation(root).run()


if __name__ == "__main__":
    raise SystemExit(main())
