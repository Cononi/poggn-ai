#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path
import lib


def git(args: list[str]) -> int:
    proc = lib.run(["git", *args], cwd=lib.root_dir())
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip())
    return proc.returncode


def task_tool(args: list[str]) -> int:
    script = lib.find_codex() / "script" / "codex_task_git.py"
    proc = lib.run([sys.executable, str(script), *args], cwd=lib.root_dir())
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip())
    return proc.returncode


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("diff"); d.add_argument("base", nargs="?", default="main")
    h = sub.add_parser("history"); h.add_argument("path", nargs="?")
    r = sub.add_parser("rollback"); r.add_argument("commit")
    t = sub.add_parser("task-revert"); t.add_argument("task_id")
    f = sub.add_parser("task-files"); f.add_argument("task_id")
    args = p.parse_args()
    if args.cmd == "diff":
        return git(["diff", f"{args.base}...HEAD"])
    if args.cmd == "history":
        cmd = ["log", "--oneline", "--decorate", "--graph", "--all"]
        if args.path:
            cmd += ["--", args.path]
        return git(cmd)
    if args.cmd == "rollback":
        return git(["revert", "--no-edit", args.commit])
    if args.cmd == "task-files":
        return task_tool(["files", args.task_id])
    return task_tool(["revert-task", args.task_id])


if __name__ == "__main__":
    raise SystemExit(main())
