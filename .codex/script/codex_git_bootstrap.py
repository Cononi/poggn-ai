#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess
import lib


def git_ok() -> bool:
    return lib.has_cmd("git")


def inside_repo() -> bool:
    if not git_ok(): return False
    return lib.run(["git", "rev-parse", "--is-inside-work-tree"]).returncode == 0


def doctor() -> int:
    if not git_ok():
        print("git missing: ask install or manual install")
        return 2
    if not inside_repo():
        print("not a git repo: run ensure to git init")
        return 1
    print("git repo ok")
    return 0


def ensure() -> int:
    if not git_ok():
        print("git missing: install git first")
        return 2
    if inside_repo():
        print("git repo already exists")
        return 0
    lib.run(["git", "init"], check=True)
    print("git init ok")
    return 0


def remote_add(url: str, name: str) -> int:
    ensure(); proc = lib.run(["git", "remote", "get-url", name])
    if proc.returncode == 0:
        print(f"remote {name} exists: {proc.stdout.strip()}")
        return 0
    lib.run(["git", "remote", "add", name, url], check=True)
    print(f"remote {name} added")
    return 0


def repo_create(args) -> int:
    ensure()
    if args.provider == "github":
        if not lib.has_cmd("gh"): raise SystemExit("gh CLI missing")
        cmd = ["gh", "repo", "create", args.name, "--source", ".", "--remote", args.remote]
        cmd.append("--" + args.visibility)
        if args.push: cmd.append("--push")
    else:
        if not lib.has_cmd("glab"): raise SystemExit("glab CLI missing")
        cmd = ["glab", "repo", "create", args.name, "--remoteName", args.remote]
        cmd.append("--" + args.visibility)
    subprocess.run(cmd, check=True)
    print("repo create command done")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor"); sub.add_parser("ensure")
    r = sub.add_parser("remote-add"); r.add_argument("--url", required=True); r.add_argument("--name", default="origin")
    c = sub.add_parser("repo-create"); c.add_argument("--provider", choices=["github", "gitlab"], required=True)
    c.add_argument("--name", required=True); c.add_argument("--visibility", choices=["private", "public"], default="private")
    c.add_argument("--remote", default="origin"); c.add_argument("--push", action="store_true")
    args = p.parse_args()
    if args.cmd == "doctor": return doctor()
    if args.cmd == "ensure": return ensure()
    if args.cmd == "remote-add": return remote_add(args.url, args.name)
    return repo_create(args)


if __name__ == "__main__":
    raise SystemExit(main())
