#!/usr/bin/env python3
from __future__ import annotations
import os, shutil
from pathlib import Path
import lib


def link_or_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink(): return
    try:
        rel = os.path.relpath(src, dst.parent)
        dst.symlink_to(rel, target_is_directory=True)
        print(f"linked {dst} -> {rel}")
    except OSError:
        shutil.copytree(src, dst); print(f"copied {src} -> {dst}")


def main() -> int:
    root = lib.root_dir()
    link_or_copy(root / ".codex" / "skills", root / ".agents" / "skills")
    print("setup links ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
