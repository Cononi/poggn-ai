#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(cwd or ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def require_worktree(path: Path) -> int:
    if not path.exists():
        print(f"worktree path not found: {path}", file=sys.stderr)
        return 2
    proc = run(["git", "rev-parse", "--is-inside-work-tree"], cwd=path)
    if proc.stdout.strip() != "true":
        print(f"not a git worktree: {path}", file=sys.stderr)
        return 2
    return 0


def collect(path: Path) -> tuple[int, str, str, str]:
    status = run(["git", "status", "--porcelain=v2", "--branch"], cwd=path)
    head = run(["git", "log", "-1", "--oneline"], cwd=path)
    upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], cwd=path)
    return status.returncode, status.stdout, head.stdout.strip(), upstream.stdout.strip()


def is_clean(status: str) -> bool:
    return all(line.startswith("#") for line in status.splitlines() if line.strip())


def status_cmd(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    rc = require_worktree(path)
    if rc:
        return rc
    _, status, head, upstream = collect(path)
    print(f"path: {path}")
    print(f"head: {head or 'unknown'}")
    print(f"upstream: {upstream or 'none'}")
    print(f"clean: {'yes' if is_clean(status) else 'no'}")
    print("status:")
    print(status.rstrip() or "<empty>")
    return 0


def remove_cmd(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    rc = require_worktree(path)
    if rc:
        return rc
    _, status, head, upstream = collect(path)
    if not is_clean(status):
        print("refusing to remove: worktree is not clean", file=sys.stderr)
        return 3
    if args.require_upstream and not upstream:
        print("refusing to remove: upstream is not configured", file=sys.stderr)
        return 3
    print(f"path: {path}")
    print(f"head: {head or 'unknown'}")
    print(f"upstream: {upstream or 'none'}")
    if not args.execute:
        print(f"dry-run: git worktree remove {path}")
        print("dry-run: git worktree prune --dry-run")
        return 0
    proc = run(["git", "worktree", "remove", str(path)])
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    if proc.returncode:
        return proc.returncode
    prune = run(["git", "worktree", "prune", "--dry-run"])
    if prune.stdout.strip():
        print(prune.stdout.strip())
    return prune.returncode


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Pogo worktree cleanup helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("path")
    s.set_defaults(fn=status_cmd)
    r = sub.add_parser("remove")
    r.add_argument("path")
    r.add_argument("--execute", action="store_true")
    r.add_argument("--allow-no-upstream", dest="require_upstream", action="store_false")
    r.set_defaults(fn=remove_cmd, require_upstream=True)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
