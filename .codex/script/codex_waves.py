#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
import lib, codex_state, codex_lanes


def current() -> dict:
    cur = codex_state.current()
    if not cur: raise SystemExit("workflow not initialized")
    return cur


def cfg() -> dict:
    data = lib.read_json(lib.find_codex() / "state" / "budget.json", {})
    maw = data.get("maw", {}) if isinstance(data, dict) else {}
    return {"max_lanes": int(maw.get("max_lanes_per_wave", 6)),
            "warn": int(maw.get("max_total_lanes_warn", 24)),
            "hard_global_cap": bool(maw.get("hard_global_cap", False))}


def to_num(value) -> int:
    if isinstance(value, int): return value
    text = str(value or "1").upper()
    return int(text[1:] if text.startswith("W") else text)


def to_wave(num: int | str) -> str:
    return f"W{to_num(num):03d}"


def rows(cur: dict) -> list[dict]: return codex_lanes.read_jsonl(codex_lanes.lane_path(cur))


def assign_rows(items: list[dict]) -> list[dict]:
    limit = max(1, cfg()["max_lanes"]); counts: dict[int, int] = {}; by_id = {}
    for row in items:
        deps = row.get("deps", [])
        dep_wave = max([to_num(by_id.get(x, 0)) for x in deps] or [0])
        num = max(1, dep_wave + 1)
        while counts.get(num, 0) >= limit: num += 1
        row["wave"] = to_wave(num); counts[num] = counts.get(num, 0) + 1
        by_id[row["id"]] = row["wave"]
    return items


def assign_current() -> list[dict]:
    cur = current(); items = assign_rows(rows(cur))
    codex_lanes.write_jsonl(codex_lanes.lane_path(cur), items)
    codex_state.write_tasks(cur, codex_state.read_tasks(cur))
    codex_state.events(cur, "waves_assign", {"waves": wave_count(items)})
    return items


def wave_count(items: list[dict]) -> int:
    return max([to_num(x.get("wave", "W001")) for x in items] or [0])


def summary(items: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for row in items:
        key = row.get("wave", "W001")
        bucket = out.setdefault(key, {"lanes": 0, "agents": {}, "todo": 0, "done": 0})
        bucket["lanes"] += 1
        ag = row.get("agent", "none")
        bucket["agents"][ag] = bucket["agents"].get(ag, 0) + 1
        if row.get("status") in {"done", "merged"}: bucket["done"] += 1
        else: bucket["todo"] += 1
    return {"waves": out, "count": len(out), "total_lanes": len(items), "budget": cfg()}


def cmd_assign(args) -> int:
    data = summary(assign_current())
    if data["total_lanes"] > data["budget"]["warn"]:
        data["warning"] = "large_maw_plan_review_needed"
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0


def cmd_plan(args) -> int:
    cur = current(); items = rows(cur)
    if not all("wave" in x for x in items): items = assign_rows(items)
    print(json.dumps(summary(items), ensure_ascii=False, indent=2)); return 0


def cmd_next(args) -> int:
    cur = current(); items = rows(cur)
    if not all("wave" in x for x in items): items = assign_current()
    for num in range(1, wave_count(items) + 1):
        chunk = [x for x in items if to_num(x.get("wave", 1)) == num]
        if any(x.get("status") not in {"done", "merged"} for x in chunk):
            print(to_wave(num)); return 0
    print("done"); return 0


def cmd_prompt(args) -> int:
    cur = current(); items = rows(cur)
    if not all("wave" in x for x in items): items = assign_current()
    wave = to_wave(args.wave or cmd_value_next())
    print(f"Run {wave} only. Then merge, verify, and continue.")
    for row in items:
        if row.get("wave", "W001") == wave:
            print(f"{row['id']} {row['agent']} {row['title']} task={row['task_id']}")
    return 0


def cmd_value_next() -> str:
    cur = current(); items = rows(cur)
    for num in range(1, wave_count(items) + 1):
        if any(x.get("status") not in {"done", "merged"}
               for x in items if to_num(x.get("wave", 1)) == num):
            return to_wave(num)
    return "done"


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("assign"); sub.add_parser("plan"); sub.add_parser("next")
    pr = sub.add_parser("prompt"); pr.add_argument("--wave", default="")
    args = p.parse_args(); return globals()["cmd_" + args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
