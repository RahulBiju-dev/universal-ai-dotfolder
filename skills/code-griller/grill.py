#!/usr/bin/env python3
"""Perform bounded, read-only static engineering review of source targets."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, NoReturn, Sequence


SUPPORTED_EXTENSIONS = frozenset(
    {
        ".bash",
        ".c",
        ".cc",
        ".cpp",
        ".cxx",
        ".go",
        ".h",
        ".hh",
        ".hpp",
        ".java",
        ".js",
        ".jsx",
        ".py",
        ".rs",
        ".sh",
        ".ts",
        ".tsx",
    }
)
SKIPPED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".mypy_cache",
        ".next",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        "build",
        "coverage",
        "dist",
        "generated",
        "node_modules",
        "out",
        "site-packages",
        "target",
        "vendor",
        "venv",
    }
)
SECRET_NAMES = frozenset(
    {
        ".env",
        ".npmrc",
        ".pypirc",
        "authorized_keys",
        "credentials",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "id_rsa",
        "known_hosts",
        "secrets.yml",
    }
)
SECRET_SUFFIXES = (".key", ".p12", ".pfx", ".pem")
DEFAULT_MAX_FILES = 2000
DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 32 * 1024 * 1024
DEFAULT_MAX_FINDINGS = 300
SEVERITY_ORDER = {"blocker": 0, "high": 1, "medium": 2, "low": 3}
C_FAMILY = frozenset({".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp"})
SHELL_EXTENSIONS = frozenset({".bash", ".sh"})


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    path: str
    line: int
    confidence: str
    evidence: str
    impact: str
    remediation: str


@dataclass
class SourceFile:
    path: Path
    display_path: str
    text: str
    lines: list[str]
    public_symbols: list[str]
    byte_size: int = 0


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        payload = {
            "ok": False,
            "error": {"type": "argument_error", "message": message},
        }
        print(json.dumps(payload, sort_keys=True))
        raise SystemExit(2)


def build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(
        description=(
            "Statically critique source files for correctness, safety, "
            "complexity, architecture, and test risk."
        )
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=["."],
        metavar="TARGET",
        help="files or directories inside --root (default: root)",
    )
    parser.add_argument(
        "--root",
        default=".",
        metavar="PATH",
        help="workspace boundary (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="output format",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        metavar="COUNT",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=DEFAULT_MAX_FILE_BYTES,
        metavar="BYTES",
    )
    parser.add_argument(
        "--max-total-bytes",
        type=int,
        default=DEFAULT_MAX_TOTAL_BYTES,
        metavar="BYTES",
        help="aggregate source byte budget",
    )
    parser.add_argument(
        "--max-findings",
        type=int,
        default=DEFAULT_MAX_FINDINGS,
        metavar="COUNT",
    )
    return parser


def is_secret_path(path: Path) -> bool:
    name = path.name.casefold()
    return (
        name in SECRET_NAMES
        or any(name.endswith(suffix) for suffix in SECRET_SUFFIXES)
        or any(part.casefold() in {".ssh", ".gnupg"} for part in path.parts)
    )


def resolve_root(value: str) -> Path:
    root = Path(value).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Workspace root is not a directory: {root}")
    return root


def iter_directory(directory: Path) -> Iterator[Path]:
    for current, directory_names, file_names in os.walk(
        directory, topdown=True, followlinks=False
    ):
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name.casefold() not in SKIPPED_DIRECTORIES
            and not Path(current, name).is_symlink()
        )
        for file_name in sorted(file_names):
            path = Path(current, file_name)
            if (
                not path.is_symlink()
                and path.suffix.casefold() in SUPPORTED_EXTENSIONS
                and not is_secret_path(path)
            ):
                yield path


def resolve_targets(
    root: Path, values: Sequence[str], *, max_files: int
) -> tuple[list[Path], list[str], bool]:
    paths: set[Path] = set()
    errors: list[str] = []
    truncated = False
    for value in values or ["."]:
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.is_symlink():
            errors.append(f"Skipped symlink target: {value}")
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            errors.append(f"Cannot resolve {value!r}: {exc}")
            continue
        if not resolved.is_relative_to(root):
            errors.append(f"Target escapes workspace root: {value}")
            continue
        candidates: Iterable[Path]
        if resolved.is_dir():
            candidates = iter_directory(resolved)
        elif resolved.is_file() and resolved.suffix.casefold() in SUPPORTED_EXTENSIONS:
            candidates = (resolved,)
        else:
            errors.append(f"Unsupported source target: {value}")
            continue
        for path in candidates:
            if path in paths:
                continue
            if len(paths) >= max_files:
                truncated = True
                break
            paths.add(path)
        if truncated:
            break
    return sorted(paths), errors, truncated


def load_source(
    path: Path, root: Path, *, max_bytes: int
) -> tuple[SourceFile | None, str | None]:
    try:
        size = path.stat().st_size
        if size > max_bytes:
            return None, f"Skipped oversized file {path.relative_to(root)} ({size} bytes)"
        with path.open("rb") as handle:
            data = handle.read(max_bytes + 1)
    except OSError as exc:
        return None, f"Cannot read {path.relative_to(root)}: {exc}"
    if len(data) > max_bytes:
        return None, f"Skipped growing or oversized file {path.relative_to(root)}"
    if b"\x00" in data[:8192]:
        return None, f"Skipped binary file {path.relative_to(root)}"
    text = data.decode("utf-8", errors="replace")
    return (
        SourceFile(
            path=path,
            display_path=path.relative_to(root).as_posix(),
            text=text,
            lines=text.splitlines(),
            public_symbols=[],
            byte_size=len(data),
        ),
        None,
    )


def line_text(source: SourceFile, line: int) -> str:
    if 1 <= line <= len(source.lines):
        return source.lines[line - 1].strip()[:240]
    return ""


def finding(
    source: SourceFile,
    *,
    severity: str,
    category: str,
    line: int,
    confidence: str,
    impact: str,
    remediation: str,
    evidence: str | None = None,
) -> Finding:
    return Finding(
        severity=severity,
        category=category,
        path=source.display_path,
        line=max(1, line),
        confidence=confidence,
        evidence=(evidence if evidence is not None else line_text(source, line))[:300],
        impact=impact,
        remediation=remediation,
    )


def constant_bounded_for(node: ast.For) -> bool:
    iterator = node.iter
    if isinstance(iterator, (ast.List, ast.Tuple, ast.Set)):
        return len(iterator.elts) <= 32
    if (
        isinstance(iterator, ast.Call)
        and isinstance(iterator.func, ast.Name)
        and iterator.func.id == "range"
        and iterator.args
        and all(isinstance(argument, ast.Constant) for argument in iterator.args)
    ):
        values = [argument.value for argument in iterator.args]
        if all(isinstance(value, int) for value in values):
            try:
                return len(range(*values)) <= 64
            except (TypeError, ValueError):
                return False
    return False


def descendant_loops(node: ast.AST) -> Iterator[ast.For | ast.AsyncFor | ast.While]:
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
            yield child
        yield from descendant_loops(child)


def call_name(node: ast.Call) -> str:
    parts: list[str] = []
    current: ast.AST = node.func
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def function_nodes(tree: ast.AST) -> Iterator[ast.FunctionDef | ast.AsyncFunctionDef]:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def python_findings(source: SourceFile) -> list[Finding]:
    results: list[Finding] = []
    try:
        tree = ast.parse(source.text, filename=source.display_path)
    except SyntaxError as exc:
        return [
            finding(
                source,
                severity="blocker",
                category="correctness",
                line=exc.lineno or 1,
                confidence="observed",
                evidence=exc.msg,
                impact="The module cannot be parsed or executed.",
                remediation="Repair the syntax error and run the language parser again.",
            )
        ]

    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    for node in function_nodes(tree):
        if not node.name.startswith("_"):
            source.public_symbols.append(node.name)
        end_line = getattr(node, "end_lineno", node.lineno)
        length = end_line - node.lineno + 1
        branch_count = sum(
            isinstance(
                child,
                (
                    ast.If,
                    ast.For,
                    ast.AsyncFor,
                    ast.While,
                    ast.Try,
                    ast.With,
                    ast.AsyncWith,
                    ast.Match,
                ),
            )
            for child in ast.walk(node)
        )
        if length > 100 or branch_count > 18:
            results.append(
                finding(
                    source,
                    severity="medium",
                    category="architecture",
                    line=node.lineno,
                    confidence="observed",
                    impact=(
                        f"`{node.name}` spans {length} lines and {branch_count} "
                        "control-flow nodes, increasing change and test risk."
                    ),
                    remediation=(
                        "Extract cohesive pure operations and isolate I/O behind "
                        "narrow interfaces."
                    ),
                )
            )
        defaults = [*node.args.defaults, *node.args.kw_defaults]
        if any(
            isinstance(default, (ast.List, ast.Dict, ast.Set))
            for default in defaults
            if default is not None
        ):
            results.append(
                finding(
                    source,
                    severity="high",
                    category="correctness",
                    line=node.lineno,
                    confidence="observed",
                    impact="A mutable default is shared across calls and leaks state.",
                    remediation="Use `None` and allocate a fresh value inside the function.",
                )
            )

        assigned_resources: dict[str, tuple[int, str]] = {}
        closed_resources: set[str] = set()
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
                nested = next(descendant_loops(child), None)
                outer_bounded = isinstance(child, ast.For) and constant_bounded_for(child)
                nested_bounded = isinstance(nested, ast.For) and constant_bounded_for(nested)
                if nested is not None and not (outer_bounded and nested_bounded):
                    results.append(
                        finding(
                            source,
                            severity="high",
                            category="complexity",
                            line=child.lineno,
                            confidence="potential",
                            impact=(
                                "Data-dependent nested iteration can become quadratic "
                                "or worse under scale."
                            ),
                            remediation=(
                                "Index repeated lookup, precompute shared work, or "
                                "document a small hard bound with complexity."
                            ),
                        )
                    )
            if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                ancestor = parents.get(child)
                while ancestor is not None and ancestor is not node:
                    if isinstance(ancestor, (ast.For, ast.AsyncFor, ast.While)):
                        if (
                            isinstance(child.value, ast.JoinedStr)
                            or isinstance(child.value, ast.Constant)
                            and isinstance(child.value.value, str)
                        ):
                            results.append(
                                finding(
                                    source,
                                    severity="medium",
                                    category="complexity",
                                    line=child.lineno,
                                    confidence="potential",
                                    impact=(
                                        "Repeated immutable concatenation in a loop "
                                        "can copy cumulative output quadratically."
                                    ),
                                    remediation="Accumulate fragments and join once.",
                                )
                            )
                        break
                    ancestor = parents.get(ancestor)
            if isinstance(child, ast.Call):
                name = call_name(child)
                if name in {"eval", "exec", "os.system"}:
                    results.append(
                        finding(
                            source,
                            severity="blocker" if name in {"eval", "exec"} else "high",
                            category="security",
                            line=child.lineno,
                            confidence="observed",
                            impact=f"`{name}` can interpret data as executable code.",
                            remediation=(
                                "Use a typed parser or direct subprocess argument "
                                "vector with an allowlisted executable."
                            ),
                        )
                    )
                if name.startswith("subprocess."):
                    for keyword in child.keywords:
                        if (
                            keyword.arg == "shell"
                            and isinstance(keyword.value, ast.Constant)
                            and keyword.value.value is True
                        ):
                            results.append(
                                finding(
                                    source,
                                    severity="blocker",
                                    category="security",
                                    line=child.lineno,
                                    confidence="observed",
                                    impact="Shell interpretation enables injection and expansion.",
                                    remediation="Pass an argument list with shell execution disabled.",
                                )
                            )
                if name in {"pickle.load", "pickle.loads", "marshal.loads"}:
                    results.append(
                        finding(
                            source,
                            severity="high",
                            category="security",
                            line=child.lineno,
                            confidence="potential",
                            impact="Deserializing untrusted data can execute code or exhaust resources.",
                            remediation="Use a bounded data format and validate its schema.",
                        )
                    )
                if name == "open":
                    parent = parents.get(child)
                    while isinstance(parent, ast.Call):
                        parent = parents.get(parent)
                    in_with = False
                    ancestor = parents.get(child)
                    while ancestor is not None and ancestor is not node:
                        if isinstance(ancestor, (ast.With, ast.AsyncWith)):
                            in_with = True
                            break
                        ancestor = parents.get(ancestor)
                    if isinstance(parent, ast.Assign):
                        for target in parent.targets:
                            if isinstance(target, ast.Name):
                                assigned_resources[target.id] = (child.lineno, "file")
                    if not in_with and not isinstance(parent, ast.Assign):
                        results.append(
                            finding(
                                source,
                                severity="medium",
                                category="resource-safety",
                                line=child.lineno,
                                confidence="potential",
                                impact="The file lifetime is not visibly scoped.",
                                remediation="Use a context manager or guaranteed `finally` cleanup.",
                            )
                        )
                if name.endswith(".close") and isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        closed_resources.add(child.func.value.id)
            if isinstance(child, ast.ExceptHandler):
                broad = child.type is None or (
                    isinstance(child.type, ast.Name) and child.type.id in {"Exception", "BaseException"}
                )
                swallowed = not child.body or all(
                    isinstance(statement, (ast.Pass, ast.Return)) for statement in child.body
                )
                if broad and swallowed:
                    results.append(
                        finding(
                            source,
                            severity="high",
                            category="error-handling",
                            line=child.lineno,
                            confidence="observed",
                            impact="A broad exception is swallowed, hiding corruption and partial failure.",
                            remediation="Catch the narrow failure, preserve context, and recover or propagate.",
                        )
                    )

        for name, (line, _) in sorted(assigned_resources.items()):
            if name not in closed_resources:
                results.append(
                    finding(
                        source,
                        severity="high",
                        category="resource-safety",
                        line=line,
                        confidence="potential",
                        impact=f"Resource `{name}` has no visible guaranteed close in `{node.name}`.",
                        remediation="Wrap acquisition in a context manager or close it in `finally`.",
                    )
                )

    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            path_lower = source.display_path.casefold()
            if "test" not in path_lower:
                results.append(
                    finding(
                        source,
                        severity="medium",
                        category="error-handling",
                        line=node.lineno,
                        confidence="observed",
                        impact="Optimization can remove `assert`, eliminating runtime validation.",
                        remediation="Raise an explicit typed exception for externally reachable input.",
                    )
                )
    return results


def strip_c_comments_and_strings(text: str) -> str:
    output = list(text)
    index = 0
    state = "code"
    quote = ""
    while index < len(text):
        current = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "code" and current == "/" and following == "/":
            output[index] = output[index + 1] = " "
            index += 2
            state = "line-comment"
            continue
        if state == "code" and current == "/" and following == "*":
            output[index] = output[index + 1] = " "
            index += 2
            state = "block-comment"
            continue
        if state == "code" and current in {'"', "'"}:
            quote = current
            output[index] = " "
            index += 1
            state = "string"
            continue
        if state == "line-comment":
            if current == "\n":
                state = "code"
            else:
                output[index] = " "
            index += 1
            continue
        if state == "block-comment":
            if current == "*" and following == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "code"
            else:
                if current != "\n":
                    output[index] = " "
                index += 1
            continue
        if state == "string":
            if current == "\\" and following:
                output[index] = " "
                if following != "\n":
                    output[index + 1] = " "
                index += 2
            elif current == quote:
                output[index] = " "
                index += 1
                state = "code"
            else:
                if current != "\n":
                    output[index] = " "
                index += 1
            continue
        index += 1
    return "".join(output)


def matching_brace(text: str, opening: int) -> int | None:
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def c_functions(cleaned: str) -> Iterator[tuple[str, int, int, int]]:
    pattern = re.compile(
        r"(?m)^[ \t]*(?!(?:if|for|while|switch|catch)\s*\()"
        r"(?:[A-Za-z_][A-Za-z0-9_\s:*<>,~]*?[ \t]+)"
        r"(?P<name>[A-Za-z_~][A-Za-z0-9_:~]*)[ \t]*"
        r"\([^;{}]*\)[ \t]*(?:const[ \t]*)?(?:noexcept[ \t]*)?\{"
    )
    for match in pattern.finditer(cleaned):
        opening = cleaned.find("{", match.start(), match.end())
        closing = matching_brace(cleaned, opening)
        if closing is not None:
            line = cleaned.count("\n", 0, match.start()) + 1
            yield match.group("name"), line, opening + 1, closing


def offset_line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def variable_is_checked(body: str, variable: str, kind: str) -> bool:
    escaped = re.escape(variable)
    if kind == "pointer":
        pattern = rf"(?:!\s*{escaped}\b|{escaped}\s*==\s*(?:NULL|nullptr|0))"
    else:
        pattern = rf"(?:{escaped}\s*<\s*0|{escaped}\s*==\s*-1)"
    return re.search(pattern, body) is not None


def c_loop_spans(cleaned: str, start: int, end: int) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    pattern = re.compile(r"\b(for|while)\s*\((?P<header>[^()]*)\)\s*\{")
    for match in pattern.finditer(cleaned, start, end):
        opening = cleaned.find("{", match.start(), match.end())
        closing = matching_brace(cleaned, opening)
        if closing is not None and closing <= end:
            spans.append((match.start(), closing, match.group("header")))
    return spans


def c_findings(source: SourceFile) -> list[Finding]:
    results: list[Finding] = []
    cleaned = strip_c_comments_and_strings(source.text)
    functions = list(c_functions(cleaned))
    for name, start_line, start, end in functions:
        if not name.startswith("_"):
            source.public_symbols.append(name)
        body = cleaned[start:end]
        body_original = source.text[start:end]
        allocations = list(
            re.finditer(
                r"\b(?P<var>[A-Za-z_]\w*)\s*=\s*"
                r"(?P<allocator>malloc|calloc|realloc|strdup)\s*\((?P<args>[^;]*)\)",
                body,
            )
        )
        for allocation in allocations:
            variable = allocation.group("var")
            allocator = allocation.group("allocator")
            line = offset_line(source.text, start + allocation.start())
            after = body[allocation.end() :]
            if not variable_is_checked(after, variable, "pointer"):
                results.append(
                    finding(
                        source,
                        severity="high",
                        category="memory-safety",
                        line=line,
                        confidence="potential",
                        impact=f"`{allocator}` result `{variable}` may be dereferenced after allocation failure.",
                        remediation="Check for null immediately and enter a complete cleanup path.",
                    )
                )
            if allocator == "realloc":
                direct = re.search(
                    rf"\b{re.escape(variable)}\s*=\s*realloc\s*\(\s*"
                    rf"{re.escape(variable)}\b",
                    allocation.group(0),
                )
                if direct:
                    results.append(
                        finding(
                            source,
                            severity="high",
                            category="memory-safety",
                            line=line,
                            confidence="observed",
                            impact="Direct `realloc` assignment loses the original allocation on failure.",
                            remediation="Assign to a temporary pointer, validate it, then replace the owner.",
                        )
                    )
            if allocator == "malloc" and re.search(r"\b[A-Za-z_]\w*\s*\*\s*[A-Za-z_]\w*", allocation.group("args")):
                results.append(
                    finding(
                        source,
                        severity="high",
                        category="memory-safety",
                        line=line,
                        confidence="potential",
                        impact="Allocation-size multiplication can wrap before `malloc`.",
                        remediation="Check multiplicands against `SIZE_MAX` before multiplying.",
                    )
                )
            frees = list(re.finditer(rf"\bfree\s*\(\s*{re.escape(variable)}\s*\)", after))
            transfers = re.search(rf"\breturn\s+{re.escape(variable)}\s*;", after)
            if not frees and not transfers:
                results.append(
                    finding(
                        source,
                        severity="high",
                        category="memory-safety",
                        line=line,
                        confidence="potential",
                        impact=f"Owned allocation `{variable}` has no visible release or ownership transfer.",
                        remediation="Release it on every exit path or document and return ownership explicitly.",
                    )
                )
            if len(frees) > 1:
                results.append(
                    finding(
                        source,
                        severity="high",
                        category="memory-safety",
                        line=line,
                        confidence="potential",
                        impact=(
                            f"`{variable}` has multiple release sites whose path "
                            "mutual exclusion is not statically proven."
                        ),
                        remediation=(
                            "Prove mutually exclusive ownership paths or centralize "
                            "idempotent cleanup."
                        ),
                    )
                )
            if frees:
                before_free = after[: frees[0].start()]
                returns_before_free = []
                null_guard = re.compile(
                    rf"if\s*\(\s*(?:!\s*{re.escape(variable)}\b|"
                    rf"{re.escape(variable)}\s*==\s*(?:NULL|nullptr|0))\s*\)"
                    rf"\s*\{{?\s*$"
                )
                for match in re.finditer(r"\breturn\b", before_free):
                    if null_guard.search(before_free[max(0, match.start() - 200) : match.start()]):
                        continue
                    returns_before_free.append(match)
                if returns_before_free:
                    return_line = offset_line(
                        source.text,
                        start + allocation.end() + returns_before_free[0].start(),
                    )
                    results.append(
                        finding(
                            source,
                            severity="high",
                            category="resource-safety",
                            line=return_line,
                            confidence="potential",
                            impact=f"An early return can bypass cleanup of `{variable}`.",
                            remediation="Route exits through one cleanup block or use scoped ownership.",
                        )
                    )

        for resource in re.finditer(
            r"\b(?P<var>[A-Za-z_]\w*)\s*=\s*"
            r"(?P<acquire>fopen|open|socket|accept|dup|dup2)\s*\(",
            body,
        ):
            variable = resource.group("var")
            acquire = resource.group("acquire")
            line = offset_line(source.text, start + resource.start())
            closer = "fclose" if acquire == "fopen" else "close"
            after = body[resource.end() :]
            kind = "pointer" if acquire == "fopen" else "descriptor"
            if not variable_is_checked(after, variable, kind):
                results.append(
                    finding(
                        source,
                        severity="high",
                        category="error-handling",
                        line=line,
                        confidence="potential",
                        impact=f"`{acquire}` failure for `{variable}` is not visibly checked.",
                        remediation="Validate the sentinel result before use and preserve error context.",
                    )
                )
            if not re.search(rf"\b{closer}\s*\(\s*{re.escape(variable)}\s*\)", after) and not re.search(
                rf"\breturn\s+{re.escape(variable)}\s*;", after
            ):
                results.append(
                    finding(
                        source,
                        severity="high",
                        category="resource-safety",
                        line=line,
                        confidence="potential",
                        impact=f"Resource `{variable}` has no visible `{closer}` or ownership transfer.",
                        remediation="Close it on every path after successful acquisition.",
                    )
                )

        loops = c_loop_spans(cleaned, start, end)
        for outer_start, outer_end, outer_header in loops:
            for inner_start, inner_end, inner_header in loops:
                if outer_start < inner_start and inner_end < outer_end:
                    numeric_outer = re.fullmatch(r"[^;]*;[^;]*<\s*\d+\s*;[^;]*", outer_header.strip())
                    numeric_inner = re.fullmatch(r"[^;]*;[^;]*<\s*\d+\s*;[^;]*", inner_header.strip())
                    if not (numeric_outer and numeric_inner):
                        results.append(
                            finding(
                                source,
                                severity="high",
                                category="complexity",
                                line=offset_line(source.text, outer_start),
                                confidence="potential",
                                impact="Nested data-dependent loops can become quadratic or worse.",
                                remediation="Index repeated lookup or document and test a strict small bound.",
                            )
                        )
                    break

        function_length = body_original.count("\n") + 1
        if function_length > 120:
            results.append(
                finding(
                    source,
                    severity="medium",
                    category="architecture",
                    line=start_line,
                    confidence="observed",
                    impact=f"`{name}` spans {function_length} lines and couples multiple failure paths.",
                    remediation="Extract cohesive operations and retain one auditable ownership boundary.",
                )
            )

    line_rules = [
        (
            re.compile(r"\bgets\s*\("),
            "blocker",
            "memory-safety",
            "`gets` cannot enforce destination bounds.",
            "Use `fgets` with the actual destination capacity and validate truncation.",
        ),
        (
            re.compile(r"\b(?:strcpy|strcat|sprintf)\s*\("),
            "high",
            "memory-safety",
            "The unbounded copy or format operation can overflow its destination.",
            "Use a size-aware operation and prove capacity including the terminator.",
        ),
        (
            re.compile(r"(?<![=\w])(?:read|write)\s*\([^;]*\)\s*;"),
            "high",
            "error-handling",
            "The I/O result is discarded, losing short transfer, interruption, and failure.",
            "Loop over partial transfers and handle zero, `EINTR`, and terminal errors.",
        ),
        (
            re.compile(r"\*\s*\(\s*[A-Za-z_]\w*\s*\+\s*[^)]+\)"),
            "medium",
            "memory-safety",
            "Pointer-offset dereference has no locally proven object bound.",
            "Validate the offset against the originating allocation before pointer formation.",
        ),
    ]
    cleaned_lines = cleaned.splitlines()
    for line_number, code in enumerate(source.lines, start=1):
        cleaned_line = (
            cleaned_lines[line_number - 1]
            if line_number <= len(cleaned_lines)
            else ""
        )
        if re.search(r"\bscanf\s*\(", cleaned_line) and re.search(
            r"\bscanf\s*\(\s*\"[^\"]*%s", code
        ):
            results.append(
                finding(
                    source,
                    severity="high",
                    category="memory-safety",
                    line=line_number,
                    confidence="observed",
                    impact="An unbounded `%s` conversion can overflow the destination.",
                    remediation=(
                        "Specify a width below destination capacity or use bounded line input."
                    ),
                )
            )
        for pattern, severity, category, impact, remediation in line_rules:
            if pattern.search(cleaned_line):
                results.append(
                    finding(
                        source,
                        severity=severity,
                        category=category,
                        line=line_number,
                        confidence="observed" if severity == "blocker" else "potential",
                        impact=impact,
                        remediation=remediation,
                    )
                )
    return results


def strip_shell_comments(text: str) -> str:
    output: list[str] = []
    for line in text.splitlines(keepends=True):
        quote = ""
        escaped = False
        rendered = list(line)
        for index, character in enumerate(line):
            if escaped:
                escaped = False
                continue
            if character == "\\" and quote != "'":
                escaped = True
                continue
            if quote:
                if character == quote:
                    quote = ""
                continue
            if character in {"'", '"'}:
                quote = character
                continue
            if character == "#":
                for remainder in range(index, len(rendered)):
                    if rendered[remainder] not in {"\r", "\n"}:
                        rendered[remainder] = " "
                break
        output.append("".join(rendered))
    return "".join(output)


def generic_findings(source: SourceFile) -> list[Finding]:
    results: list[Finding] = []
    extension = source.path.suffix.casefold()
    if extension in SHELL_EXTENSIONS:
        analysis_text = strip_shell_comments(source.text)
    else:
        analysis_text = strip_c_comments_and_strings(source.text)
    for line_number, line in enumerate(analysis_text.splitlines(), start=1):
        stripped = line.strip()
        if re.search(r"\b(?:eval|Function)\s*\(", stripped) and extension in {
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
        }:
            results.append(
                finding(
                    source,
                    severity="blocker",
                    category="security",
                    line=line_number,
                    confidence="observed",
                    impact="Dynamic code construction can execute attacker-controlled input.",
                    remediation="Use a parser and explicit dispatch table.",
                )
            )
        if extension == ".rs" and re.search(r"\b(?:unwrap|expect)\s*\(", stripped):
            results.append(
                finding(
                    source,
                    severity="medium",
                    category="error-handling",
                    line=line_number,
                    confidence="potential",
                    impact="A recoverable runtime condition may panic the process.",
                    remediation="Propagate a typed error or justify the invariant explicitly.",
                )
            )
        if extension == ".rs" and re.search(r"\bunsafe\s*\{", stripped):
            results.append(
                finding(
                    source,
                    severity="high",
                    category="memory-safety",
                    line=line_number,
                    confidence="observed",
                    impact="The unsafe block moves memory invariants outside compiler enforcement.",
                    remediation="Minimize its surface and document plus test every required invariant.",
                )
            )
        if extension in SHELL_EXTENSIONS and re.search(r"(^|[;\s])eval(?:\s|$)", stripped):
            results.append(
                finding(
                    source,
                    severity="blocker",
                    category="security",
                    line=line_number,
                    confidence="observed",
                    impact="Shell `eval` reinterprets data as commands.",
                    remediation="Use arrays and direct command dispatch without reparsing.",
                )
            )
    return results


def deduplicate(findings: Iterable[Finding]) -> list[Finding]:
    unique: dict[tuple[str, int, str, str], Finding] = {}
    for item in findings:
        key = (item.path, item.line, item.category, item.impact)
        unique[key] = item
    return sorted(
        unique.values(),
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            item.path,
            item.line,
            item.category,
            item.impact,
        ),
    )


def add_test_gaps(sources: Sequence[SourceFile], findings: list[Finding]) -> None:
    test_text = "\n".join(
        source.text
        for source in sources
        if re.search(r"(^|[/_.-])tests?([/_.-]|$)", source.display_path.casefold())
    ).casefold()
    test_paths = {
        source.path.stem.removeprefix("test_").removesuffix("_test").casefold()
        for source in sources
        if "test" in source.display_path.casefold()
    }
    for source in sources:
        if "test" in source.display_path.casefold() or len(source.public_symbols) < 2:
            continue
        stem = source.path.stem.casefold()
        symbols_seen = any(symbol.casefold() in test_text for symbol in source.public_symbols)
        if stem not in test_paths and not symbols_seen:
            findings.append(
                finding(
                    source,
                    severity="medium",
                    category="test-coverage",
                    line=1,
                    confidence="potential",
                    evidence=", ".join(source.public_symbols[:8]),
                    impact="No loaded regression test references this module's public interfaces.",
                    remediation="Add focused success, boundary, malformed-input, and failure-path tests.",
                )
            )


def escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def result_payload(
    *,
    root: Path,
    sources: Sequence[SourceFile],
    findings: Sequence[Finding],
    diagnostics: Sequence[str],
    files_truncated: bool,
    findings_truncated: bool,
    byte_budget_truncated: bool,
    content_skipped: bool,
    bytes_scanned: int,
) -> dict[str, Any]:
    counts = {
        severity: sum(item.severity == severity for item in findings)
        for severity in SEVERITY_ORDER
    }
    if counts["blocker"]:
        verdict = "BLOCK"
    elif counts["high"]:
        verdict = "CHANGES_REQUIRED"
    elif not sources or files_truncated or byte_budget_truncated or content_skipped:
        verdict = "INCOMPLETE"
    elif counts["medium"]:
        verdict = "REVIEW_REQUIRED"
    else:
        verdict = "STATIC_PASS"
    return {
        "ok": verdict in {"STATIC_PASS", "REVIEW_REQUIRED"},
        "verdict": verdict,
        "root": str(root),
        "files_scanned": len(sources),
        "lines_scanned": sum(len(source.lines) for source in sources),
        "bytes_scanned": bytes_scanned,
        "counts": counts,
        "findings": [asdict(item) for item in findings],
        "diagnostics": list(diagnostics),
        "files_truncated": files_truncated,
        "byte_budget_truncated": byte_budget_truncated,
        "content_skipped": content_skipped,
        "findings_truncated": findings_truncated,
        "limitations": (
            "Static heuristics do not prove runtime correctness, exploitability, "
            "resource balance, or asymptotic bounds."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    counts = payload["counts"]
    lines = [
        "# Code Grill",
        "",
        f"**Verdict:** {payload['verdict']}",
        "",
        (
            f"Scanned {payload['files_scanned']} files and "
            f"{payload['lines_scanned']} lines. Findings: "
            f"{counts['blocker']} blocker, {counts['high']} high, "
            f"{counts['medium']} medium, {counts['low']} low."
        ),
        "",
    ]
    if payload["findings"]:
        lines.extend(
            [
                "| Severity | Category | Location | Confidence | Failure and impact | Remediation |",
                "|---|---|---|---|---|---|",
            ]
        )
        for item in payload["findings"]:
            failure = f"`{item['evidence']}` — {item['impact']}"
            lines.append(
                "| {severity} | {category} | `{path}:{line}` | {confidence} | "
                "{failure} | {remediation} |".format(
                    severity=item["severity"].upper(),
                    category=escape_markdown(item["category"]),
                    path=escape_markdown(item["path"]),
                    line=item["line"],
                    confidence=item["confidence"],
                    failure=escape_markdown(failure),
                    remediation=escape_markdown(item["remediation"]),
                )
            )
    else:
        lines.append("No actionable findings were produced by the bounded static pass.")

    if (
        payload["diagnostics"]
        or payload["files_truncated"]
        or payload["byte_budget_truncated"]
        or payload["content_skipped"]
        or payload["findings_truncated"]
    ):
        lines.extend(["", "## Audit Limits", ""])
        for diagnostic in payload["diagnostics"]:
            lines.append(f"- {escape_markdown(diagnostic)}")
        if payload["files_truncated"]:
            lines.append("- File enumeration reached its configured limit.")
        if payload["byte_budget_truncated"]:
            lines.append("- Aggregate source bytes reached the configured limit.")
        if payload["content_skipped"]:
            lines.append("- One or more requested sources could not be analyzed.")
        if payload["findings_truncated"]:
            lines.append("- Finding output reached its configured limit.")
    lines.extend(["", f"_Limit: {payload['limitations']}_"])
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if not 1 <= arguments.max_files <= 10_000:
        build_parser().error("--max-files must be between 1 and 10000")
    if not 1024 <= arguments.max_file_bytes <= 8 * 1024 * 1024:
        build_parser().error("--max-file-bytes must be between 1024 and 8388608")
    if not 1024 <= arguments.max_total_bytes <= 256 * 1024 * 1024:
        build_parser().error("--max-total-bytes must be between 1024 and 268435456")
    if not 1 <= arguments.max_findings <= 10_000:
        build_parser().error("--max-findings must be between 1 and 10000")

    try:
        root = resolve_root(arguments.root)
    except (OSError, RuntimeError, ValueError) as exc:
        build_parser().error(str(exc))
    paths, diagnostics, files_truncated = resolve_targets(
        root, arguments.targets, max_files=arguments.max_files
    )
    sources: list[SourceFile] = []
    raw_findings: list[Finding] = []
    bytes_scanned = 0
    byte_budget_truncated = False
    content_skipped = False
    finding_budget_truncated = False
    for path in paths:
        remaining_bytes = arguments.max_total_bytes - bytes_scanned
        if remaining_bytes <= 0:
            byte_budget_truncated = True
            break
        source, load_error = load_source(
            path,
            root,
            max_bytes=min(arguments.max_file_bytes, remaining_bytes),
        )
        if load_error:
            diagnostics.append(load_error)
            if remaining_bytes < arguments.max_file_bytes:
                byte_budget_truncated = True
                break
            content_skipped = True
            continue
        if source is None:
            diagnostics.append(f"Internal loader failure for {path.relative_to(root)}")
            continue
        bytes_scanned += source.byte_size
        sources.append(source)
        extension = path.suffix.casefold()
        if extension == ".py":
            raw_findings.extend(python_findings(source))
        elif extension in C_FAMILY:
            raw_findings.extend(c_findings(source))
        else:
            raw_findings.extend(generic_findings(source))
        if len(raw_findings) > arguments.max_findings * 4:
            raw_findings = deduplicate(raw_findings)[: arguments.max_findings * 2]
            finding_budget_truncated = True

    add_test_gaps(sources, raw_findings)
    all_findings = deduplicate(raw_findings)
    findings_truncated = (
        finding_budget_truncated or len(all_findings) > arguments.max_findings
    )
    selected = all_findings[: arguments.max_findings]
    payload = result_payload(
        root=root,
        sources=sources,
        findings=selected,
        diagnostics=diagnostics,
        files_truncated=files_truncated,
        findings_truncated=findings_truncated,
        byte_budget_truncated=byte_budget_truncated,
        content_skipped=content_skipped,
        bytes_scanned=bytes_scanned,
    )
    if arguments.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(payload))
    if payload["verdict"] == "INCOMPLETE":
        return 2
    return 1 if payload["verdict"] in {"BLOCK", "CHANGES_REQUIRED"} else 0


if __name__ == "__main__":
    sys.exit(main())
