#!/usr/bin/env python3
"""Run one bounded local process without invoking a shell."""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, BinaryIO, NoReturn, Sequence


DEFAULT_TIMEOUT = 300.0
MAX_TIMEOUT = 3600.0
DEFAULT_OUTPUT_BYTES = 32 * 1024
MAX_OUTPUT_BYTES = 4 * 1024 * 1024
READ_CHUNK = 16 * 1024
SAFE_ENVIRONMENT_KEYS = frozenset(
    {
        "COMSPEC",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "LOGNAME",
        "PATH",
        "PATHEXT",
        "SYSTEMROOT",
        "TEMP",
        "TERM",
        "TMP",
        "TMPDIR",
        "USER",
        "USERPROFILE",
        "WINDIR",
    }
)
SENSITIVE_ARGUMENTS = frozenset(
    {
        "--api-key",
        "--authorization",
        "--client-secret",
        "--password",
        "--private-key",
        "--secret",
        "--token",
        "-p",
    }
)
SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|authorization|client[_-]?secret|password|"
    r"private[_-]?key|secret|token)\b(\s*[:=]\s*)(\S+)"
)
AUTHORIZATION_VALUE = re.compile(
    r"(?i)\bauthorization\b(\s*[:=]\s*)[^\r\n]+"
)
URL_CREDENTIALS = re.compile(r"(://)[^/\s:@]+:[^/\s@]+@")
PEM_BLOCK = re.compile(
    r"-----BEGIN [A-Z0-9 ]+PRIVATE KEY-----.*?"
    r"-----END [A-Z0-9 ]+PRIVATE KEY-----",
    re.DOTALL,
)
ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class JsonArgumentParser(argparse.ArgumentParser):
    """Emit parser failures through the normal JSON contract."""

    def error(self, message: str) -> NoReturn:
        emit(
            {
                "ok": False,
                "status": "argument_error",
                "exit_code": None,
                "signal": None,
                "duration_ms": 0,
                "stdout": stream_payload("", 0, False),
                "stderr": stream_payload("", 0, False),
                "error": {"type": "argument_error", "message": message},
            }
        )
        raise SystemExit(2)


class Capture:
    """Retain a bounded prefix while continuing to drain a pipe."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.data = bytearray()
        self.total = 0

    def read(self, pipe: BinaryIO) -> None:
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

    @property
    def truncated_bytes(self) -> int:
        return max(0, self.total - len(self.data))

    def decode(self) -> str:
        return bytes(self.data).decode("utf-8", errors="replace")


def build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(
        description=(
            "Execute one direct argument vector inside a workspace and emit "
            "bounded JSON terminal state."
        )
    )
    parser.add_argument(
        "--root",
        default=".",
        metavar="PATH",
        help="workspace boundary (default: current directory)",
    )
    parser.add_argument(
        "--cwd",
        metavar="PATH",
        help="working directory, absolute or relative to --root",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        metavar="SECONDS",
        help=f"runtime limit, at most {MAX_TIMEOUT:g} seconds",
    )
    parser.add_argument(
        "--max-output-bytes",
        type=int,
        default=DEFAULT_OUTPUT_BYTES,
        metavar="BYTES",
        help="retained byte limit for each output stream",
    )
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="add one explicit child environment value; may be repeated",
    )
    parser.add_argument(
        "--no-redact",
        action="store_true",
        help="disable credential-pattern redaction in captured output",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="executable and arguments after --",
    )
    return parser


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def redact(text: str) -> tuple[str, bool]:
    cleaned = AUTHORIZATION_VALUE.sub(r"authorization\1[REDACTED]", text)
    cleaned = SENSITIVE_ASSIGNMENT.sub(r"\1\2[REDACTED]", cleaned)
    cleaned = URL_CREDENTIALS.sub(r"\1[REDACTED]@", cleaned)
    cleaned = PEM_BLOCK.sub("[REDACTED PRIVATE KEY]", cleaned)
    return cleaned, cleaned != text


def sanitize_argv(argv: Sequence[str]) -> list[str]:
    sanitized: list[str] = []
    hide_next = False
    for argument in argv:
        if hide_next:
            sanitized.append("[REDACTED]")
            hide_next = False
            continue
        option = argument.casefold()
        if option in SENSITIVE_ARGUMENTS:
            sanitized.append(argument)
            hide_next = True
            continue
        if "=" in argument and argument.split("=", 1)[0].casefold() in SENSITIVE_ARGUMENTS:
            sanitized.append(f"{argument.split('=', 1)[0]}=[REDACTED]")
            continue
        sanitized.append(redact(argument)[0])
    return sanitized


def stream_payload(text: str, truncated_bytes: int, was_redacted: bool) -> dict[str, Any]:
    return {
        "text": text,
        "bytes_truncated": truncated_bytes,
        "redacted": was_redacted,
    }


def resolve_directories(root_value: str, cwd_value: str | None) -> tuple[Path, Path]:
    root = Path(root_value).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError(f"Workspace root is not a directory: {root}")

    candidate = Path(cwd_value).expanduser() if cwd_value else root
    if not candidate.is_absolute():
        candidate = root / candidate
    cwd = candidate.resolve(strict=True)
    if not cwd.is_dir():
        raise ValueError(f"Working directory is not a directory: {cwd}")
    if not cwd.is_relative_to(root):
        raise ValueError(f"Working directory escapes workspace root: {cwd}")
    return root, cwd


def build_environment(assignments: Sequence[str]) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in SAFE_ENVIRONMENT_KEYS
    }
    environment.setdefault("PATH", os.defpath)
    environment.setdefault("LANG", "C.UTF-8")
    environment["PYTHONIOENCODING"] = "utf-8"

    for assignment in assignments:
        if "=" not in assignment:
            raise ValueError(f"Environment assignment lacks '=': {assignment!r}")
        name, value = assignment.split("=", 1)
        if not ENVIRONMENT_NAME.fullmatch(name):
            raise ValueError(f"Invalid environment name: {name!r}")
        if "\x00" in value:
            raise ValueError(f"Environment value for {name!r} contains NUL")
        environment[name] = value
    return environment


def terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=0.25)
            return
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
    elif os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
    else:
        process.kill()


def terminate_remaining_group(group_id: int) -> None:
    """Stop descendants that retained the command's process group after exit."""
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


def execute(
    argv: Sequence[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout: float,
    output_limit: int,
    enable_redaction: bool,
) -> tuple[dict[str, Any], int]:
    start = time.monotonic()
    popen_options: dict[str, Any] = {}
    if os.name == "posix":
        popen_options["start_new_session"] = True
    elif os.name == "nt":
        popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    try:
        process = subprocess.Popen(
            list(argv),
            cwd=str(cwd),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            **popen_options,
        )
    except (OSError, ValueError) as exc:
        return (
            {
                "ok": False,
                "status": "launch_error",
                "argv": sanitize_argv(argv),
                "cwd": str(cwd),
                "exit_code": None,
                "signal": None,
                "duration_ms": round((time.monotonic() - start) * 1000),
                "stdout": stream_payload("", 0, False),
                "stderr": stream_payload("", 0, False),
                "error": {"type": exc.__class__.__name__, "message": str(exc)},
                "safety": (
                    "Only the working directory is workspace-contained; the "
                    "process is not sandboxed."
                ),
            },
            127,
        )

    stdout_pipe = process.stdout
    stderr_pipe = process.stderr
    if stdout_pipe is None or stderr_pipe is None:
        terminate_process_group(process)
        process.wait()
        return (
            {
                "ok": False,
                "status": "launch_error",
                "argv": sanitize_argv(argv),
                "cwd": str(cwd),
                "exit_code": process.returncode,
                "signal": None,
                "duration_ms": round((time.monotonic() - start) * 1000),
                "stdout": stream_payload("", 0, False),
                "stderr": stream_payload("", 0, False),
                "error": {
                    "type": "capture_error",
                    "message": "Process output pipes were not created.",
                },
                "safety": (
                    "Only the working directory is workspace-contained; the "
                    "process is not sandboxed."
                ),
            },
            127,
        )
    stdout_capture = Capture(output_limit)
    stderr_capture = Capture(output_limit)
    readers = [
        threading.Thread(target=stdout_capture.read, args=(stdout_pipe,), daemon=True),
        threading.Thread(target=stderr_capture.read, args=(stderr_pipe,), daemon=True),
    ]
    for reader in readers:
        reader.start()

    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        terminate_process_group(process)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    terminate_remaining_group(process.pid)
    for reader in readers:
        reader.join(timeout=2)
    for pipe, reader in zip((stdout_pipe, stderr_pipe), readers):
        if reader.is_alive():
            try:
                pipe.close()
            except OSError:
                pass
            reader.join(timeout=1)

    stdout_text = stdout_capture.decode()
    stderr_text = stderr_capture.decode()
    stdout_redacted = False
    stderr_redacted = False
    if enable_redaction:
        stdout_text, stdout_redacted = redact(stdout_text)
        stderr_text, stderr_redacted = redact(stderr_text)

    return_code = process.returncode
    terminating_signal = -return_code if return_code is not None and return_code < 0 else None
    if timed_out:
        status = "timeout"
        utility_exit = 124
        error = {
            "type": "timeout",
            "message": f"Process exceeded the {timeout:g}-second limit.",
        }
    elif return_code == 0:
        status = "success"
        utility_exit = 0
        error = None
    else:
        status = "failure"
        utility_exit = 1
        error = {
            "type": "signal" if terminating_signal else "nonzero_exit",
            "message": (
                f"Process terminated by signal {terminating_signal}."
                if terminating_signal
                else f"Process exited with status {return_code}."
            ),
        }

    return (
        {
            "ok": status == "success",
            "status": status,
            "argv": sanitize_argv(argv),
            "cwd": str(cwd),
            "exit_code": return_code,
            "signal": terminating_signal,
            "duration_ms": round((time.monotonic() - start) * 1000),
            "stdout": stream_payload(
                stdout_text, stdout_capture.truncated_bytes, stdout_redacted
            ),
            "stderr": stream_payload(
                stderr_text, stderr_capture.truncated_bytes, stderr_redacted
            ),
            "error": error,
            "safety": (
                "Only the working directory is workspace-contained; the "
                "process is not sandboxed."
            ),
        },
        utility_exit,
    )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    command = list(arguments.command)
    if command[:1] == ["--"]:
        command.pop(0)

    if not command or not command[0]:
        build_parser().error("an executable is required after --")
    if not 0 < arguments.timeout <= MAX_TIMEOUT:
        build_parser().error(
            f"--timeout must be greater than zero and at most {MAX_TIMEOUT:g}"
        )
    if not 1024 <= arguments.max_output_bytes <= MAX_OUTPUT_BYTES:
        build_parser().error(
            f"--max-output-bytes must be between 1024 and {MAX_OUTPUT_BYTES}"
        )
    if any("\x00" in value for value in command):
        build_parser().error("command arguments must not contain NUL")

    try:
        _, cwd = resolve_directories(arguments.root, arguments.cwd)
        environment = build_environment(arguments.env)
    except (OSError, RuntimeError, ValueError) as exc:
        emit(
            {
                "ok": False,
                "status": "validation_error",
                "argv": sanitize_argv(command),
                "cwd": arguments.cwd,
                "exit_code": None,
                "signal": None,
                "duration_ms": 0,
                "stdout": stream_payload("", 0, False),
                "stderr": stream_payload("", 0, False),
                "error": {"type": exc.__class__.__name__, "message": str(exc)},
                "safety": (
                    "Only the working directory is workspace-contained; the "
                    "process is not sandboxed."
                ),
            }
        )
        return 2

    result, exit_code = execute(
        command,
        cwd=cwd,
        environment=environment,
        timeout=arguments.timeout,
        output_limit=arguments.max_output_bytes,
        enable_redaction=not arguments.no_redact,
    )
    emit(result)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
