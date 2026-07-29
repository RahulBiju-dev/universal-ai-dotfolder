#!/usr/bin/env python3
"""Provide bounded Git telemetry and explicit-path staging without remote mutation."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, BinaryIO, NoReturn, Sequence
from urllib.parse import unquote, urlparse


DEFAULT_TIMEOUT = 15.0
MAX_TIMEOUT = 60.0
DEFAULT_OUTPUT_BYTES = 128 * 1024
MAX_OUTPUT_BYTES = 4 * 1024 * 1024
READ_CHUNK = 16 * 1024
REMOTE_CREDENTIALS = re.compile(r"(://)[^/\s:@]+(?::[^/\s@]*)?@")
REMOTE_QUERY_SECRET = re.compile(
    r"(?i)([?&](?:access[_-]?token|api[_-]?key|auth|password|secret|token)=)"
    r"[^&#\s]+"
)
TOKEN_SHAPE = re.compile(
    r"(?i)\b(?:gh[pousr]_[A-Za-z0-9]{20,}|"
    r"(?:api[_-]?key|token)[_-][A-Za-z0-9._-]{20,})\b"
)
SCP_REMOTE = re.compile(
    r"^(?:(?P<user>[A-Za-z0-9._-]+)@)?"
    r"(?P<host>[A-Za-z0-9.-]+):(?P<path>[^ ].*)$"
)
SSH_COMPONENT = re.compile(r"^[A-Za-z0-9._-]+$")
CONFLICT_CODES = frozenset({"AA", "AU", "DD", "DU", "UA", "UD", "UU"})


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        emit(
            {
                "ok": False,
                "operation": None,
                "repository": None,
                "error": {"type": "argument_error", "message": message},
            }
        )
        raise SystemExit(2)


class Capture:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.data = bytearray()
        self.total = 0

    def drain(self, pipe: BinaryIO) -> None:
        try:
            while True:
                chunk = pipe.read(READ_CHUNK)
                if not chunk:
                    return
                self.total += len(chunk)
                remaining = self.limit - len(self.data)
                if remaining > 0:
                    self.data.extend(chunk[:remaining])
        except (OSError, ValueError):
            return
        finally:
            try:
                pipe.close()
            except OSError:
                pass

    def text(self) -> str:
        return bytes(self.data).decode("utf-8", errors="replace")

    def payload(self, *, sanitize: bool = True) -> dict[str, Any]:
        text = self.text()
        sanitized = sanitize_remote_url(text) if sanitize else text
        return {
            "text": sanitized,
            "bytes_truncated": max(0, self.total - len(self.data)),
            "redacted": sanitized != text,
        }


def build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(
        description=(
            "Summarize Git state, inspect diffs and history, stage explicit "
            "paths, or inspect SSH remotes."
        )
    )
    parser.add_argument(
        "--repo",
        default=".",
        metavar="PATH",
        help="repository directory (default: current directory)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        metavar="SECONDS",
        help=f"per-command timeout, at most {MAX_TIMEOUT:g} seconds",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_OUTPUT_BYTES,
        metavar="BYTES",
        help="maximum retained bytes per process stream",
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("state", help="show branch, changes, remotes, and recent commits")

    diff_parser = subparsers.add_parser("diff", help="show a bounded local diff")
    diff_parser.add_argument("--staged", action="store_true", help="inspect staged changes")
    diff_parser.add_argument("paths", nargs="*", metavar="PATH")

    stage_parser = subparsers.add_parser(
        "stage", help="stage explicit repository-contained literal paths"
    )
    stage_parser.add_argument("paths", nargs="+", metavar="PATH")

    tree_parser = subparsers.add_parser("tree", help="return parsed commit topology")
    tree_parser.add_argument(
        "--limit", type=int, default=30, metavar="COUNT", help="commit limit"
    )

    ssh_parser = subparsers.add_parser(
        "ssh", help="inspect local SSH remote readiness"
    )
    ssh_parser.add_argument(
        "--probe",
        metavar="REMOTE",
        help="perform an authorized noninteractive handshake for one remote",
    )
    return parser


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def process_environment(*, read_only: bool) -> dict[str, str]:
    allowed = {
        "COMSPEC",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "PATH",
        "PATHEXT",
        "SSH_AGENT_PID",
        "SSH_AUTH_SOCK",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "TMPDIR",
        "USERPROFILE",
        "WINDIR",
    }
    environment = {
        key: value for key, value in os.environ.items() if key.upper() in allowed
    }
    environment.setdefault("PATH", os.defpath)
    environment.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "LC_ALL": "C",
        }
    )
    if read_only:
        environment["GIT_OPTIONAL_LOCKS"] = "0"
    return environment


def terminate(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
    else:
        process.kill()


def terminate_remaining_group(group_id: int) -> None:
    if os.name != "posix":
        return
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


def run_process(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout: float,
    max_bytes: int,
    environment: dict[str, str],
    sanitize_output: bool = True,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            list(argv),
            cwd=str(cwd),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=os.name == "posix",
            shell=False,
        )
    except OSError as exc:
        return {
            "ok": False,
            "argv": list(argv),
            "exit_code": None,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "stdout": {"text": "", "bytes_truncated": 0},
            "stderr": {"text": "", "bytes_truncated": 0},
            "error": {"type": exc.__class__.__name__, "message": str(exc)},
        }

    stdout_pipe = process.stdout
    stderr_pipe = process.stderr
    if stdout_pipe is None or stderr_pipe is None:
        terminate(process)
        process.wait()
        return {
            "ok": False,
            "argv": list(argv),
            "exit_code": process.returncode,
            "duration_ms": round((time.monotonic() - started) * 1000),
            "stdout": {"text": "", "bytes_truncated": 0},
            "stderr": {"text": "", "bytes_truncated": 0},
            "error": {
                "type": "capture_error",
                "message": "Process output pipes were not created.",
            },
        }
    stdout = Capture(max_bytes)
    stderr = Capture(max_bytes)
    threads = [
        threading.Thread(target=stdout.drain, args=(stdout_pipe,), daemon=True),
        threading.Thread(target=stderr.drain, args=(stderr_pipe,), daemon=True),
    ]
    for thread in threads:
        thread.start()

    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        terminate(process)
        process.wait()
    terminate_remaining_group(process.pid)
    for pipe, thread in zip((stdout_pipe, stderr_pipe), threads):
        thread.join(timeout=2)
        if thread.is_alive():
            try:
                pipe.close()
            except OSError:
                pass
            thread.join(timeout=1)

    error = None
    if timed_out:
        error = {
            "type": "timeout",
            "message": f"Command exceeded the {timeout:g}-second timeout.",
        }
    elif process.returncode != 0:
        error = {
            "type": "command_error",
            "message": (
                sanitize_remote_url(stderr.text()).strip()
                or f"Command exited {process.returncode}."
            ),
        }
    return {
        "ok": not timed_out and process.returncode == 0,
        "argv": list(argv),
        "exit_code": process.returncode,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "stdout": stdout.payload(sanitize=sanitize_output),
        "stderr": stderr.payload(sanitize=sanitize_output),
        "error": error,
    }


def git(
    repository: Path,
    arguments: Sequence[str],
    *,
    timeout: float,
    max_bytes: int,
    read_only: bool = True,
    sanitize_output: bool = True,
) -> dict[str, Any]:
    return run_process(
        ["git", "-C", str(repository), *arguments],
        cwd=repository,
        timeout=timeout,
        max_bytes=max_bytes,
        environment=process_environment(read_only=read_only),
        sanitize_output=sanitize_output,
    )


def discover_repository(
    candidate_value: str, *, timeout: float, max_bytes: int
) -> tuple[Path | None, dict[str, Any] | None]:
    try:
        candidate = Path(candidate_value).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        return None, {"type": exc.__class__.__name__, "message": str(exc)}
    if not candidate.is_dir():
        return None, {
            "type": "invalid_repository",
            "message": f"Repository path is not a directory: {candidate}",
        }
    probe = run_process(
        ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
        cwd=candidate,
        timeout=timeout,
        max_bytes=min(max_bytes, 4096),
        environment=process_environment(read_only=True),
    )
    if not probe["ok"]:
        return None, probe["error"]
    try:
        repository = Path(probe["stdout"]["text"].strip()).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        return None, {"type": exc.__class__.__name__, "message": str(exc)}
    return repository, None


def sanitize_remote_url(url: str) -> str:
    sanitized = REMOTE_CREDENTIALS.sub(r"\1[REDACTED]@", url)
    sanitized = REMOTE_QUERY_SECRET.sub(r"\1[REDACTED]", sanitized)
    return TOKEN_SHAPE.sub("[REDACTED]", sanitized)


def configured_remotes(
    repository: Path, *, timeout: float, max_bytes: int
) -> tuple[list[dict[str, str]], dict[str, Any] | None]:
    result = git(
        repository,
        ["remote", "--verbose"],
        timeout=timeout,
        max_bytes=max_bytes,
        sanitize_output=False,
    )
    if not result["ok"]:
        return [], result["error"]
    remotes: set[tuple[str, str, str]] = set()
    for line in result["stdout"]["text"].splitlines():
        fields = line.split()
        if len(fields) >= 3:
            remotes.add((fields[0], fields[1], fields[2].strip("()")))
    return [
        {"name": name, "url": url, "direction": direction}
        for name, url, direction in sorted(remotes)
    ], None


def status_summary(
    repository: Path, *, timeout: float, max_bytes: int
) -> dict[str, Any]:
    result = git(
        repository,
        ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
        timeout=timeout,
        max_bytes=max_bytes,
    )
    if not result["ok"]:
        return {"ok": False, "error": result["error"]}

    records = result["stdout"]["text"].split("\x00")
    counts = {"staged": 0, "unstaged": 0, "untracked": 0, "conflicted": 0}
    paths: list[dict[str, str]] = []
    parsed_records = 0
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if len(record) < 4:
            continue
        parsed_records += 1
        code = record[:2]
        path = record[3:]
        if "R" in code or "C" in code:
            if index < len(records) and records[index]:
                path = f"{records[index]} -> {path}"
                index += 1
        if code == "??":
            counts["untracked"] += 1
        else:
            if code[0] != " ":
                counts["staged"] += 1
            if code[1] != " ":
                counts["unstaged"] += 1
            if code in CONFLICT_CODES:
                counts["conflicted"] += 1
        if len(paths) < 40:
            paths.append({"code": code, "path": path})
    return {
        "ok": True,
        "counts": counts,
        "paths": paths,
        "path_sample_truncated": parsed_records > len(paths),
        "output_truncated": result["stdout"]["bytes_truncated"] > 0,
    }


def optional_text(
    repository: Path,
    arguments: Sequence[str],
    *,
    timeout: float,
    max_bytes: int,
) -> str | None:
    result = git(
        repository, arguments, timeout=timeout, max_bytes=max_bytes
    )
    return result["stdout"]["text"].strip() if result["ok"] else None


def state_operation(
    repository: Path, *, timeout: float, max_bytes: int
) -> tuple[dict[str, Any], int]:
    status = status_summary(repository, timeout=timeout, max_bytes=max_bytes)
    if not status["ok"]:
        return {"status": status}, 1

    branch = optional_text(
        repository,
        ["symbolic-ref", "--quiet", "--short", "HEAD"],
        timeout=timeout,
        max_bytes=4096,
    )
    head = optional_text(
        repository,
        ["rev-parse", "--short=12", "HEAD"],
        timeout=timeout,
        max_bytes=4096,
    )
    upstream = optional_text(
        repository,
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        timeout=timeout,
        max_bytes=4096,
    )
    ahead = behind = None
    if upstream:
        divergence = optional_text(
            repository,
            [
                "rev-list",
                "--left-right",
                "--count",
                f"HEAD{'.' * 3}{upstream}",
            ],
            timeout=timeout,
            max_bytes=4096,
        )
        if divergence:
            fields = divergence.split()
            if len(fields) == 2 and all(field.isdigit() for field in fields):
                ahead, behind = map(int, fields)

    log_result = git(
        repository,
        ["log", "-5", "--date=short", "--format=%h%x1f%ad%x1f%s%x1e"],
        timeout=timeout,
        max_bytes=max_bytes,
    )
    commits: list[dict[str, str]] = []
    if log_result["ok"]:
        for record in log_result["stdout"]["text"].split("\x1e"):
            fields = record.strip().split("\x1f", 2)
            if len(fields) == 3:
                commits.append({"id": fields[0], "date": fields[1], "subject": fields[2]})
    remotes, remote_error = configured_remotes(
        repository, timeout=timeout, max_bytes=max_bytes
    )
    return (
        {
            "branch": branch or (f"detached@{head}" if head else "unborn"),
            "head": head,
            "upstream": upstream,
            "ahead": ahead,
            "behind": behind,
            "changes": status,
            "recent_commits": commits,
            "remotes": [
                {**remote, "url": sanitize_remote_url(remote["url"])}
                for remote in remotes
            ],
            "remote_error": remote_error,
        },
        0,
    )


def normalize_paths(
    repository: Path,
    values: Sequence[str],
    *,
    require_known: bool,
    timeout: float,
    max_bytes: int,
) -> list[str]:
    normalized: list[str] = []
    for value in values:
        if not value or "\x00" in value:
            raise ValueError("Git paths must be nonempty and contain no NUL")
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = repository / candidate
        absolute = Path(os.path.abspath(candidate))
        if not absolute.is_relative_to(repository):
            raise ValueError(f"Git path escapes repository: {value!r}")
        relative = absolute.relative_to(repository).as_posix()
        if relative in {"", "."}:
            raise ValueError("Repository-wide staging requires explicit file paths")
        repository_path = repository / relative
        if repository_path.is_symlink():
            normalized.append(relative)
            continue
        if repository_path.exists():
            try:
                resolved = repository_path.resolve(strict=True)
            except (OSError, RuntimeError) as exc:
                raise ValueError(f"Cannot resolve Git path {value!r}: {exc}") from exc
            if not resolved.is_relative_to(repository):
                raise ValueError(f"Git path follows a symlink outside repository: {value!r}")
            if require_known and not repository_path.is_file():
                raise ValueError(f"Git staging requires a file, symlink, or deletion: {value!r}")
        elif require_known:
            tracked = git(
                repository,
                ["--literal-pathspecs", "ls-files", "--stage", "--", relative],
                timeout=timeout,
                max_bytes=min(max_bytes, 4096),
            )
            tracked_paths = {
                line.split("\t", 1)[1]
                for line in tracked["stdout"]["text"].splitlines()
                if "\t" in line
            }
            if not tracked["ok"] or tracked_paths != {relative}:
                raise ValueError(f"Path is neither present nor tracked: {value!r}")
        normalized.append(relative)
    return sorted(set(normalized))


def diff_operation(
    repository: Path,
    *,
    staged: bool,
    paths: Sequence[str],
    timeout: float,
    max_bytes: int,
) -> tuple[dict[str, Any], int]:
    normalized = normalize_paths(
        repository,
        paths,
        require_known=False,
        timeout=timeout,
        max_bytes=max_bytes,
    )
    command = ["--literal-pathspecs", "diff", "--no-ext-diff", "--no-textconv"]
    if staged:
        command.append("--cached")
    command.extend(["--", *normalized])
    result = git(
        repository, command, timeout=timeout, max_bytes=max_bytes
    )
    return (
        {
            "staged": staged,
            "paths": normalized,
            "diff": result["stdout"],
            "line_count": len(result["stdout"]["text"].splitlines()),
            "error": result["error"],
        },
        0 if result["ok"] else 1,
    )


def stage_operation(
    repository: Path,
    *,
    paths: Sequence[str],
    timeout: float,
    max_bytes: int,
) -> tuple[dict[str, Any], int]:
    normalized = normalize_paths(
        repository,
        paths,
        require_known=True,
        timeout=timeout,
        max_bytes=max_bytes,
    )
    before = git(
        repository,
        ["--literal-pathspecs", "status", "--short", "--", *normalized],
        timeout=timeout,
        max_bytes=max_bytes,
    )
    staged = git(
        repository,
        ["--literal-pathspecs", "add", "--", *normalized],
        timeout=timeout,
        max_bytes=max_bytes,
        read_only=False,
    )
    if not staged["ok"]:
        return {
            "paths": normalized,
            "before": before["stdout"],
            "error": staged["error"],
        }, 1
    after = git(
        repository,
        ["--literal-pathspecs", "status", "--short", "--", *normalized],
        timeout=timeout,
        max_bytes=max_bytes,
    )
    stat = git(
        repository,
        ["--literal-pathspecs", "diff", "--cached", "--stat", "--", *normalized],
        timeout=timeout,
        max_bytes=max_bytes,
    )
    return (
        {
            "paths": normalized,
            "before": before["stdout"],
            "after": after["stdout"],
            "staged_stat": stat["stdout"],
            "error": after["error"] or stat["error"],
        },
        0 if after["ok"] and stat["ok"] else 1,
    )


def tree_operation(
    repository: Path, *, limit: int, timeout: float, max_bytes: int
) -> tuple[dict[str, Any], int]:
    if not 1 <= limit <= 500:
        raise ValueError("--limit must be between 1 and 500")
    result = git(
        repository,
        [
            "log",
            "--all",
            "--topo-order",
            f"-{limit}",
            "--date=short",
            "--format=%H%x1f%h%x1f%P%x1f%ad%x1f%D%x1f%s%x1e",
        ],
        timeout=timeout,
        max_bytes=max_bytes,
    )
    commits: list[dict[str, Any]] = []
    if result["ok"]:
        for record in result["stdout"]["text"].split("\x1e"):
            fields = record.strip().split("\x1f", 5)
            if len(fields) == 6:
                commits.append(
                    {
                        "id": fields[0],
                        "short_id": fields[1],
                        "parents": fields[2].split(),
                        "date": fields[3],
                        "decorations": fields[4],
                        "subject": fields[5],
                    }
                )
    return (
        {
            "commits": commits,
            "truncated": result["stdout"]["bytes_truncated"] > 0,
            "error": result["error"],
        },
        0 if result["ok"] else 1,
    )


def parse_ssh_url(url: str) -> dict[str, Any] | None:
    parsed = urlparse(url)
    if parsed.scheme == "ssh" and parsed.hostname:
        return {
            "user": unquote(parsed.username or "git"),
            "host": parsed.hostname,
            "port": parsed.port or 22,
        }
    match = SCP_REMOTE.fullmatch(url)
    if match:
        return {
            "user": match.group("user") or "git",
            "host": match.group("host"),
            "port": 22,
        }
    return None


def known_host(host: str, *, timeout: float, max_bytes: int) -> bool | None:
    executable = shutil.which("ssh-keygen")
    if not executable:
        return None
    candidates = [Path.home() / ".ssh" / "known_hosts", Path.home() / ".ssh" / "known_hosts2"]
    for candidate in candidates:
        if not candidate.is_file():
            continue
        result = run_process(
            [executable, "-F", host, "-f", str(candidate)],
            cwd=Path.cwd(),
            timeout=min(timeout, 5),
            max_bytes=min(max_bytes, 4096),
            environment=process_environment(read_only=True),
        )
        if result["ok"] and result["stdout"]["text"].strip():
            return True
    return False


def ssh_operation(
    repository: Path,
    *,
    probe_remote: str | None,
    timeout: float,
    max_bytes: int,
) -> tuple[dict[str, Any], int]:
    remotes, remote_error = configured_remotes(
        repository, timeout=timeout, max_bytes=max_bytes
    )
    ssh_executable = shutil.which("ssh")
    states: list[dict[str, Any]] = []
    fetch_urls: dict[str, str] = {}
    for remote in remotes:
        if remote["direction"] == "fetch":
            fetch_urls[remote["name"]] = remote["url"]
    for name, url in sorted(fetch_urls.items()):
        target = parse_ssh_url(url)
        states.append(
            {
                "remote": name,
                "transport": "ssh" if target else urlparse(url).scheme or "local",
                "host": target["host"] if target else None,
                "user": target["user"] if target else None,
                "port": target["port"] if target else None,
                "ssh_available": ssh_executable is not None,
                "known_host": (
                    known_host(
                        target["host"], timeout=timeout, max_bytes=max_bytes
                    )
                    if target
                    else None
                ),
            }
        )

    probe_result = None
    exit_code = 0 if remote_error is None else 1
    if probe_remote:
        if probe_remote not in fetch_urls:
            raise ValueError(f"Unknown fetch remote: {probe_remote!r}")
        target = parse_ssh_url(fetch_urls[probe_remote])
        if target is None:
            raise ValueError(f"Remote {probe_remote!r} does not use SSH")
        if ssh_executable is None:
            raise ValueError("ssh executable is unavailable")
        if not SSH_COMPONENT.fullmatch(target["user"]) or not SSH_COMPONENT.fullmatch(
            target["host"]
        ):
            raise ValueError("SSH remote contains unsupported user or host syntax")
        destination = f"{target['user']}@{target['host']}"
        probe_result = run_process(
            [
                ssh_executable,
                "-T",
                "-o",
                "BatchMode=yes",
                "-o",
                "NumberOfPasswordPrompts=0",
                "-o",
                "StrictHostKeyChecking=yes",
                "-o",
                f"ConnectTimeout={max(1, min(10, int(timeout)))}",
                "-p",
                str(target["port"]),
                destination,
            ],
            cwd=repository,
            timeout=min(timeout, 15),
            max_bytes=min(max_bytes, 16 * 1024),
            environment=process_environment(read_only=True),
        )
        message = (
            probe_result["stdout"]["text"] + "\n" + probe_result["stderr"]["text"]
        ).casefold()
        authenticated = probe_result["ok"] or any(
            marker in message
            for marker in ("successfully authenticated", "authenticated to", "welcome to gitlab")
        )
        probe_result = {
            "remote": probe_remote,
            "authenticated": authenticated,
            "exit_code": probe_result["exit_code"],
            "stdout": probe_result["stdout"],
            "stderr": probe_result["stderr"],
            "error": None if authenticated else probe_result["error"],
        }
        exit_code = 0 if authenticated else 1
    return (
        {
            "ssh_available": ssh_executable is not None,
            "remotes": states,
            "probe": probe_result,
            "error": remote_error,
        },
        exit_code,
    )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if not 0 < arguments.timeout <= MAX_TIMEOUT:
        build_parser().error(
            f"--timeout must be greater than zero and at most {MAX_TIMEOUT:g}"
        )
    if not 4096 <= arguments.max_bytes <= MAX_OUTPUT_BYTES:
        build_parser().error(
            f"--max-bytes must be between 4096 and {MAX_OUTPUT_BYTES}"
        )

    repository, repository_error = discover_repository(
        arguments.repo, timeout=arguments.timeout, max_bytes=arguments.max_bytes
    )
    if repository is None:
        emit(
            {
                "ok": False,
                "operation": arguments.operation,
                "repository": arguments.repo,
                "error": repository_error,
            }
        )
        return 2

    try:
        if arguments.operation == "state":
            payload, exit_code = state_operation(
                repository,
                timeout=arguments.timeout,
                max_bytes=arguments.max_bytes,
            )
        elif arguments.operation == "diff":
            payload, exit_code = diff_operation(
                repository,
                staged=arguments.staged,
                paths=arguments.paths,
                timeout=arguments.timeout,
                max_bytes=arguments.max_bytes,
            )
        elif arguments.operation == "stage":
            payload, exit_code = stage_operation(
                repository,
                paths=arguments.paths,
                timeout=arguments.timeout,
                max_bytes=arguments.max_bytes,
            )
        elif arguments.operation == "tree":
            payload, exit_code = tree_operation(
                repository,
                limit=arguments.limit,
                timeout=arguments.timeout,
                max_bytes=arguments.max_bytes,
            )
        elif arguments.operation == "ssh":
            payload, exit_code = ssh_operation(
                repository,
                probe_remote=arguments.probe,
                timeout=arguments.timeout,
                max_bytes=arguments.max_bytes,
            )
        else:
            raise ValueError(f"Unsupported operation: {arguments.operation}")
    except (OSError, RuntimeError, ValueError) as exc:
        emit(
            {
                "ok": False,
                "operation": arguments.operation,
                "repository": str(repository),
                "error": {"type": exc.__class__.__name__, "message": str(exc)},
            }
        )
        return 2

    emit(
        {
            "ok": exit_code == 0,
            "operation": arguments.operation,
            "repository": str(repository),
            **payload,
        }
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
