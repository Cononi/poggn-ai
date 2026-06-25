#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_CHECK = "pogo-policy"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def remote_slug(remote: str) -> tuple[str, str]:
    result = run("git", "remote", "get-url", remote)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or f"unable to read remote {remote}")
    url = result.stdout.strip()
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group("owner"), match.group("repo")
    raise SystemExit(f"unsupported GitHub remote URL: {url}")


def default_branch(remote: str) -> str:
    result = run("git", "symbolic-ref", f"refs/remotes/{remote}/HEAD")
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().rsplit("/", 1)[-1]
    return "main"


def protection_payload() -> dict:
    return {
        "required_status_checks": {
            "strict": True,
            "contexts": [REQUIRED_CHECK],
        },
        "enforce_admins": True,
        "required_pull_request_reviews": None,
        "restrictions": None,
        "required_linear_history": False,
        "allow_force_pushes": False,
        "allow_deletions": False,
        "block_creations": False,
        "required_conversation_resolution": False,
        "lock_branch": False,
        "allow_fork_syncing": True,
    }


def apply_protection(owner: str, repo: str, branch: str, payload: dict) -> int:
    cmd = [
        "gh",
        "api",
        "--method",
        "PUT",
        f"repos/{owner}/{repo}/branches/{branch}/protection",
        "--input",
        "-",
    ]
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        input=json.dumps(payload),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
        return result.returncode
    print(f"branch-protection: applied {owner}/{repo}@{branch} requiring {REQUIRED_CHECK} without PR reviews")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure GitHub branch protection for pogo policy checks.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    owner, repo = remote_slug(args.remote)
    branch = args.branch or default_branch(args.remote)
    payload = protection_payload()
    print(f"target={owner}/{repo}@{branch}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not args.apply:
        print("branch-protection: dry-run")
        return 0
    return apply_protection(owner, repo, branch, payload)


if __name__ == "__main__":
    raise SystemExit(main())
