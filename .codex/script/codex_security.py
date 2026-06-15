#!/usr/bin/env python3
from __future__ import annotations
import argparse, re, subprocess
from pathlib import Path
import lib

SKIP = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}
PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("openai-key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("generic-token", re.compile(r'(?i)(token|secret|password)\s*[:=]\s*[\'"]?[^\'"\s]{12,}')),
]


def git_files(root: Path, staged: bool, base: str) -> list[Path]:
    if staged:
        cmd = ["git", "diff", "--cached", "--name-only"]
    elif base:
        cmd = ["git", "diff", "--name-only", f"{base}..HEAD"]
    else:
        cmd = ["git", "diff", "--name-only", "HEAD"]
    p = subprocess.run(cmd, cwd=str(root), text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        return []
    return [root / x for x in p.stdout.splitlines() if x.strip()]


def files(root: Path, staged: bool = False, base: str = ""):
    rows = git_files(root, staged, base) if staged or base else []
    scan = rows or list(root.rglob("*"))
    for path in scan:
        if any(part in SKIP for part in path.parts):
            continue
        if path.is_file() and path.stat().st_size < 500_000:
            yield path


def scan(root: Path, staged: bool = False, base: str = "") -> list[str]:
    hits = []
    for path in files(root, staged, base):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            continue
        for name, rx in PATTERNS:
            if rx.search(text):
                hits.append(f"{path.relative_to(root)}: {name}")
    return hits


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("command", choices=["gate", "scan"])
    p.add_argument("--cwd", default=""); p.add_argument("--staged", action="store_true")
    p.add_argument("--base", default="")
    args = p.parse_args(); root = Path(args.cwd).resolve() if args.cwd else lib.root_dir()
    hits = scan(root, args.staged, args.base)
    if hits:
        print("\n".join(hits)); return 2
    print("security gate ok"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
