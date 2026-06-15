#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
import codex_event_bus, codex_lanes, codex_state, codex_trace_view

DONE = {"done", "merged"}
FINAL = {"final_refactor", "final_security"}


def cur() -> dict:
    data = codex_state.current()
    if not data: raise SystemExit("workflow not initialized")
    return data


def lanes(c: dict) -> list[dict]:
    return codex_lanes.read_jsonl(codex_lanes.lane_path(c))


def code_changed(c: dict) -> bool:
    for row in codex_trace_view.commits(c):
        for item in row.get("files", []):
            path = item.split("\t")[-1]
            if path.endswith((".java", ".kt", ".py", ".go", ".rs", ".ts",
                              ".tsx", ".js", ".jsx", ".sql")):
                return True
    return False


def ready(c: dict) -> tuple[bool, list[str]]:
    rows = [x for x in lanes(c) if x.get("stage") not in FINAL]
    missing = [x["id"] for x in rows if x.get("status") not in DONE]
    return not missing, missing


def exists(rows: list[dict], stage: str) -> bool:
    return any(x.get("stage") == stage for x in rows)


def row_for(c: dict, deps: list[str], stage: str, agent: str, title: str) -> dict:
    return {"id": "FINAL", "title": title, "agent": agent, "feature": "final",
            "stage": stage, "wave": "W999", "deps": deps, "root_lane_id": "FINAL"}


def apply_final(args) -> dict:
    c = cur(); rows = lanes(c); ok, missing = ready(c)
    if not ok:
        return {"created": [], "blocked_by": missing}
    if not code_changed(c) and not args.force:
        return {"created": [], "reason": "no code changes"}
    deps = [x["id"] for x in rows if x.get("status") in DONE]
    tasks = codex_state.read_tasks(c); made = []
    if not exists(rows, "final_refactor") and not args.security_only:
        r = row_for(c, deps, "final_refactor", "refactor", "Final refactor sweep")
        made.append(codex_event_bus.create(c, tasks, rows, r, "final_refactor",
                                           "refactor", r["title"], deps))
        deps = [made[-1]["id"]] if made[-1] else deps
    if not exists(rows, "final_security"):
        r = row_for(c, deps, "final_security", "security", "Final security sweep")
        made.append(codex_event_bus.create(c, tasks, rows, r, "final_security",
                                           "security", r["title"], deps))
    codex_state.write_tasks(c, codex_state.read_tasks(c))
    return {"created": [x for x in made if x]}


def cmd_status(args) -> int:
    c = cur(); ok, missing = ready(c)
    print(json.dumps({"ready": ok, "missing": missing,
                      "code_changed": code_changed(c)}, ensure_ascii=False, indent=2))
    return 0


def cmd_apply(args) -> int:
    print(json.dumps(apply_final(args), ensure_ascii=False, indent=2)); return 0


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    a = sub.add_parser("apply"); a.add_argument("--force", action="store_true")
    a.add_argument("--security-only", action="store_true")
    a.add_argument("--for-ai", action="store_true")
    args = p.parse_args(); return globals()["cmd_" + args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
