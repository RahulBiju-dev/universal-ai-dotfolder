#!/usr/bin/env python3
"""Print a deterministic inventory of the dotfolder scaffold.

Demonstrates the executable-utility contract every skill utility follows:
standard library only, explicit argument vector, bounded output, deterministic
ordering, and distinct exit codes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REGISTRIES = ("agents", "commands", "workflows", "rules", "skills")
SUFFIXES = {"agents": ".md", "commands": ".md", "workflows": ".md", "rules": ".mdc"}

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_MISSING = 3


def is_template(name: str) -> bool:
    """Authoring templates are excluded from every registry count."""
    return name.startswith("_")


def collect(root: Path, registry: str, limit: int) -> tuple[list[str], int]:
    directory = root / registry
    if not directory.is_dir():
        return [], 0
    if registry == "skills":
        entries = [path.name for path in directory.iterdir() if path.is_dir()]
    else:
        entries = [
            path.stem for path in directory.glob(f"*{SUFFIXES[registry]}") if path.is_file()
        ]
    kept = sorted(name for name in entries if not is_template(name))
    return kept[:limit], max(0, len(kept) - limit)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="workspace root to inventory")
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="maximum entries printed per registry",
    )
    args = parser.parse_args(argv)

    if args.limit < 1:
        print("--limit must be at least 1", file=sys.stderr)
        return EXIT_USAGE

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"root is not a directory: {root}", file=sys.stderr)
        return EXIT_MISSING

    for registry in REGISTRIES:
        names, truncated = collect(root, registry, args.limit)
        print(f"{registry}: {len(names) + truncated}")
        for name in names:
            print(f"  {name}")
        if truncated:
            print(f"  truncated: {truncated} more")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
