#!/usr/bin/env python3
from __future__ import annotations
import argparse
import lib


def path():
    return lib.find_codex() / "state" / "edit_mode.json"


def set_mode(mode: str, reason: str) -> None:
    lib.write_json(path(), {"mode": mode, "reason": reason, "updated_at": lib.now()})


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    on = sub.add_parser("on"); on.add_argument("--reason", default="codex maintenance")
    off = sub.add_parser("off"); off.add_argument("--reason", default="project work")
    sub.add_parser("status"); args = p.parse_args()
    if args.cmd == "on": set_mode("codex", args.reason)
    elif args.cmd == "off": set_mode("project", args.reason)
    print(lib.read_json(path(), {"mode": "project"}).get("mode", "project"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
