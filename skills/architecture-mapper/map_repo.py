#!/usr/bin/env python3
"""Emit a bounded Mermaid dependency and inferred-call graph without execution."""

from __future__ import annotations

import argparse
import ast
import hashlib
import heapq
import html
import os
import posixpath
import re
import stat
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Iterator, Sequence


DEFAULT_MAX_FILES = 2_000
DEFAULT_MAX_FILE_BYTES = 1_048_576
DEFAULT_MAX_NODES = 2_500
DEFAULT_MAX_EDGES = 6_000
MAX_FILES = 10_000
MAX_FILE_BYTES = 8_388_608
MAX_NODES = 20_000
MAX_EDGES = 50_000
MAX_DIRECTORY_ENTRIES = 10_000
MAX_VISITED_DIRECTORIES = 10_000
MAX_ERRORS = 16
MAX_IMPORTS_PER_FILE = 1_000
MAX_FUNCTIONS_PER_FILE = 1_000
MAX_CALLS_PER_SCOPE = 500

_PYTHON_SUFFIXES = frozenset({".py", ".pyi"})
_C_SUFFIXES = frozenset({".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"})
_SOURCE_SUFFIXES = _PYTHON_SUFFIXES | _C_SUFFIXES
_HEADER_SUFFIXES = frozenset({".h", ".hh", ".hpp", ".hxx"})
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
_INCLUDE_RE = re.compile(
    r'^[ \t]*#[ \t]*include[ \t]*[<"](?P<header>[^>"\r\n]+)[>"]',
    re.MULTILINE,
)
_C_FUNCTION_RE = re.compile(
    r"(?m)^[ \t]*"
    r"(?P<prefix>(?:[^#\n;{}]*\r?\n){0,4}[^#\n;{}]*?)"
    r"(?P<name>(?:[A-Za-z_]\w*::)*~?[A-Za-z_]\w*)[ \t]*"
    r"\((?P<params>[^;{}]*?)\)[ \t\r\n]*"
    r"(?:const\b[ \t\r\n]*)?"
    r"(?:noexcept(?:[ \t]*\([^)]*\))?[ \t\r\n]*)?"
    r"(?:->[^{;\r\n]+[ \t\r\n]*)?"
    r"(?P<brace>\{)"
)
_C_CALL_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?P<name>(?:[A-Za-z_]\w*::)*~?[A-Za-z_]\w*)"
    r"[ \t\r\n]*\("
)
_C_NON_CALLS = frozenset(
    {
        "_Alignof",
        "_Generic",
        "_Static_assert",
        "alignas",
        "alignof",
        "catch",
        "decltype",
        "delete",
        "do",
        "for",
        "if",
        "new",
        "noexcept",
        "return",
        "sizeof",
        "static_assert",
        "switch",
        "throw",
        "typeid",
        "typeof",
        "while",
    }
)
_PY_BUILTINS = frozenset(
    {
        "__import__",
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "breakpoint",
        "bytearray",
        "bytes",
        "callable",
        "chr",
        "classmethod",
        "compile",
        "complex",
        "delattr",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "eval",
        "exec",
        "filter",
        "float",
        "format",
        "frozenset",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "input",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "locals",
        "map",
        "max",
        "memoryview",
        "min",
        "next",
        "object",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "property",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "setattr",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "vars",
        "zip",
    }
)


@dataclass(frozen=True)
class PyImport:
    module: str
    symbol: str | None
    local: str


@dataclass
class PyFunction:
    qualname: str
    line: int
    calls: list[str] = field(default_factory=list)


@dataclass
class PyUnit:
    path: str
    module: str
    is_package: bool
    imports: list[PyImport]
    functions: list[PyFunction]
    module_calls: list[str]


@dataclass
class CFunction:
    name: str
    line: int
    calls: list[str]

    @property
    def short_name(self) -> str:
        return self.name.rsplit("::", 1)[-1].lstrip("~")


@dataclass
class CUnit:
    path: str
    includes: list[str]
    functions: list[CFunction]


@dataclass(frozen=True)
class Node:
    key: str
    label: str


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    label: str


@dataclass
class ScanState:
    discovered_files: int = 0
    parsed_files: int = 0
    scanned_bytes: int = 0
    visited_directories: int = 0
    errors: list[str] = field(default_factory=list)
    error_count: int = 0
    skipped: dict[str, int] = field(
        default_factory=lambda: {
            "binary_or_encoding": 0,
            "dependency_or_generated": 0,
            "directory_limit": 0,
            "directory_entry_limit": 0,
            "file_limit": 0,
            "oversized": 0,
            "parse_error": 0,
            "secret": 0,
            "symlink": 0,
            "unsupported": 0,
        }
    )
    truncation_reasons: set[str] = field(default_factory=set)

    def error(self, path: Path | str, exc: BaseException) -> None:
        self.error_count += 1
        if len(self.errors) < MAX_ERRORS:
            self.errors.append(
                _safe_text(f"{path}: {type(exc).__name__}: {exc}", 200)
            )

    def truncate(self, reason: str) -> None:
        self.truncation_reasons.add(reason)


class Graph:
    def __init__(self, max_nodes: int, max_edges: int, state: ScanState) -> None:
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.state = state
        self.nodes: dict[str, Node] = {}
        self.edges: set[Edge] = set()

    def add_node(self, key: str, label: str) -> bool:
        if key in self.nodes:
            return True
        if len(self.nodes) >= self.max_nodes:
            self.state.truncate("node limit")
            return False
        self.nodes[key] = Node(key, label)
        return True

    def add_edge(self, source: str, target: str, label: str) -> bool:
        if source not in self.nodes or target not in self.nodes:
            return False
        edge = Edge(source, target, label)
        if edge in self.edges:
            return True
        if len(self.edges) >= self.max_edges:
            self.state.truncate("edge limit")
            return False
        self.edges.add(edge)
        return True


class PythonAnalyzer(ast.NodeVisitor):
    def __init__(
        self, path: str, module: str, is_package: bool, state: ScanState
    ) -> None:
        self.path = path
        self.module = module
        self.is_package = is_package
        self.state = state
        self.imports: list[PyImport] = []
        self.functions: list[PyFunction] = []
        self.module_calls: list[str] = []
        self._scope: list[str] = []
        self._active_functions: list[PyFunction] = []

    def unit(self) -> PyUnit:
        return PyUnit(
            path=self.path,
            module=self.module,
            is_package=self.is_package,
            imports=self.imports,
            functions=self.functions,
            module_calls=self.module_calls,
        )

    def _record_import(self, item: PyImport) -> None:
        if len(self.imports) >= MAX_IMPORTS_PER_FILE:
            self.state.truncate("per-file import limit")
            return
        self.imports.append(item)

    def _visit_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        qualname = ".".join((*self._scope, node.name))
        if len(self.functions) >= MAX_FUNCTIONS_PER_FILE:
            self.state.truncate("per-file function limit")
            return
        function = PyFunction(qualname=qualname, line=node.lineno)
        self.functions.append(function)
        self._scope.append(node.name)
        self._active_functions.append(function)
        self.generic_visit(node)
        self._active_functions.pop()
        self._scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local = alias.asname or alias.name.split(".", 1)[0]
            self._record_import(
                PyImport(module=alias.name, symbol=None, local=local)
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        base = _absolute_import(
            self.module, self.is_package, node.module or "", node.level
        )
        for alias in node.names:
            if alias.name == "*":
                self._record_import(PyImport(module=base, symbol="*", local="*"))
                continue
            local = alias.asname or alias.name
            self._record_import(
                PyImport(module=base, symbol=alias.name, local=local)
            )

    def visit_Call(self, node: ast.Call) -> None:
        name = _python_call_name(node.func)
        if name:
            target = (
                self._active_functions[-1].calls
                if self._active_functions
                else self.module_calls
            )
            if len(target) < MAX_CALLS_PER_SCOPE:
                target.append(name)
            else:
                self.state.truncate("per-scope call limit")
        self.generic_visit(node)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Print a deterministic Mermaid flowchart for Python and C/C++ "
            "imports, includes, definitions, and statically inferred calls."
        )
    )
    parser.add_argument(
        "--root",
        default=".",
        help="repository root and traversal boundary (default: current directory)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=DEFAULT_MAX_FILES,
        help=f"source file limit (1-{MAX_FILES}; default: {DEFAULT_MAX_FILES})",
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
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=DEFAULT_MAX_NODES,
        help=f"graph node limit (1-{MAX_NODES}; default: {DEFAULT_MAX_NODES})",
    )
    parser.add_argument(
        "--max-edges",
        type=int,
        default=DEFAULT_MAX_EDGES,
        help=f"graph edge limit (1-{MAX_EDGES}; default: {DEFAULT_MAX_EDGES})",
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


def _safe_text(text: str, limit: int = 140) -> str:
    safe: list[str] = []
    for char in text:
        if unicodedata.category(char).startswith("C"):
            safe.append(" ")
        else:
            safe.append(char)
    value = re.sub(r"\s+", " ", "".join(safe)).strip()
    if len(value) <= limit:
        return value
    suffix = " [truncated]"
    return value[: max(0, limit - len(suffix))].rstrip() + suffix


def _mermaid_label(text: str) -> str:
    value = html.escape(_safe_text(text), quote=True)
    return (
        value.replace("`", "&#96;")
        .replace("\\", "&#92;")
        .replace("[", "&#91;")
        .replace("]", "&#93;")
    )


def _is_sensitive(name: str) -> bool:
    lowered = name.casefold()
    return bool(_SENSITIVE_NAME.search(lowered)) or Path(lowered).suffix in (
        _SENSITIVE_SUFFIXES
    )


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
        state.truncate("directory entry limit")
    return entries


def _iter_source_files(
    root: Path, state: ScanState, max_files: int
) -> Iterator[Path]:
    stack = [root]
    yielded = 0
    while stack:
        if state.visited_directories >= MAX_VISITED_DIRECTORIES:
            state.skipped["directory_limit"] += len(stack)
            state.truncate("directory limit")
            return
        directory = stack.pop()
        state.visited_directories += 1
        child_directories: list[Path] = []
        for entry in _directory_entries(directory, state):
            path = Path(os.path.abspath(entry.path))
            if not _is_within(path, root):
                state.skipped["unsupported"] += 1
                state.truncate("outside-root path")
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
            if path.suffix.casefold() not in _SOURCE_SUFFIXES:
                state.skipped["unsupported"] += 1
                continue
            if yielded >= max_files:
                state.skipped["file_limit"] += 1
                state.truncate("file limit")
                return
            yielded += 1
            state.discovered_files += 1
            yield path
        stack.extend(reversed(child_directories))


def _read_text(
    path: Path, root: Path, max_file_bytes: int, state: ScanState
) -> str | None:
    if not _is_within(Path(os.path.abspath(path)), root):
        state.skipped["unsupported"] += 1
        state.truncate("outside-root path")
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
    state.scanned_bytes += len(data)
    return text


def _module_for_path(relative_path: str) -> tuple[str, bool]:
    pure = PurePosixPath(relative_path)
    parts = list(pure.with_suffix("").parts)
    is_package = bool(parts and parts[-1] == "__init__")
    if is_package:
        parts.pop()
    return ".".join(parts), is_package


def _absolute_import(
    current_module: str, is_package: bool, module: str, level: int
) -> str:
    if level == 0:
        return module
    package = current_module.split(".") if current_module else []
    if not is_package and package:
        package.pop()
    upward = max(0, level - 1)
    if upward > len(package):
        package = []
    elif upward:
        del package[-upward:]
    if module:
        package.extend(module.split("."))
    return ".".join(part for part in package if part)


def _python_call_name(node: ast.expr) -> str | None:
    parts: list[str] = []
    current: ast.expr = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _parse_python(
    path: str,
    text: str,
    module: str,
    is_package: bool,
    state: ScanState,
) -> PyUnit | None:
    try:
        tree = ast.parse(text, filename=path, type_comments=True)
        analyzer = PythonAnalyzer(path, module, is_package, state)
        analyzer.visit(tree)
    except (SyntaxError, ValueError, RecursionError, MemoryError) as exc:
        state.skipped["parse_error"] += 1
        state.error(path, exc)
        return None
    state.parsed_files += 1
    return analyzer.unit()


def _strip_c_comments(text: str) -> str:
    output = list(text)
    index = 0
    state = "code"
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and following == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "line_comment"
                continue
            if char == "/" and following == "*":
                output[index] = output[index + 1] = " "
                index += 2
                state = "block_comment"
                continue
            if char == '"':
                state = "string"
            elif char == "'":
                state = "character"
        elif state == "line_comment":
            if char == "\n":
                state = "code"
            else:
                output[index] = " "
            index += 1
            continue
        elif state == "block_comment":
            if char == "*" and following == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "code"
                continue
            if char != "\n":
                output[index] = " "
            index += 1
            continue
        elif state in {"string", "character"}:
            quote = '"' if state == "string" else "'"
            if char == "\\" and following:
                index += 2
                continue
            if char == quote:
                state = "code"
        index += 1
    return "".join(output)


def _strip_c_noncode(text: str) -> str:
    output = list(text)
    index = 0
    state = "code"
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and following == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "line_comment"
                continue
            if char == "/" and following == "*":
                output[index] = output[index + 1] = " "
                index += 2
                state = "block_comment"
                continue
            if char == '"':
                output[index] = " "
                index += 1
                state = "string"
                continue
            if char == "'":
                output[index] = " "
                index += 1
                state = "character"
                continue
        elif state == "line_comment":
            if char == "\n":
                state = "code"
            else:
                output[index] = " "
            index += 1
            continue
        elif state == "block_comment":
            if char == "*" and following == "/":
                output[index] = output[index + 1] = " "
                index += 2
                state = "code"
                continue
            if char != "\n":
                output[index] = " "
            index += 1
            continue
        elif state in {"string", "character"}:
            quote = '"' if state == "string" else "'"
            if char == "\\" and following:
                if char != "\n":
                    output[index] = " "
                if following != "\n":
                    output[index + 1] = " "
                index += 2
                continue
            if char == quote:
                output[index] = " "
                index += 1
                state = "code"
                continue
            if char != "\n":
                output[index] = " "
            index += 1
            continue
        index += 1
    return "".join(output)


def _matching_brace(code: str, opening: int) -> int | None:
    depth = 0
    for index in range(opening, len(code)):
        if code[index] == "{":
            depth += 1
        elif code[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _parse_c(path: str, text: str, state: ScanState) -> CUnit:
    includes: list[str] = []
    seen_includes: set[str] = set()
    for match in _INCLUDE_RE.finditer(_strip_c_comments(text)):
        header = match.group("header").strip()
        if header and header not in seen_includes:
            seen_includes.add(header)
            includes.append(header)
            if len(includes) >= MAX_IMPORTS_PER_FILE:
                state.truncate("per-file include limit")
                break

    code = _strip_c_noncode(text)
    functions: list[CFunction] = []
    cursor = 0
    while len(functions) < MAX_FUNCTIONS_PER_FILE:
        match = _C_FUNCTION_RE.search(code, cursor)
        if match is None:
            break
        name = match.group("name")
        prefix = match.group("prefix").strip()
        short_name = name.rsplit("::", 1)[-1].lstrip("~")
        opening = match.start("brace")
        closing = _matching_brace(code, opening)
        if closing is None:
            state.skipped["parse_error"] += 1
            state.truncate("unbalanced C or C++ body")
            break
        cursor = closing + 1
        if short_name in _C_NON_CALLS or (not prefix and "::" not in name):
            continue
        calls: list[str] = []
        seen_calls: set[str] = set()
        body = code[opening + 1 : closing]
        for call_match in _C_CALL_RE.finditer(body):
            call = call_match.group("name")
            call_short = call.rsplit("::", 1)[-1].lstrip("~")
            if call_short in _C_NON_CALLS or call in seen_calls:
                continue
            seen_calls.add(call)
            calls.append(call)
            if len(calls) >= MAX_CALLS_PER_SCOPE:
                state.truncate("per-scope call limit")
                break
        line = code.count("\n", 0, match.start("name")) + 1
        functions.append(CFunction(name=name, line=line, calls=calls))
    if (
        len(functions) >= MAX_FUNCTIONS_PER_FILE
        and _C_FUNCTION_RE.search(code, cursor) is not None
    ):
        state.truncate("per-file function limit")
    state.parsed_files += 1
    return CUnit(path=path, includes=includes, functions=functions)


def _file_key(path: str) -> str:
    return f"file:{path}"


def _py_function_key(unit: PyUnit, function: PyFunction) -> str:
    return f"python-function:{unit.path}:{function.qualname}:{function.line}"


def _c_function_key(unit: CUnit, function: CFunction) -> str:
    return f"c-function:{unit.path}:{function.name}:{function.line}"


def _external_module_key(module: str) -> str:
    return f"external-python:{module or '<relative>'}"


def _external_symbol_key(symbol: str) -> str:
    return f"external-python-symbol:{symbol}"


def _external_header_key(header: str) -> str:
    return f"external-header:{header}"


def _resolve_module(
    module: str, module_map: dict[str, str]
) -> tuple[str | None, str]:
    candidate = module
    while candidate:
        if candidate in module_map:
            return module_map[candidate], candidate
        candidate = candidate.rpartition(".")[0]
    return None, module


def _resolve_from_target(
    imported: PyImport, module_map: dict[str, str]
) -> tuple[str | None, str]:
    if imported.symbol and imported.symbol != "*":
        child = ".".join(part for part in (imported.module, imported.symbol) if part)
        if child in module_map:
            return module_map[child], child
    return _resolve_module(imported.module, module_map)


def _py_function_index(
    units: Sequence[PyUnit],
) -> dict[tuple[str, str], list[PyFunction]]:
    by_file_and_name: dict[tuple[str, str], list[PyFunction]] = defaultdict(list)
    for unit in units:
        for function in unit.functions:
            short = function.qualname.rsplit(".", 1)[-1]
            by_file_and_name[(unit.path, short)].append(function)
    return by_file_and_name


def _local_python_target(
    unit: PyUnit,
    current: PyFunction | None,
    call: str,
    by_file_and_name: dict[tuple[str, str], list[PyFunction]],
) -> PyFunction | None:
    parts = call.split(".")
    short = parts[-1]
    candidates = by_file_and_name.get((unit.path, short), [])
    if not candidates:
        return None
    if current is not None:
        current_parent = current.qualname.rpartition(".")[0]
        if parts[0] in {"self", "cls"} and current_parent:
            expected = f"{current_parent}.{short}"
            exact = [item for item in candidates if item.qualname == expected]
            if len(exact) == 1:
                return exact[0]
        same_scope = [
            item
            for item in candidates
            if item.qualname.rpartition(".")[0] == current_parent
        ]
        if len(same_scope) == 1:
            return same_scope[0]
    top_level = [item for item in candidates if "." not in item.qualname]
    if len(top_level) == 1:
        return top_level[0]
    return candidates[0] if len(candidates) == 1 else None


def _imported_python_target(
    unit: PyUnit,
    call: str,
    aliases: dict[str, PyImport],
    module_map: dict[str, str],
    units_by_path: dict[str, PyUnit],
    by_file_and_name: dict[tuple[str, str], list[PyFunction]],
) -> tuple[str | None, str | None]:
    parts = call.split(".")
    imported = aliases.get(parts[0])
    if imported is None or imported.local == "*":
        return None, None
    target_path, resolved_module = _resolve_from_target(imported, module_map)
    if imported.symbol and imported.symbol != "*":
        symbol = imported.symbol if len(parts) == 1 else parts[-1]
    elif len(parts) > 1:
        symbol = parts[-1]
    else:
        symbol = None
    display = ".".join(
        item
        for item in (resolved_module or imported.module, symbol)
        if item
    )
    if target_path is None or symbol is None:
        return None, display or call
    target_unit = units_by_path.get(target_path)
    if target_unit is None:
        return None, display or call
    candidates = by_file_and_name.get((target_unit.path, symbol), [])
    if len(candidates) == 1:
        return _py_function_key(target_unit, candidates[0]), None
    return None, display or call


def _resolve_include(
    unit_path: str,
    header: str,
    headers: set[str],
    header_suffix_map: dict[str, list[str]],
) -> str | None:
    normalized = posixpath.normpath(
        str(PurePosixPath(unit_path).parent / PurePosixPath(header))
    )
    if not normalized.startswith("../") and normalized in headers:
        return normalized
    direct = posixpath.normpath(header)
    if not direct.startswith("../") and direct in headers:
        return direct
    candidates = header_suffix_map.get(header, [])
    return candidates[0] if len(candidates) == 1 else None


def _build_graph(
    py_units: Sequence[PyUnit],
    c_units: Sequence[CUnit],
    all_paths: Sequence[str],
    module_map: dict[str, str],
    max_nodes: int,
    max_edges: int,
    state: ScanState,
) -> Graph:
    graph = Graph(max_nodes, max_edges, state)
    py_by_path = {unit.path: unit for unit in py_units}

    for path in sorted(all_paths, key=lambda item: (item.casefold(), item)):
        graph.add_node(_file_key(path), path)

    for unit in sorted(py_units, key=lambda item: (item.path.casefold(), item.path)):
        for function in sorted(
            unit.functions, key=lambda item: (item.line, item.qualname)
        ):
            key = _py_function_key(unit, function)
            if graph.add_node(key, f"{unit.path} :: {function.qualname}()"):
                graph.add_edge(_file_key(unit.path), key, "defines")
    for unit in sorted(c_units, key=lambda item: (item.path.casefold(), item.path)):
        for function in sorted(unit.functions, key=lambda item: (item.line, item.name)):
            key = _c_function_key(unit, function)
            if graph.add_node(key, f"{unit.path} :: {function.name}()"):
                graph.add_edge(_file_key(unit.path), key, "defines")

    py_by_file_name = _py_function_index(py_units)
    for unit in sorted(py_units, key=lambda item: (item.path.casefold(), item.path)):
        aliases: dict[str, PyImport] = {}
        for imported in unit.imports:
            aliases.setdefault(imported.local, imported)
            target_path, display_module = _resolve_from_target(imported, module_map)
            if target_path is not None:
                graph.add_edge(
                    _file_key(unit.path), _file_key(target_path), "imports"
                )
            else:
                target_key = _external_module_key(display_module or imported.module)
                if graph.add_node(
                    target_key,
                    f"external Python :: {display_module or imported.module or 'relative'}",
                ):
                    graph.add_edge(_file_key(unit.path), target_key, "imports")

        call_scopes: list[tuple[PyFunction | None, list[str], str]] = [
            (None, unit.module_calls, _file_key(unit.path))
        ]
        call_scopes.extend(
            (function, function.calls, _py_function_key(unit, function))
            for function in unit.functions
        )
        for current, calls, source_key in call_scopes:
            for call in sorted(set(calls), key=lambda item: (item.casefold(), item)):
                if "." not in call and call in _PY_BUILTINS:
                    continue
                local = _local_python_target(unit, current, call, py_by_file_name)
                if local is not None:
                    graph.add_edge(
                        source_key, _py_function_key(unit, local), "calls"
                    )
                    continue
                target_key, external = _imported_python_target(
                    unit,
                    call,
                    aliases,
                    module_map,
                    py_by_path,
                    py_by_file_name,
                )
                if target_key is not None:
                    graph.add_edge(source_key, target_key, "calls")
                elif external:
                    external_key = _external_symbol_key(external)
                    if graph.add_node(
                        external_key, f"external Python call :: {external}"
                    ):
                        graph.add_edge(source_key, external_key, "calls")

    headers = {
        path for path in all_paths if PurePosixPath(path).suffix.casefold() in _HEADER_SUFFIXES
    }
    header_suffix_map: dict[str, list[str]] = defaultdict(list)
    for path in sorted(headers):
        parts = PurePosixPath(path).parts
        for start in range(len(parts)):
            header_suffix_map["/".join(parts[start:])].append(path)

    c_by_short: dict[str, list[tuple[CUnit, CFunction]]] = defaultdict(list)
    c_by_file_short: dict[tuple[str, str], list[CFunction]] = defaultdict(list)
    for unit in c_units:
        for function in unit.functions:
            c_by_short[function.short_name].append((unit, function))
            c_by_file_short[(unit.path, function.short_name)].append(function)

    for unit in sorted(c_units, key=lambda item: (item.path.casefold(), item.path)):
        for header in sorted(set(unit.includes), key=lambda item: (item.casefold(), item)):
            target_path = _resolve_include(
                unit.path, header, headers, header_suffix_map
            )
            if target_path is not None:
                graph.add_edge(
                    _file_key(unit.path), _file_key(target_path), "includes"
                )
            else:
                target_key = _external_header_key(header)
                if graph.add_node(target_key, f"external header :: {header}"):
                    graph.add_edge(_file_key(unit.path), target_key, "includes")

        for function in unit.functions:
            source_key = _c_function_key(unit, function)
            for call in sorted(
                set(function.calls), key=lambda item: (item.casefold(), item)
            ):
                short = call.rsplit("::", 1)[-1].lstrip("~")
                if short == function.short_name:
                    graph.add_edge(source_key, source_key, "calls")
                    continue
                local = c_by_file_short.get((unit.path, short), [])
                if len(local) == 1:
                    graph.add_edge(
                        source_key, _c_function_key(unit, local[0]), "calls"
                    )
                    continue
                global_targets = c_by_short.get(short, [])
                if len(global_targets) == 1:
                    target_unit, target_function = global_targets[0]
                    graph.add_edge(
                        source_key,
                        _c_function_key(target_unit, target_function),
                        "calls",
                    )
    return graph


def _stable_ids(keys: Sequence[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    occupied: dict[str, str] = {}
    for key in sorted(keys):
        digest = hashlib.sha256(key.encode("utf-8", errors="surrogatepass")).hexdigest()
        length = 16
        identifier = f"n_{digest[:length]}"
        while identifier in occupied and occupied[identifier] != key:
            length += 2
            if length <= len(digest):
                identifier = f"n_{digest[:length]}"
            else:
                identifier = f"n_{digest}_{len(occupied)}"
        occupied[identifier] = key
        result[key] = identifier
    return result


def _render_mermaid(graph: Graph, state: ScanState) -> str:
    identifiers = _stable_ids(tuple(graph.nodes))
    lines = ["flowchart LR"]
    lines.append(
        "  %% "
        f"files={state.discovered_files} parsed={state.parsed_files} "
        f"bytes={state.scanned_bytes} errors={state.error_count}"
    )
    for key in sorted(
        graph.nodes,
        key=lambda item: (
            graph.nodes[item].label.casefold(),
            graph.nodes[item].label,
            item,
        ),
    ):
        node = graph.nodes[key]
        lines.append(f'  {identifiers[key]}["{_mermaid_label(node.label)}"]')
    for edge in sorted(
        graph.edges,
        key=lambda item: (
            graph.nodes[item.source].label.casefold(),
            graph.nodes[item.target].label.casefold(),
            item.label,
            item.source,
            item.target,
        ),
    ):
        lines.append(
            f"  {identifiers[edge.source]} -->|{edge.label}| "
            f"{identifiers[edge.target]}"
        )
    if state.truncation_reasons:
        reasons = ", ".join(sorted(state.truncation_reasons))
        lines.append(
            f'  graph_truncated["{_mermaid_label(f"TRUNCATED :: {reasons}")}"]'
        )
    return "\n".join(lines)


def map_repository(
    root: Path,
    *,
    max_files: int,
    max_file_bytes: int,
    max_nodes: int,
    max_edges: int,
) -> tuple[str, ScanState]:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("repository root must be a directory")
    state = ScanState()
    paths = list(_iter_source_files(root, state, max_files))
    relative_paths = [path.relative_to(root).as_posix() for path in paths]
    module_map: dict[str, str] = {}
    for relative in relative_paths:
        if PurePosixPath(relative).suffix.casefold() in _PYTHON_SUFFIXES:
            module, _ = _module_for_path(relative)
            if module:
                module_map.setdefault(module, relative)

    py_units: list[PyUnit] = []
    c_units: list[CUnit] = []
    for path, relative in zip(paths, relative_paths):
        text = _read_text(path, root, max_file_bytes, state)
        if text is None:
            continue
        suffix = path.suffix.casefold()
        if suffix in _PYTHON_SUFFIXES:
            module, is_package = _module_for_path(relative)
            unit = _parse_python(relative, text, module, is_package, state)
            if unit is not None:
                py_units.append(unit)
        else:
            c_units.append(_parse_c(relative, text, state))

    parsed_paths = sorted(
        {unit.path for unit in py_units} | {unit.path for unit in c_units},
        key=lambda item: (item.casefold(), item),
    )
    graph = _build_graph(
        py_units,
        c_units,
        parsed_paths,
        module_map,
        max_nodes,
        max_edges,
        state,
    )
    return _render_mermaid(graph, state), state


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    max_files = _bounded(parser, "--max-files", args.max_files, MAX_FILES)
    max_file_bytes = _bounded(
        parser, "--max-file-bytes", args.max_file_bytes, MAX_FILE_BYTES
    )
    max_nodes = _bounded(parser, "--max-nodes", args.max_nodes, MAX_NODES)
    max_edges = _bounded(parser, "--max-edges", args.max_edges, MAX_EDGES)
    root = _resolve_root(args.root, parser)
    mermaid, _ = map_repository(
        root,
        max_files=max_files,
        max_file_bytes=max_file_bytes,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
    try:
        sys.stdout.write(mermaid + "\n")
    except BrokenPipeError:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
