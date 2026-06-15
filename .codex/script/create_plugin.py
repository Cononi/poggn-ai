#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import lib


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("name"); args = p.parse_args()
    root = lib.root_dir() / ".codex" / "plugins" / lib.safe_slug(args.name)
    meta = root / ".codex-plugin"; skill = root / "skills" / "starter"
    meta.mkdir(parents=True, exist_ok=True); skill.mkdir(parents=True, exist_ok=True)
    (meta / "plugin.json").write_text(json.dumps({"name": args.name}, indent=2) + "\n")
    (skill / "SKILL.md").write_text("---\nname: starter\ndescription: Starter skill.\n---\n\n# Starter\n")
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
