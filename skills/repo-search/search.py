#!/usr/bin/env python3
"""Deterministic, bounded, read-only repository text search."""

from __future__ import annotations

import argparse
import heapq
import json
import os
import re
import stat
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Sequence


DEFAULT_MAX_RESULTS = 40
DEFAULT_MAX_FILES = 4_000
DEFAULT_MAX_FILE_BYTES = 1_048_576
MAX_RESULTS = 500
MAX_FILES = 25_000
MAX_FILE_BYTES = 8_388_608
MAX_QUERY_CHARS = 512
MAX_LINE_CHARS = 320
MAX_DIRECTORY_ENTRIES = 10_000
MAX_VISITED_DIRECTORIES = 10_000
MAX_ERRORS = 20

_SOURCE_SUFFIXES = frozenset(
    {
        ".asm",
        ".bash",
        ".c",
        ".cc",
        ".cfg",
        ".clj",
        ".cmake",
        ".conf",
        ".cpp",
        ".cs",
        ".css",
        ".cxx",
        ".dart",
        ".fish",
        ".go",
        ".graphql",
        ".h",
        ".hh",
        ".hpp",
        ".hxx",
        ".ini",
        ".java",
        ".js",
        ".json",
        ".jsx",
        ".kt",
        ".kts",
        ".lua",
        ".md",
        ".mdc",
        ".mjs",
        ".ml",
        ".mli",
        ".php",
        ".proto",
        ".ps1",
        ".py",
        ".pyi",
        ".rb",
        ".rs",
        ".scala",
        ".scss",
        ".sh",
        ".sql",
        ".svelte",
        ".swift",
        ".tex",
        ".toml",
        ".ts",
        ".tsx",
        ".txt",
        ".vue",
        ".xml",
        ".yaml",
        ".yml",
        ".zig",
    }
)
_SOURCE_NAMES = frozenset(
    {
        ".dockerignore",
        ".editorconfig",
        ".gitattributes",
        ".gitignore",
        ".npmignore",
        "cmakelists.txt",
        "dockerfile",
        "gemfile",
        "justfile",
        "makefile",
        "meson.build",
        "procfile",
        "rakefile",
    }
)
_SKIP_DIRECTORIES = frozenset(
    {
        ".aws",
        ".cache",
        ".git",
        ".gnupg",
        ".hg",
        ".idea",
        ".mypy_cache",
        ".next",
        ".npm",
        ".pytest_cache",
        ".ruff_cache",
        ".ssh",
        ".svn",
        ".tox",
        ".venv",
        ".vscode",
        "__pycache__",
        "bower_components",
        "build",
        "coverage",
        "dist",
        "generated",
        "node_modules",
        "out",
        "target",
        "vendor",
        "venv",
    }
)
_SENSITIVE_NAME = re.compile(
    r"(?:^\.env(?:$|[._-].*|rc$))|"
    r"(?:^|[._-])(?:"
    r"secret|secrets|credential|credentials|password|passwords|passwd|"
    r"token|tokens|private[_-]?key|api[_-]?key|id_rsa|id_ed25519"
    r")(?:$|[._-])",
    re.IGNORECASE,
)
_SENSITIVE_SUFFIXES = frozenset(
    {".der", ".jks", ".key", ".keystore", ".p12", ".pfx", ".pem"}
)
_GENERATED_NAMES = frozenset(
    {
        "bun.lock",
        "cargo.lock",
        "composer.lock",
        "package-lock.json",
        "pnpm-lock.yaml",
        "poetry.lock",
        "yarn.lock",
    }
)
_WORD_RE = re.compile(r"[^\W_]+(?:_[^\W_]+)*", re.UNICODE)
_PY_DEFINITION_RE = re.compile(
    r"^\s*(?:async\s+)?(?:def|class)\s+[A-Za-z_]\w*"
)
_C_DEFINITION_RE = re.compile(
    r"^\s*(?:[A-Za-z_]\w*[\s:*&<>~,]+)+"
    r"(?:[A-Za-z_]\w*::)*[~A-Za-z_]\w*\s*\([^;{}]*\)\s*(?:const\s*)?\{?"
)
_GENERIC_DEFINITION_RE = re.compile(
    r"^\s*(?:function|func|fn|interface|struct|enum|type|class)\s+"
    r"[A-Za-z_]\w*"
)
_IMPORT_RE = re.compile(r"^\s*(?:from\s+\S+\s+import|import\s+|use\s+)")
_INCLUDE_RE = re.compile(r"^\s*#\s*include\b")
_CALL_RE = re.compile(r"\b[A-Za-z_]\w*\s*\(")


@dataclass(frozen=True)
class Query:
    phrase: str
    tokens: Sequence[str]
    case_sensitive: bool


@dataclass(frozen=True)
class Match:
    path: str
    line: int
    score: int
    kind: str
    text: str


@dataclass
class ScanState:
    scanned_files: int = 0
    scanned_bytes: int = 0
    matched_lines: int = 0
    visited_directories: int = 0
    traversal_truncated: bool = False
    skipped: dict[str, int] = field(
        default_factory=lambda: {
            "binary_or_encoding": 0,
            "dependency_or_generated": 0,
            "directory_limit": 0,
            "directory_entry_limit": 0,
            "file_limit": 0,
            "oversized": 0,
            "secret": 0,
            "symlink": 0,
            "unsupported": 0,
        }
    )
    errors: list[str] = field(default_factory=list)
    error_count: int = 0

    def error(self, path: Path, exc: BaseException) -> None:
        self.error_count += 1
        if len(self.errors) >= MAX_ERRORS:
            return
        message = _safe_display(f"{path}: {type(exc).__name__}: {exc}", 240)
        self.errors.append(message)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Search source and configuration text with deterministic ranking. "
            "Output is one compact JSON document."
        )
    )
    parser.add_argument("query", nargs="+", help="one or more search terms")
    parser.add_argument(
        "--root",
        default=".",
        help="search root and traversal boundary (default: current directory)",
    )
    parser.add_argument(
        "--case-sensitive", action="store_true", help="preserve query case"
    )
    parser.add_argument(
        "--definitions-only",
        action="store_true",
        help="return only likely symbol definitions",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help=f"result limit (1-{MAX_RESULTS}; default: {DEFAULT_MAX_RESULTS})",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"eligible file limit (1-{MAX_FILES}; default: {DEFAULT_MAX_FILES})",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=DEFAULT_MAX_FILE_BYTES,
        help=(
            f"per-file byte limit (1-{MAX_FILE_BYTES}; "
            f"default: {DEFAULT_MAX_FILE_BYTES})"
        ),
    )
    return parser


def _bounded(
    parser: argparse.ArgumentParser, name: str, value: int, maximum: int
) -> int:
    if not 1 <= value <= maximum:
        parser.error(f"{name} must be between 1 and {maximum}")
    return value


def _is_within(path: Path, boundary: Path) -> bool:
    try:
        return os.path.commonpath((str(path), str(boundary))) == str(boundary)
    except ValueError:
        return False


def _resolve_root(raw_root: str, parser: argparse.ArgumentParser) -> Path:
    try:
        root = Path(raw_root).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        parser.error(f"cannot resolve root: {exc}")
    if not root.is_dir():
        parser.error("root must be a directory")
    return root


def _safe_display(text: str, limit: int = MAX_LINE_CHARS) -> str:
    rendered: list[str] = []
    for char in text:
        if char == "\t":
            rendered.append(" ")
        elif unicodedata.category(char).startswith("C"):
            rendered.append(" ")
        else:
            rendered.append(char)
    compact = re.sub(r"\s+", " ", "".join(rendered)).strip()
    if len(compact) <= limit:
        return compact
    suffix = " [truncated]"
    return compact[: max(0, limit - len(suffix))].rstrip() + suffix


def _is_sensitive(name: str) -> bool:
    lowered = name.casefold()
    return bool(_SENSITIVE_NAME.search(lowered)) or Path(lowered).suffix in (
        _SENSITIVE_SUFFIXES
    )


def _is_source(name: str) -> bool:
    lowered = name.casefold()
    if lowered in _GENERATED_NAMES or lowered.endswith((".min.js", ".min.css")):
        return False
    return lowered in _SOURCE_NAMES or Path(lowered).suffix in _SOURCE_SUFFIXES


def _entry_key(entry: os.DirEntry[str]) -> tuple[str, str]:
    return (entry.name.casefold(), entry.name)


def _directory_entries(directory: Path, state: ScanState) -> list[os.DirEntry[str]]:
    try:
        with os.scandir(directory) as iterator:
            entries = heapq.nsmallest(
                MAX_DIRECTORY_ENTRIES + 1, iterator, key=_entry_key
            )
    except OSError as exc:
        state.error(directory, exc)
        return []
    if len(entries) > MAX_DIRECTORY_ENTRIES:
        entries.pop()
        state.skipped["directory_entry_limit"] += 1
        state.traversal_truncated = True
    return entries


def _iter_source_files(
    root: Path, state: ScanState, max_files: int
) -> Iterator[Path]:
    stack = [root]
    yielded = 0
    while stack:
        if state.visited_directories >= MAX_VISITED_DIRECTORIES:
            state.skipped["directory_limit"] += len(stack)
            state.traversal_truncated = True
            return
        directory = stack.pop()
        state.visited_directories += 1
        child_directories: list[Path] = []
        for entry in _directory_entries(directory, state):
            path = Path(os.path.abspath(entry.path))
            if not _is_within(path, root):
                state.skipped["unsupported"] += 1
                state.traversal_truncated = True
                continue
            try:
                if entry.is_symlink():
                    state.skipped["symlink"] += 1
                    continue
                if entry.is_dir(follow_symlinks=False):
                    if entry.name.casefold() in _SKIP_DIRECTORIES:
                        state.skipped["dependency_or_generated"] += 1
                    elif _is_sensitive(entry.name):
                        state.skipped["secret"] += 1
                    else:
                        child_directories.append(path)
                    continue
                if not entry.is_file(follow_symlinks=False):
                    state.skipped["unsupported"] += 1
                    continue
            except OSError as exc:
                state.error(path, exc)
                continue

            if _is_sensitive(entry.name):
                state.skipped["secret"] += 1
                continue
            if not _is_source(entry.name):
                key = (
                    "dependency_or_generated"
                    if entry.name.casefold() in _GENERATED_NAMES
                    else "unsupported"
                )
                state.skipped[key] += 1
                continue
            if yielded >= max_files:
                state.skipped["file_limit"] += 1
                state.traversal_truncated = True
                return
            yielded += 1
            yield path
        stack.extend(reversed(child_directories))


def _read_text(
    path: Path, root: Path, max_file_bytes: int, state: ScanState
) -> str | None:
    if not _is_within(Path(os.path.abspath(path)), root):
        state.skipped["unsupported"] += 1
        state.traversal_truncated = True
        return None
    flags = os.O_RDONLY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor: int | None = None
    try:
        descriptor = os.open(path, flags)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            state.skipped["unsupported"] += 1
            return None
        if metadata.st_size > max_file_bytes:
            state.skipped["oversized"] += 1
            return None
        chunks: list[bytes] = []
        remaining = max_file_bytes + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
    except OSError as exc:
        state.error(path, exc)
        return None
    finally:
        if descriptor is not None:
            os.close(descriptor)

    if len(data) > max_file_bytes:
        state.skipped["oversized"] += 1
        return None
    if b"\x00" in data:
        state.skipped["binary_or_encoding"] += 1
        return None
    try:
        text = data.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        state.skipped["binary_or_encoding"] += 1
        return None
    state.scanned_files += 1
    state.scanned_bytes += len(data)
    return text


def _tokenize(text: str, case_sensitive: bool) -> Sequence[str]:
    tokens: list[str] = []
    seen: set[str] = set()
    for match in _WORD_RE.finditer(text):
        token = match.group(0)
        if not case_sensitive:
            token = token.casefold()
        if token not in seen:
            seen.add(token)
            tokens.append(token)
    return tuple(tokens)


def _make_query(raw: str, case_sensitive: bool, parser: argparse.ArgumentParser) -> Query:
    raw = raw.strip()
    if not raw:
        parser.error("query must not be empty")
    if len(raw) > MAX_QUERY_CHARS:
        parser.error(f"query exceeds the {MAX_QUERY_CHARS}-character limit")
    phrase = raw if case_sensitive else raw.casefold()
    tokens = _tokenize(raw, case_sensitive)
    if not tokens:
        parser.error("query must contain at least one letter or number")
    return Query(phrase=phrase, tokens=tokens, case_sensitive=case_sensitive)


def _kind(line: str) -> str:
    if _PY_DEFINITION_RE.search(line) or _C_DEFINITION_RE.search(
        line
    ) or _GENERIC_DEFINITION_RE.search(line):
        return "definition"
    if _INCLUDE_RE.search(line):
        return "include"
    if _IMPORT_RE.search(line):
        return "import"
    if _CALL_RE.search(line):
        return "call"
    return "reference"


def _line_score(line: str, relative_path: str, query: Query, kind: str) -> int:
    comparable = line if query.case_sensitive else line.casefold()
    comparable_path = (
        relative_path if query.case_sensitive else relative_path.casefold()
    )
    line_tokens = set(_tokenize(line, query.case_sensitive))
    matched = 0
    score = 0
    if query.phrase in comparable:
        score += 45
    for token in query.tokens:
        if token in line_tokens:
            score += 14
            matched += 1
        elif token in comparable:
            score += 5
            matched += 1
        if token in comparable_path:
            score += 2
    if matched == 0 and query.phrase not in comparable:
        return 0
    if matched == len(query.tokens):
        score += 18
    score += {
        "definition": 24,
        "import": 8,
        "include": 8,
        "call": 3,
        "reference": 0,
    }[kind]
    return score


def _match_key(match: Match) -> tuple[int, str, str, int, str]:
    return (-match.score, match.path.casefold(), match.path, match.line, match.text)


def search_repository(
    root: Path,
    query: Query,
    *,
    definitions_only: bool,
    max_results: int,
    max_files: int,
    max_file_bytes: int,
) -> dict[str, Any]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("search root must be a directory")
    state = ScanState()
    retained: list[Match] = []
    trim_threshold = max_results * 4
    for path in _iter_source_files(root, state, max_files):
        text = _read_text(path, root, max_file_bytes, state)
        if text is None:
            continue
        relative_path = path.relative_to(root).as_posix()
        for number, line in enumerate(text.splitlines(), start=1):
            kind = _kind(line)
            if definitions_only and kind != "definition":
                continue
            score = _line_score(line, relative_path, query, kind)
            if score <= 0:
                continue
            state.matched_lines += 1
            retained.append(
                Match(
                    path=relative_path,
                    line=number,
                    score=score,
                    kind=kind,
                    text=_safe_display(line),
                )
            )
            if len(retained) >= trim_threshold:
                retained.sort(key=_match_key)
                del retained[max_results * 2 :]

    retained.sort(key=_match_key)
    matches = retained[:max_results]
    truncated = state.traversal_truncated or state.matched_lines > len(matches)
    return {
        "matches": [
            {
                "path": match.path,
                "line": match.line,
                "score": match.score,
                "kind": match.kind,
                "text": match.text,
            }
            for match in matches
        ],
        "truncated": truncated,
        "scanned_files": state.scanned_files,
        "scanned_bytes": state.scanned_bytes,
        "visited_directories": state.visited_directories,
        "matched_lines": state.matched_lines,
        "skipped": state.skipped,
        "error_count": state.error_count,
        "errors": state.errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    max_results = _bounded(parser, "--max-results", args.max_results, MAX_RESULTS)
    max_files = _bounded(parser, "--max-files", args.max_files, MAX_FILES)
    max_file_bytes = _bounded(
        parser, "--max-file-bytes", args.max_file_bytes, MAX_FILE_BYTES
    )
    root = _resolve_root(args.root, parser)
    query = _make_query(" ".join(args.query), args.case_sensitive, parser)
    result = search_repository(
        root,
        query,
        definitions_only=args.definitions_only,
        max_results=max_results,
        max_files=max_files,
        max_file_bytes=max_file_bytes,
    )
    try:
        json.dump(
            result,
            sys.stdout,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=False,
        )
        sys.stdout.write("\n")
    except BrokenPipeError:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
