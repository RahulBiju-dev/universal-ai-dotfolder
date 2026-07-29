#!/usr/bin/env python3
"""Statically inspect one Python or C file and generate a unittest harness."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import pprint
import re
import stat
import sys
import tempfile
import textwrap
import tokenize
from pathlib import Path
from typing import Any, Sequence


MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_INTERFACES = 24
MAX_SMOKE_CASES = 32
DEFAULT_TIMEOUT_SECONDS = 2.0
DEFAULT_OUTPUT_BYTES = 64 * 1024
MIN_OUTPUT_BYTES = 4 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024


class GenerationError(RuntimeError):
    """A concise, user-correctable generation failure."""


PYTHON_LIMITATIONS = (
    "Smoke inputs check bounded termination, signals, importability, and symbol "
    "resolution; they do not establish semantic correctness.",
    "Ordinary exceptions raised by inferred boundary inputs are accepted because "
    "the source contract does not reveal which exceptions are intentional.",
    "Dynamic exports, decorator-altered signatures, metaclasses, lazy iterator "
    "consumption, external services, and stateful call sequences are not exhaustive.",
    "Import checks execute module top-level code in an isolated child working "
    "directory; they cannot prevent absolute-path, network, or other external effects.",
    "Timeout, output, file-size, descriptor, CPU, and memory limits are best effort "
    "and depend on operating-system support.",
)

C_LIMITATIONS = (
    "Strict compilation covers one translation unit with generic C11 flags; project "
    "defines, generated headers, companion objects, libraries, and build flags are absent.",
    "Non-main functions are compile-checked only because static inspection cannot infer "
    "safe ABI values, ownership rules, or semantic assertions.",
    "Main smoke cases provide empty, malformed, and bounded large stdin; nonzero exit "
    "codes are accepted, while timeouts and signals fail.",
    "The harness does not replace sanitizers, fuzzers, Valgrind, integration tests, or "
    "manual ownership and concurrency review.",
    "Timeout, output, file-size, descriptor, CPU, and memory limits are best effort "
    "and depend on operating-system support.",
)


COMMON_RUNTIME = r'''
def _child_limits():
    if os.name != "posix":
        return
    try:
        import resource
    except ImportError:
        return

    cpu_seconds = max(1, int(math.ceil(TIMEOUT_SECONDS)) + 1)
    limits = (
        (getattr(resource, "RLIMIT_CPU", None), (cpu_seconds, cpu_seconds)),
        (
            getattr(resource, "RLIMIT_AS", None),
            (1536 * 1024 * 1024, 1536 * 1024 * 1024),
        ),
        (
            getattr(resource, "RLIMIT_FSIZE", None),
            (8 * 1024 * 1024, 8 * 1024 * 1024),
        ),
        (getattr(resource, "RLIMIT_NOFILE", None), (64, 64)),
    )
    for resource_id, value in limits:
        if resource_id is None:
            continue
        try:
            soft, hard = resource.getrlimit(resource_id)
            requested_soft, requested_hard = value
            if hard != resource.RLIM_INFINITY:
                requested_soft = min(requested_soft, hard)
                requested_hard = min(requested_hard, hard)
            resource.setrlimit(
                resource_id, (requested_soft, requested_hard)
            )
        except (OSError, ValueError):
            continue


def _drain(pipe, bucket):
    try:
        while True:
            chunk = pipe.read(8192)
            if not chunk:
                break
            remaining = MAX_OUTPUT_BYTES - len(bucket["data"])
            if remaining > 0:
                bucket["data"].extend(chunk[:remaining])
            if len(chunk) > remaining:
                bucket["truncated"] = True
    finally:
        pipe.close()


def _kill_process_group(process):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
            return
        except ProcessLookupError:
            return
        except OSError:
            pass
    try:
        process.kill()
    except ProcessLookupError:
        pass


def _run(command, *, cwd, input_data=None):
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    environment.pop("PYTHONINSPECT", None)
    environment.pop("PYTHONSTARTUP", None)

    stdin = subprocess.PIPE if input_data is not None else subprocess.DEVNULL
    options = {
        "cwd": str(cwd),
        "env": environment,
        "stdin": stdin,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }
    if os.name == "posix":
        options["start_new_session"] = True
        options["preexec_fn"] = _child_limits
    elif os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    try:
        process = subprocess.Popen(command, **options)
    except OSError as exc:
        return {
            "command": command,
            "returncode": None,
            "timed_out": False,
            "stdout": "",
            "stderr": "",
            "stdout_truncated": False,
            "stderr_truncated": False,
            "launch_error": f"{type(exc).__name__}: {exc}",
        }

    stdout_bucket = {"data": bytearray(), "truncated": False}
    stderr_bucket = {"data": bytearray(), "truncated": False}
    readers = (
        threading.Thread(
            target=_drain, args=(process.stdout, stdout_bucket), daemon=True
        ),
        threading.Thread(
            target=_drain, args=(process.stderr, stderr_bucket), daemon=True
        ),
    )
    for reader in readers:
        reader.start()

    if input_data is not None and process.stdin is not None:
        try:
            process.stdin.write(input_data)
            process.stdin.flush()
        except (BrokenPipeError, OSError):
            pass
        finally:
            process.stdin.close()

    timed_out = False
    try:
        returncode = process.wait(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_process_group(process)
        try:
            returncode = process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            returncode = None
    finally:
        if os.name == "posix":
            _kill_process_group(process)

    for reader in readers:
        reader.join(timeout=1.0)

    return {
        "command": command,
        "returncode": returncode,
        "timed_out": timed_out,
        "stdout": bytes(stdout_bucket["data"]).decode("utf-8", "replace"),
        "stderr": bytes(stderr_bucket["data"]).decode("utf-8", "replace"),
        "stdout_truncated": stdout_bucket["truncated"],
        "stderr_truncated": stderr_bucket["truncated"],
        "launch_error": None,
    }


def _diagnostic(result):
    command = " ".join(shlex.quote(str(part)) for part in result["command"])
    details = [
        f"command: {command}",
        f"returncode: {result['returncode']}",
        f"timed_out: {result['timed_out']}",
    ]
    if result["launch_error"]:
        details.append(f"launch_error: {result['launch_error']}")
    if result["stdout"]:
        suffix = " [truncated]" if result["stdout_truncated"] else ""
        details.append(f"stdout{suffix}:\n{result['stdout']}")
    if result["stderr"]:
        suffix = " [truncated]" if result["stderr_truncated"] else ""
        details.append(f"stderr{suffix}:\n{result['stderr']}")
    return "\n".join(details)


def _assert_bounded(test_case, result, label, *, require_zero):
    diagnostic = f"{label}\n{_diagnostic(result)}"
    test_case.assertIsNone(result["launch_error"], diagnostic)
    test_case.assertFalse(result["timed_out"], diagnostic)
    test_case.assertIsNotNone(result["returncode"], diagnostic)
    test_case.assertGreaterEqual(result["returncode"], 0, diagnostic)
    if require_zero:
        test_case.assertEqual(result["returncode"], 0, diagnostic)
'''


PYTHON_CHILDREN = r'''
_PYTHON_SYNTAX = r"""
import ast
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
compile(source.read_bytes(), str(source), "exec", ast.PyCF_ONLY_AST)
"""

_PYTHON_IMPORT = r"""
import importlib.util
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2])
sys.path[:0] = [str(root), str(source.parent)]
spec = importlib.util.spec_from_file_location("_generated_test_target", source)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to create module spec")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
"""

_PYTHON_CALL = r"""
import asyncio
import importlib.util
import inspect
import io
import json
import pathlib
import sys


def materialize(descriptor):
    kind = descriptor["kind"]
    values = {
        "none": lambda: None,
        "false": lambda: False,
        "zero-int": lambda: 0,
        "max-int": lambda: (2 ** 31) - 1,
        "zero-float": lambda: 0.0,
        "max-float": lambda: sys.float_info.max,
        "empty-text": lambda: "",
        "large-text": lambda: "x" * 4096,
        "malformed-text": lambda: "\x00\ufffd{",
        "empty-bytes": lambda: b"",
        "large-bytes": lambda: b"x" * 4096,
        "malformed-bytes": lambda: b"\x00\xffinvalid",
        "empty-list": lambda: [],
        "large-list": lambda: [0] * 1024,
        "malformed-list": lambda: [None, {"invalid": object()}],
        "empty-tuple": lambda: (),
        "large-tuple": lambda: tuple([0] * 1024),
        "malformed-tuple": lambda: (None, {"invalid": object()}),
        "empty-set": lambda: set(),
        "large-set": lambda: set(range(1024)),
        "malformed-set": lambda: {None, "invalid"},
        "empty-dict": lambda: {},
        "large-dict": lambda: {str(index): index for index in range(1024)},
        "malformed-dict": lambda: {"\x00": object()},
        "empty-path": lambda: "",
        "large-path": lambda: "x" * 4096,
        "malformed-path": lambda: "\x00",
        "empty-stream": lambda: io.BytesIO(b""),
        "large-stream": lambda: io.BytesIO(b"x" * 4096),
        "malformed-stream": lambda: io.BytesIO(b"\x00\xffinvalid"),
        "opaque": lambda: object(),
    }
    if kind not in values:
        raise ValueError(f"unsupported descriptor: {kind}")
    return values[kind]()


source = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2])
case = json.loads(sys.argv[3])
sys.path[:0] = [str(root), str(source.parent)]
spec = importlib.util.spec_from_file_location("_generated_test_target", source)
if spec is None or spec.loader is None:
    raise SystemExit(20)
module = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(module)
    target = getattr(module, case["symbol"])
except BaseException as exc:
    print(
        json.dumps(
            {"outcome": "resolution-error", "type": type(exc).__name__},
            sort_keys=True,
        )
    )
    raise SystemExit(20)

args = [materialize(item) for item in case["args"]]
kwargs = {
    name: materialize(item) for name, item in case["kwargs"].items()
}
try:
    result = target(*args, **kwargs)
    if inspect.isawaitable(result):
        asyncio.run(result)
except BaseException as exc:
    print(
        json.dumps(
            {"outcome": "exception", "type": type(exc).__name__},
            sort_keys=True,
        )
    )
    raise SystemExit(0)
print(json.dumps({"outcome": "returned"}, sort_keys=True))
"""
'''


PYTHON_TEST_BODY = r'''
class GeneratedPythonSmokeTests(unittest.TestCase):
    def test_source_has_valid_syntax(self):
        with tempfile.TemporaryDirectory(prefix="generated-python-syntax-") as tmp:
            result = _run(
                [sys.executable, "-I", "-c", _PYTHON_SYNTAX, str(SOURCE)],
                cwd=tmp,
            )
        _assert_bounded(self, result, "Python syntax check", require_zero=True)

    def test_module_imports_in_isolation(self):
        with tempfile.TemporaryDirectory(prefix="generated-python-import-") as tmp:
            result = _run(
                [
                    sys.executable,
                    "-I",
                    "-c",
                    _PYTHON_IMPORT,
                    str(SOURCE),
                    str(WORKSPACE_ROOT),
                ],
                cwd=tmp,
            )
        _assert_bounded(self, result, "Python import check", require_zero=True)

    def test_public_interface_smoke_cases(self):
        if not SMOKE_CASES:
            self.skipTest("no statically discoverable public callables")
        for case in SMOKE_CASES:
            with self.subTest(case=case["label"]):
                with tempfile.TemporaryDirectory(
                    prefix="generated-python-call-"
                ) as tmp:
                    result = _run(
                        [
                            sys.executable,
                            "-I",
                            "-c",
                            _PYTHON_CALL,
                            str(SOURCE),
                            str(WORKSPACE_ROOT),
                            json.dumps(case, sort_keys=True),
                        ],
                        cwd=tmp,
                    )
                _assert_bounded(
                    self,
                    result,
                    f"Python interface case {case['label']}",
                    require_zero=True,
                )


if __name__ == "__main__":
    unittest.main()
'''


C_TEST_BODY = r'''
def _compiler_command():
    configured = os.environ.get("CC", "")
    candidates = []
    if configured:
        try:
            candidates.append(shlex.split(configured))
        except ValueError:
            candidates.append([])
    candidates.extend(([name] for name in ("cc", "clang", "gcc")))
    for candidate in candidates:
        if not candidate:
            continue
        executable = shutil.which(candidate[0])
        if executable:
            return [executable, *candidate[1:]]
    return None


def _compile(source, output, *, link, cwd):
    compiler = _compiler_command()
    if compiler is None:
        return None
    command = [
        *compiler,
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-Werror",
        "-g",
        "-O0",
        str(source),
    ]
    if not link:
        command.append("-c")
    command.extend(["-o", str(output)])
    return _run(command, cwd=cwd)


class GeneratedCSmokeTests(unittest.TestCase):
    def test_translation_unit_compiles_strictly(self):
        with tempfile.TemporaryDirectory(prefix="generated-c-object-") as tmp:
            output = pathlib.Path(tmp) / "target.o"
            result = _compile(SOURCE, output, link=False, cwd=tmp)
        if result is None:
            self.skipTest("no C compiler found in CC or PATH")
        _assert_bounded(self, result, "strict C object compilation", require_zero=True)

    def test_main_handles_bounded_input(self):
        if not HAS_MAIN:
            self.skipTest("no main function discovered; compile-only coverage")
        with tempfile.TemporaryDirectory(prefix="generated-c-main-") as tmp:
            suffix = ".exe" if os.name == "nt" else ""
            binary = pathlib.Path(tmp) / f"target{suffix}"
            compiled = _compile(SOURCE, binary, link=True, cwd=tmp)
            if compiled is None:
                self.skipTest("no C compiler found in CC or PATH")
            _assert_bounded(
                self, compiled, "strict C executable compilation", require_zero=True
            )

            cases = (
                ("empty", b""),
                ("malformed", b"\x00\xffinvalid\n"),
                ("bounded-large", (b"9" * 4096) + b"\n"),
            )
            for label, input_data in cases:
                with self.subTest(case=label):
                    result = _run([str(binary)], cwd=tmp, input_data=input_data)
                    _assert_bounded(
                        self,
                        result,
                        f"C main stdin case {label}",
                        require_zero=False,
                    )


if __name__ == "__main__":
    unittest.main()
'''


def _python_literal(value: Any) -> str:
    return pprint.pformat(value, sort_dicts=True, width=88)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _resolve_root(raw_root: str) -> Path:
    try:
        root = Path(raw_root).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise GenerationError(f"workspace root is unavailable: {exc}") from exc
    if not root.is_dir():
        raise GenerationError(f"workspace root is not a directory: {root}")
    return root


def _resolve_source(root: Path, raw_source: str) -> Path:
    candidate = Path(raw_source).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        source = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise GenerationError(f"source is unavailable: {exc}") from exc
    if not _inside(source, root):
        raise GenerationError("source escapes the workspace root")
    try:
        mode = source.stat().st_mode
    except OSError as exc:
        raise GenerationError(f"cannot inspect source: {exc}") from exc
    if not stat.S_ISREG(mode):
        raise GenerationError(f"source is not a regular file: {source}")
    if source.stat().st_size > MAX_SOURCE_BYTES:
        raise GenerationError(
            f"source exceeds {MAX_SOURCE_BYTES} bytes: {source}"
        )
    return source


def _safe_slug(relative_source: Path) -> str:
    pieces = []
    for part in relative_source.with_suffix("").parts:
        normalized = re.sub(r"[^A-Za-z0-9]+", "_", part).strip("_").lower()
        pieces.append(normalized or "source")
    slug = "__".join(pieces)
    if len(slug) <= 120:
        return slug
    digest = hashlib.sha256(relative_source.as_posix().encode("utf-8")).hexdigest()[:16]
    return f"{slug[:103].rstrip('_')}__{digest}"


def _resolve_output(
    root: Path, source: Path, raw_output: str | None
) -> Path:
    if raw_output is None:
        relative_source = source.relative_to(root)
        candidate = (
            root
            / "tests"
            / "generated"
            / f"test_{_safe_slug(relative_source)}_generated.py"
        )
    else:
        candidate = Path(raw_output).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate

    absolute = Path(os.path.abspath(candidate))
    try:
        resolved_parent = absolute.parent.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise GenerationError(f"cannot resolve output parent: {exc}") from exc
    output = resolved_parent / absolute.name
    if not _inside(output, root):
        raise GenerationError("output escapes the workspace root")
    if output.suffix.lower() != ".py":
        raise GenerationError("generated unittest output must end in .py")
    if output == source:
        raise GenerationError("output cannot replace the inspected source")
    return output


def _read_source(source: Path, language: str) -> str:
    try:
        if language == "python":
            with tokenize.open(source) as handle:
                return handle.read()
        return source.read_text(encoding="utf-8")
    except (OSError, SyntaxError, UnicodeError) as exc:
        raise GenerationError(f"cannot decode source: {exc}") from exc


def _annotation_text(annotation: ast.expr | None) -> str:
    if annotation is None:
        return ""
    try:
        return re.sub(r"\s+", "", ast.unparse(annotation))
    except (AttributeError, ValueError):
        return ""


def _default_family(default: ast.expr | None) -> str:
    if not isinstance(default, ast.Constant):
        return ""
    value = default.value
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, bytes):
        return "bytes"
    if value is None:
        return "unknown"
    return ""


def _parameter_family(
    name: str, annotation: str, default: ast.expr | None
) -> str:
    lowered = annotation.lower().replace("typing.", "")
    name_tokens = set(filter(None, re.split(r"[^a-z0-9]+", name.lower())))

    if any(token in lowered for token in ("binaryio", "bytesio", "textio", "iobase")):
        return "stream"
    if "path" in lowered or name_tokens.intersection(
        {"path", "file", "filename", "directory", "dir"}
    ):
        return "path"
    if "bool" in lowered or name.startswith(("is_", "has_", "should_")):
        return "bool"
    if "bytes" in lowered or "bytearray" in lowered:
        return "bytes"
    if re.search(r"(^|[^a-z])str([^a-z]|$)", lowered):
        return "str"
    if "dict" in lowered or "mapping" in lowered:
        return "dict"
    if "tuple" in lowered:
        return "tuple"
    if "set" in lowered and "frozenset" not in lowered:
        return "set"
    if any(token in lowered for token in ("list", "sequence", "iterable")):
        return "list"
    if "float" in lowered or "decimal" in lowered:
        return "float"
    if re.search(r"(^|[^a-z])int([^a-z]|$)", lowered):
        return "int"

    inferred_default = _default_family(default)
    if inferred_default:
        return inferred_default
    if name_tokens.intersection(
        {"count", "size", "length", "index", "offset", "limit", "number", "n"}
    ):
        return "int"
    if name_tokens.intersection({"text", "name", "key", "value", "query", "pattern"}):
        return "str"
    if name_tokens.intersection({"data", "items", "values", "array", "records", "rows"}):
        return "list"
    if name_tokens.intersection({"stream", "reader", "writer", "buffer"}):
        return "stream"
    return "unknown"


def _parameters(
    arguments: ast.arguments,
) -> tuple[list[dict[str, Any]], bool]:
    positional = [*arguments.posonlyargs, *arguments.args]
    defaults: list[ast.expr | None] = [
        None
    ] * (len(positional) - len(arguments.defaults)) + list(arguments.defaults)
    parameters: list[dict[str, Any]] = []

    for argument, default in zip(positional, defaults):
        annotation = _annotation_text(argument.annotation)
        parameters.append(
            {
                "name": argument.arg,
                "passing": "positional",
                "annotation": annotation,
                "family": _parameter_family(argument.arg, annotation, default),
                "required": default is None,
            }
        )
    for argument, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
        annotation = _annotation_text(argument.annotation)
        parameters.append(
            {
                "name": argument.arg,
                "passing": "keyword",
                "annotation": annotation,
                "family": _parameter_family(argument.arg, annotation, default),
                "required": default is None,
            }
        )
    return parameters, bool(arguments.vararg or arguments.kwarg)


def _inspect_python(text: str) -> dict[str, Any]:
    warnings: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        location = f"line {exc.lineno}" if exc.lineno else "unknown line"
        warnings.append(f"static parse failed at {location}: {exc.msg}")
        return {
            "interfaces": [],
            "cases": [],
            "warnings": warnings,
            "truncated": False,
        }

    definitions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                definitions[node.name] = node

    interfaces: list[dict[str, Any]] = []
    for node in sorted(definitions.values(), key=lambda item: item.lineno):
        if isinstance(node, ast.ClassDef):
            initializer = next(
                (
                    child
                    for child in node.body
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and child.name == "__init__"
                ),
                None,
            )
            if initializer is None:
                parameters: list[dict[str, Any]] = []
                variadic = False
            else:
                parameters, variadic = _parameters(initializer.args)
                if parameters and parameters[0]["name"] in {"self", "cls"}:
                    parameters = parameters[1:]
            methods = [
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not child.name.startswith("_")
            ]
            interfaces.append(
                {
                    "name": node.name,
                    "kind": "class",
                    "async": False,
                    "parameters": parameters,
                    "variadic": variadic,
                    "public_methods": methods[:20],
                }
            )
        else:
            parameters, variadic = _parameters(node.args)
            interfaces.append(
                {
                    "name": node.name,
                    "kind": "function",
                    "async": isinstance(node, ast.AsyncFunctionDef),
                    "parameters": parameters,
                    "variadic": variadic,
                    "public_methods": [],
                }
            )

    truncated = len(interfaces) > MAX_INTERFACES
    if truncated:
        warnings.append(
            f"interface report truncated from {len(interfaces)} to {MAX_INTERFACES}"
        )
        interfaces = interfaces[:MAX_INTERFACES]
    cases = _python_cases(interfaces)
    if len(cases) == MAX_SMOKE_CASES:
        warnings.append(f"smoke case generation capped at {MAX_SMOKE_CASES}")
    return {
        "interfaces": interfaces,
        "cases": cases,
        "warnings": warnings,
        "truncated": truncated,
    }


def _descriptor(family: str, profile: str) -> dict[str, str]:
    mapping = {
        "bool": {
            "baseline": "false",
            "null": "none",
            "maximum": "false",
            "malformed": "opaque",
        },
        "int": {
            "baseline": "zero-int",
            "null": "none",
            "maximum": "max-int",
            "malformed": "malformed-text",
        },
        "float": {
            "baseline": "zero-float",
            "null": "none",
            "maximum": "max-float",
            "malformed": "malformed-text",
        },
        "str": {
            "baseline": "empty-text",
            "null": "none",
            "maximum": "large-text",
            "malformed": "malformed-text",
        },
        "bytes": {
            "baseline": "empty-bytes",
            "null": "none",
            "maximum": "large-bytes",
            "malformed": "malformed-bytes",
        },
        "list": {
            "baseline": "empty-list",
            "null": "none",
            "maximum": "large-list",
            "malformed": "malformed-list",
        },
        "tuple": {
            "baseline": "empty-tuple",
            "null": "none",
            "maximum": "large-tuple",
            "malformed": "malformed-tuple",
        },
        "set": {
            "baseline": "empty-set",
            "null": "none",
            "maximum": "large-set",
            "malformed": "malformed-set",
        },
        "dict": {
            "baseline": "empty-dict",
            "null": "none",
            "maximum": "large-dict",
            "malformed": "malformed-dict",
        },
        "path": {
            "baseline": "empty-path",
            "null": "none",
            "maximum": "large-path",
            "malformed": "malformed-path",
        },
        "stream": {
            "baseline": "empty-stream",
            "null": "none",
            "maximum": "large-stream",
            "malformed": "malformed-stream",
        },
        "unknown": {
            "baseline": "none",
            "null": "none",
            "maximum": "opaque",
            "malformed": "malformed-bytes",
        },
    }
    return {"kind": mapping.get(family, mapping["unknown"])[profile]}


def _python_cases(interfaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    data_families = {
        "str",
        "bytes",
        "list",
        "tuple",
        "set",
        "dict",
        "path",
        "stream",
    }
    for interface in interfaces:
        parameters = interface["parameters"]
        profiles = ["baseline"]
        if parameters:
            profiles.extend(("null", "maximum"))
            if any(parameter["family"] in data_families for parameter in parameters):
                profiles.append("malformed")
        for profile in profiles:
            args = []
            kwargs = {}
            for parameter in parameters:
                value = _descriptor(parameter["family"], profile)
                if parameter["passing"] == "positional":
                    args.append(value)
                else:
                    kwargs[parameter["name"]] = value
            cases.append(
                {
                    "label": f"{interface['kind']}:{interface['name']}:{profile}",
                    "symbol": interface["name"],
                    "args": args,
                    "kwargs": kwargs,
                }
            )
            if len(cases) >= MAX_SMOKE_CASES:
                return cases
    return cases


def _strip_c_noncode(text: str) -> str:
    output = list(text)
    state = "code"
    index = 0
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and following == "/":
                output[index] = output[index + 1] = " "
                state = "line-comment"
                index += 2
                continue
            if char == "/" and following == "*":
                output[index] = output[index + 1] = " "
                state = "block-comment"
                index += 2
                continue
            if char == '"':
                output[index] = " "
                state = "string"
            elif char == "'":
                output[index] = " "
                state = "character"
        elif state == "line-comment":
            if char == "\n":
                state = "code"
            else:
                output[index] = " "
        elif state == "block-comment":
            if char == "*" and following == "/":
                output[index] = output[index + 1] = " "
                state = "code"
                index += 2
                continue
            if char != "\n":
                output[index] = " "
        elif state in {"string", "character"}:
            if char == "\\" and following:
                output[index] = " "
                if following != "\n":
                    output[index + 1] = " "
                index += 2
                continue
            terminator = '"' if state == "string" else "'"
            if char == terminator:
                output[index] = " "
                state = "code"
            elif char != "\n":
                output[index] = " "
        index += 1

    cleaned_lines: list[str] = []
    in_directive = False
    for line in "".join(output).splitlines(keepends=True):
        stripped = line.lstrip()
        if in_directive or stripped.startswith("#"):
            continuation = line.rstrip("\r\n").rstrip().endswith("\\")
            cleaned_lines.append(
                "".join("\n" if character == "\n" else " " for character in line)
            )
            in_directive = continuation
        else:
            cleaned_lines.append(line)
    return "".join(cleaned_lines)


def _c_function_before(cleaned: str, brace_index: int) -> dict[str, Any] | None:
    cursor = brace_index - 1
    while cursor >= 0 and cleaned[cursor].isspace():
        cursor -= 1
    if cursor < 0 or cleaned[cursor] != ")":
        return None

    closing = cursor
    depth = 1
    cursor -= 1
    while cursor >= 0:
        if cleaned[cursor] == ")":
            depth += 1
        elif cleaned[cursor] == "(":
            depth -= 1
            if depth == 0:
                break
        cursor -= 1
    if cursor < 0:
        return None

    opening = cursor
    name_match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", cleaned[:opening])
    if name_match is None:
        return None
    name = name_match.group(1)
    if name in {"if", "for", "while", "switch", "sizeof", "_Generic"}:
        return None

    segment_start = max(
        cleaned.rfind(";", 0, name_match.start()),
        cleaned.rfind("}", 0, name_match.start()),
        cleaned.rfind("{", 0, name_match.start()),
    )
    prefix = cleaned[segment_start + 1 : name_match.start()]
    if re.search(r"\btypedef\b", prefix) or "=" in prefix:
        return None
    parameters = re.sub(r"\s+", " ", cleaned[opening + 1 : closing]).strip()
    return {
        "name": name,
        "parameters": parameters,
        "internal": bool(re.search(r"\bstatic\b", prefix)),
    }


def _inspect_c(text: str) -> dict[str, Any]:
    cleaned = _strip_c_noncode(text)
    depth = 0
    discovered: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    for index, character in enumerate(cleaned):
        if character == "{":
            if depth == 0:
                candidate = _c_function_before(cleaned, index)
                if candidate is not None:
                    discovered[candidate["name"]] = candidate
            depth += 1
        elif character == "}":
            depth = max(0, depth - 1)

    public = [
        value
        for value in discovered.values()
        if not value["internal"] or value["name"] == "main"
    ]
    truncated = len(public) > MAX_INTERFACES
    if truncated:
        warnings.append(
            f"interface report truncated from {len(public)} to {MAX_INTERFACES}"
        )
        public = public[:MAX_INTERFACES]
    if not public:
        warnings.append(
            "no public C function definitions were recognized by lexical inspection"
        )
    return {
        "interfaces": public,
        "has_main": "main" in discovered,
        "warnings": warnings,
        "truncated": truncated,
    }


def _module_header(
    *,
    source_relative: str,
    root_from_output: str,
    timeout: float,
    max_output_bytes: int,
    limitations: Sequence[str],
) -> str:
    limitation_lines = "\n".join(f"- {item}" for item in limitations)
    return (
        "#!/usr/bin/env python3\n"
        '"""Generated deterministic regression smoke harness.\n\n'
        f"Source: {source_relative}\n\n"
        "Coverage limitations:\n"
        f"{limitation_lines}\n"
        '"""\n\n'
        "import json\n"
        "import math\n"
        "import os\n"
        "import pathlib\n"
        "import shlex\n"
        "import signal\n"
        "import subprocess\n"
        "import sys\n"
        "import tempfile\n"
        "import threading\n"
        "import unittest\n\n"
        f"ROOT_FROM_HARNESS = {_python_literal(root_from_output)}\n"
        f"SOURCE_RELATIVE = {_python_literal(source_relative)}\n"
        "WORKSPACE_ROOT = (\n"
        "    pathlib.Path(__file__).resolve().parent / ROOT_FROM_HARNESS\n"
        ").resolve()\n"
        "SOURCE = (WORKSPACE_ROOT / SOURCE_RELATIVE).resolve()\n"
        "try:\n"
        "    SOURCE.relative_to(WORKSPACE_ROOT)\n"
        "except ValueError as exc:\n"
        '    raise RuntimeError("source escapes the generated workspace root") from exc\n'
        f"TIMEOUT_SECONDS = {timeout!r}\n"
        f"MAX_OUTPUT_BYTES = {max_output_bytes}\n"
        f"LIMITATIONS = {_python_literal(list(limitations))}\n"
    )


def _render_python(
    *,
    source_relative: str,
    root_from_output: str,
    inspection: dict[str, Any],
    timeout: float,
    max_output_bytes: int,
) -> str:
    header = _module_header(
        source_relative=source_relative,
        root_from_output=root_from_output,
        timeout=timeout,
        max_output_bytes=max_output_bytes,
        limitations=PYTHON_LIMITATIONS,
    )
    metadata = (
        f"INTERFACES = {_python_literal(inspection['interfaces'])}\n"
        f"SMOKE_CASES = {_python_literal(inspection['cases'])}\n"
        f"INSPECTION_WARNINGS = {_python_literal(inspection['warnings'])}\n"
    )
    return (
        header
        + metadata
        + "\n"
        + textwrap.dedent(COMMON_RUNTIME).lstrip()
        + "\n"
        + textwrap.dedent(PYTHON_CHILDREN).lstrip()
        + "\n"
        + textwrap.dedent(PYTHON_TEST_BODY).lstrip()
    )


def _render_c(
    *,
    source_relative: str,
    root_from_output: str,
    inspection: dict[str, Any],
    timeout: float,
    max_output_bytes: int,
) -> str:
    header = _module_header(
        source_relative=source_relative,
        root_from_output=root_from_output,
        timeout=timeout,
        max_output_bytes=max_output_bytes,
        limitations=C_LIMITATIONS,
    )
    metadata = (
        "import shutil\n\n"
        f"C_INTERFACES = {_python_literal(inspection['interfaces'])}\n"
        f"HAS_MAIN = {inspection['has_main']!r}\n"
        f"INSPECTION_WARNINGS = {_python_literal(inspection['warnings'])}\n"
    )
    return (
        header
        + metadata
        + "\n"
        + textwrap.dedent(COMMON_RUNTIME).lstrip()
        + "\n"
        + textwrap.dedent(C_TEST_BODY).lstrip()
    )


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(directory, flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _atomic_write(output: Path, content: str, *, force: bool, root: Path) -> str:
    existed = output.exists() or output.is_symlink()
    if existed and not force:
        raise GenerationError(
            f"output exists; review it and pass --force to replace it: {output}"
        )
    if output.is_symlink():
        raise GenerationError("refusing to replace a symbolic-link output")
    if existed and not output.is_file():
        raise GenerationError("refusing to replace a non-file output")

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        parent = output.parent.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise GenerationError(f"cannot create output directory: {exc}") from exc
    if not _inside(parent, root):
        raise GenerationError("resolved output directory escapes the workspace root")
    output = parent / output.name

    descriptor = -1
    temporary_name = ""
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output.name}.", suffix=".tmp", dir=parent
        )
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            descriptor = -1
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_name, 0o644)

        if force:
            os.replace(temporary_name, output)
            temporary_name = ""
        else:
            try:
                os.link(temporary_name, output)
            except FileExistsError as exc:
                raise GenerationError(
                    f"output was created concurrently and was not replaced: {output}"
                ) from exc
            except OSError as exc:
                raise GenerationError(
                    "filesystem cannot provide atomic non-overwriting publication"
                ) from exc
            os.unlink(temporary_name)
            temporary_name = ""
        _fsync_directory(parent)
    except GenerationError:
        raise
    except OSError as exc:
        raise GenerationError(f"cannot publish generated harness: {exc}") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_name:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
    return "replaced" if existed else "created"


def _positive_timeout(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number") from exc
    if not 0.1 <= parsed <= 30.0:
        raise argparse.ArgumentTypeError("timeout must be between 0.1 and 30 seconds")
    return parsed


def _bounded_output(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("output limit must be an integer") from exc
    if not MIN_OUTPUT_BYTES <= parsed <= MAX_OUTPUT_BYTES:
        raise argparse.ArgumentTypeError(
            f"output limit must be between {MIN_OUTPUT_BYTES} and {MAX_OUTPUT_BYTES}"
        )
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Statically inspect one workspace-contained Python or C source file and "
            "atomically generate a deterministic unittest smoke harness."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("source", help="Python (.py) or C (.c) source path")
    parser.add_argument(
        "--root",
        required=True,
        help="workspace root containing the source and generated output",
    )
    parser.add_argument(
        "--output",
        help=(
            "output .py path; defaults to "
            "tests/generated/test_<source>_generated.py"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="atomically replace an existing regular output file",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_timeout,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="per-process timeout embedded in the generated harness",
    )
    parser.add_argument(
        "--max-output-bytes",
        type=_bounded_output,
        default=DEFAULT_OUTPUT_BYTES,
        help="stdout and stderr bytes retained per generated smoke process",
    )
    return parser


def generate(args: argparse.Namespace) -> dict[str, Any]:
    root = _resolve_root(args.root)
    source = _resolve_source(root, args.source)
    extension = source.suffix.lower()
    if extension == ".py":
        language = "python"
    elif extension == ".c":
        language = "c"
    else:
        raise GenerationError("source must have a .py or .c extension")

    output = _resolve_output(root, source, args.output)
    text = _read_source(source, language)
    source_relative = source.relative_to(root).as_posix()
    root_from_output = os.path.relpath(root, output.parent)

    if language == "python":
        inspection = _inspect_python(text)
        content = _render_python(
            source_relative=source_relative,
            root_from_output=root_from_output,
            inspection=inspection,
            timeout=args.timeout,
            max_output_bytes=args.max_output_bytes,
        )
        cases = [case["label"] for case in inspection["cases"]]
        limitations = list(PYTHON_LIMITATIONS)
    else:
        inspection = _inspect_c(text)
        content = _render_c(
            source_relative=source_relative,
            root_from_output=root_from_output,
            inspection=inspection,
            timeout=args.timeout,
            max_output_bytes=args.max_output_bytes,
        )
        cases = (
            ["strict-compile", "main-empty", "main-malformed", "main-bounded-large"]
            if inspection["has_main"]
            else ["strict-compile"]
        )
        limitations = list(C_LIMITATIONS)

    status = _atomic_write(output, content, force=args.force, root=root)
    return {
        "status": status,
        "language": language,
        "source": source_relative,
        "output": output.relative_to(root).as_posix(),
        "interfaces": inspection["interfaces"],
        "smoke_cases": cases,
        "inspection_warnings": inspection["warnings"],
        "coverage_limitations": limitations,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        report = generate(args)
    except GenerationError as exc:
        print(
            json.dumps(
                {"status": "error", "error": str(exc)},
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 1

    print(
        json.dumps(
            report,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
