#!/usr/bin/env python3
from __future__ import annotations
import runpy, sys
from pathlib import Path


def find_codex() -> Path:
    cur = Path(__file__).resolve()
    for item in (cur, *cur.parents):
        if item.name == ".codex":
            return item
    raise SystemExit(0)


def main() -> int:
    codex = find_codex()
    sys.path.insert(0, str(codex / "script"))
    sys.argv = [str(codex / "script" / "hook_context.py"), *sys.argv[1:]]
    runpy.run_path(str(codex / "script" / "hook_context.py"), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
