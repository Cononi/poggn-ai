#!/usr/bin/env python3
from __future__ import annotations
import argparse, inspect, json, sys, tempfile, traceback
from pathlib import Path


def run_tests() -> dict:
    """Run trusted .codex test_*.py files with the supported fixture set."""
    root = Path(__file__).resolve().parents[2]
    script_dir = root / ".codex" / "script"
    test_dir = root / ".codex" / "tests"
    sys.path.insert(0, str(script_dir))
    failures = []
    count = 0
    for test_file in sorted(test_dir.glob("test_*.py")):
        ns = {"__file__": str(test_file)}
        code = test_file.read_text(encoding="utf-8")
        exec(compile(code, str(test_file), "exec"), ns)
        tests = sorted((k, v) for k, v in ns.items()
                       if k.startswith("test_") and callable(v))
        for name, fn in tests:
            params = inspect.signature(fn).parameters
            unsupported = [p for p in params if p != "tmp_path"]
            test_name = f"{test_file.name}::{name}"
            if unsupported:
                failures.append({"test": test_name,
                                 "error": f"unsupported fixtures: {unsupported}"})
                continue
            with tempfile.TemporaryDirectory() as tmp:
                kwargs = {"tmp_path": Path(tmp)} if "tmp_path" in params else {}
                try:
                    fn(**kwargs)
                    count += 1
                except Exception as exc:
                    failures.append({"test": test_name, "error": repr(exc),
                                     "trace": traceback.format_exc(limit=4)})
    return {"ok": not failures, "count": count, "failures": failures}


def main() -> int:
    """Parse runner options and return a shell-friendly test status code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--for-ai", action="store_true")
    args = parser.parse_args()
    data = run_tests()
    if args.for_ai and data["failures"]:
        data["failures"] = data["failures"][:5]
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if data["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
