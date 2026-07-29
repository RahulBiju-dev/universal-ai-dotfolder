#!/usr/bin/env python3
"""Compile trusted C sources and audit the binary with bounded Valgrind."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from contextlib import ExitStack
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

try:
    import resource
except ImportError:
    resource = None


EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2
EXIT_COMPILE_FAILED = 3
EXIT_TOOL_MISSING = 4
EXIT_TIMEOUT = 5
EXIT_ANALYSIS_FAILED = 6
EXIT_TARGET_FAILED = 7

VALGRIND_ERROR_EXIT = 97
MAX_TIMEOUT_SECONDS = 600.0
MIN_OUTPUT_BYTES = 1_024
MAX_OUTPUT_BYTES = 16 * 1024 * 1024
MAX_INPUT_BYTES = 1024 * 1024 * 1024
CHILD_FILE_LIMIT_BYTES = 64 * 1024 * 1024

DEFINE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:=[^\x00\r\n]*)?$")
LIBRARY_RE = re.compile(r"^[A-Za-z0-9_+.-]+$")
LEAK_KIND_LABELS = {
    "Leak_DefinitelyLost": "definitely lost",
    "Leak_IndirectlyLost": "indirectly lost",
    "Leak_PossiblyLost": "possibly lost",
    "Leak_StillReachable": "still reachable",
}
LEAK_ORDER = {
    "definitely lost": 0,
    "indirectly lost": 1,
    "possibly lost": 2,
    "still reachable": 3,
}


class AuditInputError(ValueError):
    """Raised when a requested audit would escape its declared workspace."""


@dataclass(frozen=True)
class CapturedText:
    text: str
    total_bytes: int
    truncated_bytes: int


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    duration_seconds: float
    timed_out: bool
    stdout: CapturedText
    stderr: CapturedText

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _positive_timeout(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number") from exc
    if not math.isfinite(parsed) or parsed <= 0 or parsed > MAX_TIMEOUT_SECONDS:
        raise argparse.ArgumentTypeError(
            f"timeout must be greater than 0 and at most {MAX_TIMEOUT_SECONDS:g}"
        )
    return parsed


def _bounded_output_size(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("output limit must be an integer") from exc
    if parsed < MIN_OUTPUT_BYTES or parsed > MAX_OUTPUT_BYTES:
        raise argparse.ArgumentTypeError(
            f"output limit must be between {MIN_OUTPUT_BYTES} and {MAX_OUTPUT_BYTES}"
        )
    return parsed


def _bounded_input_size(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("input limit must be an integer") from exc
    if parsed < 0 or parsed > MAX_INPUT_BYTES:
        raise argparse.ArgumentTypeError(
            f"input limit must be between 0 and {MAX_INPUT_BYTES}"
        )
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compile explicit workspace C sources, execute the binary under "
            "Valgrind Memcheck, and emit a bounded evidence report."
        ),
        epilog=(
            "Exit codes: 0 clean, 1 findings, 2 invalid input, 3 compile failure, "
            "4 tool missing, 5 timeout, 6 analysis failure, 7 target failure. "
            "The compiled target is trusted code: this wrapper is not a sandbox."
        ),
    )
    parser.add_argument("sources", nargs="+", metavar="SOURCE", help="C source inside ROOT")
    parser.add_argument(
        "--root",
        default=".",
        help="workspace root used for containment and execution (default: current directory)",
    )
    parser.add_argument(
        "-I",
        "--include",
        action="append",
        default=[],
        metavar="DIR",
        help="workspace-contained include directory; repeat as needed",
    )
    parser.add_argument(
        "-D",
        "--define",
        action="append",
        default=[],
        metavar="NAME[=VALUE]",
        help="preprocessor definition; repeat as needed",
    )
    parser.add_argument(
        "-L",
        "--library-dir",
        action="append",
        default=[],
        metavar="DIR",
        help="workspace-contained library directory; repeat as needed",
    )
    parser.add_argument(
        "-l",
        "--library",
        action="append",
        default=[],
        metavar="NAME",
        help="link library by name; repeat as needed",
    )
    parser.add_argument(
        "--arg",
        action="append",
        default=[],
        metavar="VALUE",
        help="single target-program argument; use --arg=-x for leading dashes",
    )
    parser.add_argument(
        "--input",
        "--stdin",
        dest="input_path",
        metavar="FILE",
        help="workspace-contained file connected to target stdin",
    )
    parser.add_argument(
        "--compiler",
        default="cc",
        metavar="EXECUTABLE",
        help="C compiler executable or command name (default: cc)",
    )
    parser.add_argument(
        "--valgrind",
        default="valgrind",
        metavar="EXECUTABLE",
        help="Valgrind executable or command name (default: valgrind)",
    )
    parser.add_argument(
        "--std",
        choices=("c89", "c90", "c99", "c11", "c17", "c18", "c2x", "c23"),
        default="c17",
        help="C language standard (default: c17)",
    )
    parser.add_argument(
        "--compile-timeout",
        type=_positive_timeout,
        default=30.0,
        metavar="SECONDS",
        help="compiler wall-clock limit, at most 600 seconds (default: 30)",
    )
    parser.add_argument(
        "--run-timeout",
        type=_positive_timeout,
        default=30.0,
        metavar="SECONDS",
        help="Valgrind and target wall-clock limit, at most 600 seconds (default: 30)",
    )
    parser.add_argument(
        "--max-output-bytes",
        type=_bounded_output_size,
        default=64 * 1024,
        metavar="BYTES",
        help="captured byte limit per stdout/stderr stream (default: 65536)",
    )
    parser.add_argument(
        "--max-input-bytes",
        type=_bounded_input_size,
        default=16 * 1024 * 1024,
        metavar="BYTES",
        help="maximum accepted stdin-file size (default: 16777216)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit stable JSON instead of Markdown",
    )
    return parser


def _resolve_root(raw: str) -> Path:
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise AuditInputError(f"workspace root is unavailable: {raw}") from exc
    if not root.is_dir():
        raise AuditInputError(f"workspace root is not a directory: {raw}")
    return root


def _inside_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _workspace_path(raw: str, root: Path, expected: str) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise AuditInputError(f"{expected} is unavailable: {raw}") from exc
    if not _inside_root(resolved, root):
        raise AuditInputError(f"{expected} escapes workspace root: {raw}")
    if expected == "file" and not resolved.is_file():
        raise AuditInputError(f"expected a regular file: {raw}")
    if expected == "directory" and not resolved.is_dir():
        raise AuditInputError(f"expected a directory: {raw}")
    return resolved


def _resolve_sources(raw_sources: Sequence[str], root: Path) -> list[Path]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    for raw in raw_sources:
        source = _workspace_path(raw, root, "file")
        if source.suffix.lower() != ".c":
            raise AuditInputError(f"source must have a .c extension: {raw}")
        if source not in seen:
            resolved.append(source)
            seen.add(source)
    if not resolved:
        raise AuditInputError("at least one unique C source is required")
    return resolved


def _validate_defines(defines: Sequence[str]) -> list[str]:
    invalid = [value for value in defines if not DEFINE_RE.fullmatch(value)]
    if invalid:
        raise AuditInputError(f"invalid preprocessor definition: {invalid[0]}")
    return list(defines)


def _validate_libraries(libraries: Sequence[str]) -> list[str]:
    invalid = [
        value
        for value in libraries
        if not LIBRARY_RE.fullmatch(value) or value.startswith(("-", "."))
    ]
    if invalid:
        raise AuditInputError(f"invalid library name: {invalid[0]}")
    return list(libraries)


def _resolve_tool(raw: str) -> Path | None:
    if "\x00" in raw or "\r" in raw or "\n" in raw:
        return None
    candidate: str | None
    if os.sep in raw or (os.altsep and os.altsep in raw):
        path = Path(raw).expanduser()
        try:
            resolved = path.resolve(strict=True)
        except (OSError, RuntimeError):
            return None
        candidate = str(resolved)
    else:
        candidate = shutil.which(raw)
    if candidate is None:
        return None
    path = Path(candidate)
    if not path.is_file() or not os.access(path, os.X_OK):
        return None
    return path.resolve()


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _controlled_environment(temp_dir: Path, library_dirs: Sequence[Path]) -> dict[str, str]:
    environment = {
        "PATH": os.environ.get("PATH", os.defpath),
        "HOME": str(temp_dir),
        "TMPDIR": str(temp_dir),
        "LANG": "C",
        "LC_ALL": "C",
        "TERM": "dumb",
    }
    if library_dirs:
        environment["LD_LIBRARY_PATH"] = os.pathsep.join(str(path) for path in library_dirs)
    return environment


def _resource_limiter(timeout: float) -> Callable[[], None] | None:
    if resource is None:
        return None

    def limit() -> None:
        requested = (
            (resource.RLIMIT_CORE, 0),
            (resource.RLIMIT_CPU, max(1, math.ceil(timeout) + 1)),
            (resource.RLIMIT_FSIZE, CHILD_FILE_LIMIT_BYTES),
            (resource.RLIMIT_NOFILE, 256),
        )
        for resource_id, desired in requested:
            try:
                current_soft, current_hard = resource.getrlimit(resource_id)
                hard_cap = desired if current_hard == resource.RLIM_INFINITY else current_hard
                target = min(desired, hard_cap)
                resource.setrlimit(resource_id, (target, hard_cap))
            except (OSError, ValueError):
                continue

    return limit


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=0.5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            return


def _stop_remaining_children(group_id: int) -> None:
    try:
        os.killpg(group_id, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 0.25
    while time.monotonic() < deadline:
        try:
            os.killpg(group_id, 0)
        except ProcessLookupError:
            return
        time.sleep(0.025)
    try:
        os.killpg(group_id, signal.SIGKILL)
    except ProcessLookupError:
        return


def _read_capped(stream: Any, limit: int) -> CapturedText:
    stream.flush()
    stream.seek(0, os.SEEK_END)
    total = stream.tell()
    stream.seek(0)
    if total <= limit:
        payload = stream.read()
        truncated = 0
    else:
        head_size = max(1, (limit * 2) // 3)
        tail_size = max(0, limit - head_size)
        head = stream.read(head_size)
        stream.seek(max(0, total - tail_size))
        tail = stream.read(tail_size)
        omitted = total - head_size - tail_size
        marker = f"\n[truncated {omitted} bytes]\n".encode("ascii")
        payload = head + marker + tail
        truncated = omitted
    return CapturedText(
        text=payload.decode("utf-8", errors="replace").rstrip(),
        total_bytes=total,
        truncated_bytes=truncated,
    )


def _run_bounded(
    command: Sequence[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout: float,
    output_limit: int,
    capture_dir: Path,
    stdin_path: Path | None = None,
) -> ProcessResult:
    started = time.monotonic()
    with ExitStack() as stack:
        stdout_file = stack.enter_context(tempfile.TemporaryFile(mode="w+b", dir=capture_dir))
        stderr_file = stack.enter_context(tempfile.TemporaryFile(mode="w+b", dir=capture_dir))
        if stdin_path is None:
            stdin_stream: Any = subprocess.DEVNULL
        else:
            stdin_stream = stack.enter_context(stdin_path.open("rb"))
        process = subprocess.Popen(
            list(command),
            cwd=str(cwd),
            env=environment,
            stdin=stdin_stream,
            stdout=stdout_file,
            stderr=stderr_file,
            start_new_session=True,
            preexec_fn=_resource_limiter(timeout),
        )
        timed_out = False
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _terminate_process_group(process)
            returncode = process.returncode
            if returncode is None:
                returncode = -signal.SIGKILL
        _stop_remaining_children(process.pid)
        duration = time.monotonic() - started
        stdout = _read_capped(stdout_file, output_limit)
        stderr = _read_capped(stderr_file, output_limit)
    return ProcessResult(
        returncode=returncode,
        duration_seconds=round(duration, 3),
        timed_out=timed_out,
        stdout=stdout,
        stderr=stderr,
    )


def _integer(element: ET.Element | None, path: str, default: int = 0) -> int:
    if element is None:
        return default
    text = element.findtext(path)
    try:
        return int(text) if text is not None else default
    except ValueError:
        return default


def _frame_path(frame: ET.Element, root: Path) -> dict[str, Any]:
    directory = frame.findtext("dir") or ""
    filename = frame.findtext("file") or ""
    line = _integer(frame, "line")
    display_path = ""
    in_workspace = False
    if filename:
        joined = Path(directory) / filename if directory else Path(filename)
        try:
            resolved = joined.resolve(strict=False)
        except (OSError, RuntimeError):
            resolved = joined
        if resolved.is_absolute() and _inside_root(resolved, root):
            display_path = _relative(resolved, root)
            in_workspace = True
        else:
            display_path = joined.as_posix()
    return {
        "instruction_pointer": frame.findtext("ip") or "",
        "object": frame.findtext("obj") or "",
        "function": frame.findtext("fn") or "",
        "directory": directory,
        "file": filename,
        "line": line,
        "path": display_path,
        "workspace": in_workspace,
    }


def _parse_stack(stack: ET.Element | None, root: Path) -> list[dict[str, Any]]:
    if stack is None:
        return []
    return [_frame_path(frame, root) for frame in stack.findall("frame")]


def _location(frames: Sequence[dict[str, Any]]) -> tuple[str, bool]:
    for frame in frames:
        if frame["workspace"] and frame["path"] and frame["line"] > 0:
            function = f" in {frame['function']}" if frame["function"] else ""
            return f"{frame['path']}:{frame['line']}{function}", True
    for frame in frames:
        if frame["path"] and frame["line"] > 0:
            function = f" in {frame['function']}" if frame["function"] else ""
            return f"{frame['path']}:{frame['line']}{function}", True
    for frame in frames:
        if frame["function"] or frame["object"]:
            function = frame["function"] or "unknown function"
            source = f" ({frame['object']})" if frame["object"] else ""
            return f"debug location unavailable; nearest frame {function}{source}", False
    return "debug location unavailable", False


def _error_occurrences(document: ET.Element) -> dict[str, int]:
    counts: dict[str, int] = {}
    for pair in document.findall("./errorcounts/pair"):
        unique = pair.findtext("unique") or ""
        count = _integer(pair, "count")
        if unique:
            counts[unique] = count
    return counts


def _suppression_counts(document: ET.Element) -> dict[str, int]:
    counts: dict[str, int] = {}
    for pair in document.findall("./suppcounts/pair"):
        name = pair.findtext("name") or "unnamed"
        counts[name] = counts.get(name, 0) + _integer(pair, "count")
    return dict(sorted(counts.items()))


def _parse_valgrind_xml(xml_path: Path, root: Path) -> dict[str, Any]:
    try:
        size = xml_path.stat().st_size
    except OSError as exc:
        raise RuntimeError("Valgrind did not create an XML report") from exc
    if size == 0:
        raise RuntimeError("Valgrind created an empty XML report")
    if size > CHILD_FILE_LIMIT_BYTES:
        raise RuntimeError("Valgrind XML report exceeded the safety limit")
    try:
        document = ET.parse(xml_path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise RuntimeError("Valgrind XML report is incomplete or invalid") from exc
    if document.tag != "valgrindoutput":
        raise RuntimeError("unexpected Valgrind XML root element")
    protocol_tool = document.findtext("protocoltool") or ""
    if protocol_tool != "memcheck":
        raise RuntimeError(f"unexpected Valgrind protocol tool: {protocol_tool or 'missing'}")

    occurrence_map = _error_occurrences(document)
    leak_totals = {
        label: {"records": 0, "occurrences": 0, "blocks": 0, "bytes": 0}
        for label in LEAK_KIND_LABELS.values()
    }
    loss_records: list[dict[str, Any]] = []
    memory_errors: list[dict[str, Any]] = []

    for error in document.findall("error"):
        unique = error.findtext("unique") or ""
        kind = error.findtext("kind") or "Unknown"
        occurrences = occurrence_map.get(unique, 1)
        frames = _parse_stack(error.find("stack"), root)
        location, location_precise = _location(frames)
        if kind in LEAK_KIND_LABELS:
            xwhat = error.find("xwhat")
            leaked_bytes = _integer(xwhat, "leakedbytes")
            leaked_blocks = _integer(xwhat, "leakedblocks")
            detail = (
                xwhat.findtext("text")
                if xwhat is not None
                else error.findtext("what")
            ) or kind
            label = LEAK_KIND_LABELS[kind]
            totals = leak_totals[label]
            totals["records"] += 1
            totals["occurrences"] += occurrences
            totals["blocks"] += leaked_blocks
            totals["bytes"] += leaked_bytes
            loss_records.append(
                {
                    "id": unique,
                    "kind": label,
                    "occurrences": occurrences,
                    "blocks": leaked_blocks,
                    "bytes": leaked_bytes,
                    "detail": detail,
                    "location": location,
                    "location_precise": location_precise,
                    "frames": frames,
                }
            )
        else:
            detail = error.findtext("what") or kind
            auxiliary = [
                value.strip()
                for value in (node.text for node in error.findall("auxwhat"))
                if value and value.strip()
            ]
            memory_errors.append(
                {
                    "id": unique,
                    "kind": kind,
                    "occurrences": occurrences,
                    "detail": detail,
                    "auxiliary": auxiliary,
                    "location": location,
                    "location_precise": location_precise,
                    "frames": frames,
                }
            )

    loss_records.sort(
        key=lambda record: (
            LEAK_ORDER.get(record["kind"], 99),
            record["location"],
            record["id"],
        )
    )
    memory_errors.sort(
        key=lambda record: (record["kind"], record["location"], record["id"])
    )

    fatal_signal: dict[str, Any] | None = None
    fatal = document.find("fatal_signal")
    if fatal is not None:
        frames = _parse_stack(fatal.find("stack"), root)
        location, location_precise = _location(frames)
        fatal_signal = {
            "number": _integer(fatal, "signo"),
            "name": fatal.findtext("signame") or "",
            "code": fatal.findtext("sicode") or "",
            "location": location,
            "location_precise": location_precise,
            "frames": frames,
        }

    states = [
        {
            "state": status.findtext("state") or "",
            "time": status.findtext("time") or "",
        }
        for status in document.findall("status")
    ]
    finished = any(status["state"] == "FINISHED" for status in states)
    error_occurrences = sum(occurrence_map.values())
    if not occurrence_map:
        error_occurrences = sum(
            record["occurrences"] for record in loss_records + memory_errors
        )

    return {
        "protocol_version": document.findtext("protocolversion") or "",
        "states": states,
        "finished": finished,
        "error_occurrences": error_occurrences,
        "suppression_counts": _suppression_counts(document),
        "leak_totals": leak_totals,
        "loss_records": loss_records,
        "memory_errors": memory_errors,
        "fatal_signal": fatal_signal,
    }


def _has_findings(analysis: dict[str, Any]) -> bool:
    actionable_leaks = ("definitely lost", "indirectly lost", "possibly lost")
    leaked = any(analysis["leak_totals"][kind]["bytes"] > 0 for kind in actionable_leaks)
    return bool(leaked or analysis["memory_errors"] or analysis["fatal_signal"])


def _report_base(root: Path, sources: Sequence[Path]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "pending",
        "exit_code": EXIT_ANALYSIS_FAILED,
        "root": str(root),
        "sources": [_relative(source, root) for source in sources],
        "safety": (
            "The compiled target executes with workspace access. Time and resource "
            "limits reduce impact but do not provide a sandbox."
        ),
    }


def _failure_report(
    status: str,
    exit_code: int,
    message: str,
    *,
    root: Path | None = None,
    sources: Sequence[Path] = (),
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": status,
        "exit_code": exit_code,
        "message": message,
    }
    if root is not None:
        report["root"] = str(root)
        report["sources"] = [_relative(source, root) for source in sources]
    return report


def _md_cell(value: Any) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ")
    return text.replace("|", "\\|").strip()


def _indented_block(text: str) -> str:
    return "\n".join(f"    {line}" for line in text.splitlines()) or "    (empty)"


def _render_process_output(
    lines: list[str], heading: str, process: dict[str, Any]
) -> None:
    for stream_name in ("stdout", "stderr"):
        stream = process[stream_name]
        if not stream["text"]:
            continue
        lines.extend(
            [
                f"### {heading} {stream_name}",
                "",
                _indented_block(stream["text"]),
                "",
            ]
        )
        if stream["truncated_bytes"]:
            lines.append(
                f"Captured output omitted {stream['truncated_bytes']} bytes."
            )
            lines.append("")


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# C Memory Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Exit code: `{report['exit_code']}`",
    ]
    if report.get("sources"):
        lines.append(f"- Sources: {', '.join(f'`{source}`' for source in report['sources'])}")
    if report.get("message"):
        lines.extend(["", f"**Result:** {_md_cell(report['message'])}"])
    if report.get("safety"):
        lines.extend(["", f"**Safety boundary:** {_md_cell(report['safety'])}"])

    build = report.get("build")
    if build:
        lines.extend(
            [
                "",
                "## Build",
                "",
                f"- Compiler: `{_md_cell(build['compiler'])}`",
                f"- Process exit: `{build['process']['returncode']}`",
                f"- Duration: `{build['process']['duration_seconds']:.3f}s`",
            ]
        )
        _render_process_output(lines, "compiler", build["process"])

    execution = report.get("execution")
    if execution:
        process = execution["process"]
        lines.extend(
            [
                "",
                "## Valgrind execution",
                "",
                f"- Valgrind: `{_md_cell(execution['valgrind'])}`",
                f"- Process exit: `{process['returncode']}`",
                f"- Duration: `{process['duration_seconds']:.3f}s`",
            ]
        )
        analysis = execution.get("analysis")
        if analysis:
            lines.extend(
                [
                    f"- Error occurrences: `{analysis['error_occurrences']}`",
                    "",
                    "### Leak summary",
                    "",
                    "| Kind | Records | Occurrences | Blocks | Bytes |",
                    "|---|---:|---:|---:|---:|",
                ]
            )
            for kind in sorted(analysis["leak_totals"], key=lambda item: LEAK_ORDER[item]):
                totals = analysis["leak_totals"][kind]
                lines.append(
                    f"| {kind} | {totals['records']} | {totals['occurrences']} | "
                    f"{totals['blocks']} | {totals['bytes']} |"
                )

            records = analysis["loss_records"]
            lines.extend(
                [
                    "",
                    "### Loss records",
                    "",
                ]
            )
            if records:
                lines.extend(
                    [
                        "| Kind | Bytes | Blocks | Occurrences | Location | Detail |",
                        "|---|---:|---:|---:|---|---|",
                    ]
                )
                for record in records:
                    lines.append(
                        f"| {_md_cell(record['kind'])} | {record['bytes']} | "
                        f"{record['blocks']} | {record['occurrences']} | "
                        f"{_md_cell(record['location'])} | {_md_cell(record['detail'])} |"
                    )
            else:
                lines.append("No loss records.")

            errors = analysis["memory_errors"]
            lines.extend(["", "### Memory errors", ""])
            if errors:
                lines.extend(
                    [
                        "| Kind | Occurrences | Location | Detail |",
                        "|---|---:|---|---|",
                    ]
                )
                for error in errors:
                    lines.append(
                        f"| {_md_cell(error['kind'])} | {error['occurrences']} | "
                        f"{_md_cell(error['location'])} | {_md_cell(error['detail'])} |"
                    )
            else:
                lines.append("No non-leak memory errors.")

            fatal = analysis.get("fatal_signal")
            if fatal:
                signal_name = fatal["name"] or str(fatal["number"])
                lines.extend(
                    [
                        "",
                        "### Fatal signal",
                        "",
                        f"- Signal: `{_md_cell(signal_name)}`",
                        f"- Location: {_md_cell(fatal['location'])}",
                    ]
                )
            suppressions = analysis["suppression_counts"]
            if suppressions:
                lines.extend(["", "### Suppressions", ""])
                for name, count in suppressions.items():
                    lines.append(f"- `{_md_cell(name)}`: {count}")
        _render_process_output(lines, "target/Valgrind", process)
    return "\n".join(lines).rstrip() + "\n"


def _emit(report: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        sys.stdout.write(_render_markdown(report))


def _main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root: Path | None = None
    sources: list[Path] = []
    try:
        root = _resolve_root(args.root)
        sources = _resolve_sources(args.sources, root)
        includes = [_workspace_path(value, root, "directory") for value in args.include]
        library_dirs = [
            _workspace_path(value, root, "directory") for value in args.library_dir
        ]
        defines = _validate_defines(args.define)
        libraries = _validate_libraries(args.library)
        input_path = (
            _workspace_path(args.input_path, root, "file")
            if args.input_path
            else None
        )
        if input_path is not None and input_path.stat().st_size > args.max_input_bytes:
            raise AuditInputError(
                f"stdin file exceeds {args.max_input_bytes} bytes: "
                f"{_relative(input_path, root)}"
            )
    except (AuditInputError, OSError) as exc:
        report = _failure_report(
            "invalid_input",
            EXIT_USAGE,
            str(exc),
            root=root,
            sources=sources,
        )
        _emit(report, args.json)
        return EXIT_USAGE

    compiler = _resolve_tool(args.compiler)
    if compiler is None:
        report = _failure_report(
            "tool_missing",
            EXIT_TOOL_MISSING,
            f"compiler is unavailable or not executable: {args.compiler}",
            root=root,
            sources=sources,
        )
        _emit(report, args.json)
        return EXIT_TOOL_MISSING
    valgrind = _resolve_tool(args.valgrind)
    if valgrind is None:
        report = _failure_report(
            "tool_missing",
            EXIT_TOOL_MISSING,
            f"Valgrind is unavailable or not executable: {args.valgrind}",
            root=root,
            sources=sources,
        )
        _emit(report, args.json)
        return EXIT_TOOL_MISSING

    with tempfile.TemporaryDirectory(prefix="mem-leak-audit-") as raw_build_dir:
        build_dir = Path(raw_build_dir)
        executable = build_dir / "audit-target"
        xml_path = build_dir / "valgrind.xml"
        environment = _controlled_environment(build_dir, library_dirs)
        compile_command = [
            str(compiler),
            f"-std={args.std}",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-g3",
            "-O0",
            "-fno-omit-frame-pointer",
        ]
        for include in includes:
            compile_command.extend(("-I", str(include)))
        compile_command.extend(f"-D{value}" for value in defines)
        compile_command.extend(str(source) for source in sources)
        for directory in library_dirs:
            compile_command.extend(("-L", str(directory)))
        compile_command.extend(("-o", str(executable)))
        compile_command.extend(f"-l{library}" for library in libraries)

        try:
            compile_result = _run_bounded(
                compile_command,
                cwd=root,
                environment=environment,
                timeout=args.compile_timeout,
                output_limit=args.max_output_bytes,
                capture_dir=build_dir,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            report = _failure_report(
                "compile_failed",
                EXIT_COMPILE_FAILED,
                f"compiler could not start: {exc}",
                root=root,
                sources=sources,
            )
            _emit(report, args.json)
            return EXIT_COMPILE_FAILED

        report = _report_base(root, sources)
        report["build"] = {
            "compiler": str(compiler),
            "process": compile_result.to_dict(),
        }
        if compile_result.timed_out:
            report.update(
                status="timeout",
                exit_code=EXIT_TIMEOUT,
                message=f"compilation exceeded {args.compile_timeout:g} seconds",
            )
            _emit(report, args.json)
            return EXIT_TIMEOUT
        if compile_result.returncode != 0 or not executable.is_file():
            report.update(
                status="compile_failed",
                exit_code=EXIT_COMPILE_FAILED,
                message="compilation failed; Valgrind was not started",
            )
            _emit(report, args.json)
            return EXIT_COMPILE_FAILED

        valgrind_command = [
            str(valgrind),
            "--tool=memcheck",
            "--leak-check=full",
            "--show-leak-kinds=all",
            "--errors-for-leak-kinds=definite,indirect,possible",
            "--track-origins=yes",
            "--num-callers=40",
            "--error-limit=no",
            "--xml=yes",
            f"--xml-file={xml_path}",
            f"--error-exitcode={VALGRIND_ERROR_EXIT}",
            str(executable),
            *args.arg,
        ]
        try:
            execution_result = _run_bounded(
                valgrind_command,
                cwd=root,
                environment=environment,
                timeout=args.run_timeout,
                output_limit=args.max_output_bytes,
                capture_dir=build_dir,
                stdin_path=input_path,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            report.update(
                status="analysis_failed",
                exit_code=EXIT_ANALYSIS_FAILED,
                message=f"Valgrind could not start: {exc}",
            )
            _emit(report, args.json)
            return EXIT_ANALYSIS_FAILED

        report["execution"] = {
            "valgrind": str(valgrind),
            "process": execution_result.to_dict(),
        }
        if execution_result.timed_out:
            report.update(
                status="timeout",
                exit_code=EXIT_TIMEOUT,
                message=f"Valgrind execution exceeded {args.run_timeout:g} seconds",
            )
            _emit(report, args.json)
            return EXIT_TIMEOUT
        try:
            analysis = _parse_valgrind_xml(xml_path, root)
        except RuntimeError as exc:
            report.update(
                status="analysis_failed",
                exit_code=EXIT_ANALYSIS_FAILED,
                message=str(exc),
            )
            _emit(report, args.json)
            return EXIT_ANALYSIS_FAILED
        report["execution"]["analysis"] = analysis
        if not analysis["finished"]:
            report.update(
                status="analysis_failed",
                exit_code=EXIT_ANALYSIS_FAILED,
                message="Valgrind XML does not contain a finished analysis state",
            )
            _emit(report, args.json)
            return EXIT_ANALYSIS_FAILED
        if _has_findings(analysis):
            report.update(
                status="findings",
                exit_code=EXIT_FINDINGS,
                message="Valgrind reported actionable leaks or memory errors",
            )
            _emit(report, args.json)
            return EXIT_FINDINGS
        if execution_result.returncode != 0:
            report.update(
                status="target_failed",
                exit_code=EXIT_TARGET_FAILED,
                message=(
                    "target or Valgrind exited nonzero without an actionable "
                    "memory finding"
                ),
            )
            _emit(report, args.json)
            return EXIT_TARGET_FAILED
        report.update(
            status="clean",
            exit_code=EXIT_CLEAN,
            message="no actionable leaks or memory errors detected",
        )
        _emit(report, args.json)
        return EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(_main())
