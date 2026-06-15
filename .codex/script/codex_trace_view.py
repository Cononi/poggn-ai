#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path


def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x]


def lanes(cur: dict) -> list[dict]:
    return jsonl(Path(cur["path"]) / "lanes.jsonl")


def commits(cur: dict) -> list[dict]:
    return jsonl(Path(cur["path"]) / "commits.jsonl")


def waves(cur: dict) -> list[dict]:
    return jsonl(Path(cur["path"]) / "waves.jsonl")


def by_task(rows: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(row.get("task_id", ""), []).append(row)
    return out


def short_path(path: str, max_len: int = 58) -> str:
    return path if len(path) <= max_len else "..." + path[-max_len + 3:]


def value_text(value, limit: int = 180) -> str:
    if isinstance(value, list):
        value = "; ".join(str(x) for x in value if x)
    elif value is None:
        value = ""
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def fallback_purpose(item: dict) -> str:
    stage = item.get("stage", "implement")
    feature = item.get("feature", "work")
    agent = item.get("agent", "agent")
    if stage == "foundation":
        return "요청을 구현 전에 public contract, 보안, 검증 기준으로 고정합니다."
    if stage == "implement":
        return f"{feature} 기능의 {agent} 책임을 구현합니다."
    return f"{feature} 기능의 {agent} 단계로 구현 결과를 검증합니다."


def fallback_acceptance(item: dict) -> str:
    stage = item.get("stage", "implement")
    if stage == "foundation":
        return "범위, 계약, 보안 경계, lane 완료 기준이 명확합니다."
    if stage == "implement":
        return "사용자 시나리오, owner files, 테스트, 보안 기준을 충족합니다."
    return "실패 원인, blocker, 남은 위험을 분리해 보고합니다."


def contract_lines(item: dict, indent: str = "  ") -> list[str]:
    purpose = value_text(item.get("purpose") or fallback_purpose(item))
    acceptance = value_text(item.get("acceptance") or fallback_acceptance(item))
    non_goals = value_text(item.get("non_goals"), 160)
    out = [f"{indent}purpose:{purpose}", f"{indent}acceptance:{acceptance}"]
    if non_goals:
        out.append(f"{indent}non_goals:{non_goals}")
    return out


def file_parts(files: list[str], limit: int = 8) -> tuple[str, list[str]]:
    counts = {"A": 0, "M": 0, "D": 0, "R": 0, "?": 0}; shown = []
    for raw in files:
        parts = raw.split("\t"); code = parts[0][:1] if parts else "?"
        code = code if code in counts else "?"; counts[code] += 1
        path = parts[-1] if len(parts) > 1 else raw
        if len(shown) < limit:
            shown.append(f"{code} {short_path(path)}")
    summary = " ".join(f"{k}{v}" for k, v in counts.items() if v)
    if len(files) > limit:
        shown.append(f"+{len(files) - limit} more files (showing {limit}/{len(files)} total)")
    return summary or "no-file", shown


def task_done(task: dict, task_lanes: list[dict], task_commits: list[dict]) -> bool:
    if task.get("status") != "done":
        return False
    if task_lanes:
        ok = all(x.get("status") in {"done", "merged"} for x in task_lanes)
        return ok and bool(task_commits)
    return bool(task.get("commits") or task_commits)


def agent_rows(tasks: list[dict], lane_map: dict, commit_map: dict) -> list[str]:
    agents: dict[str, dict] = {}
    for task in tasks:
        name = task.get("agent", "none")
        row = agents.setdefault(name, {"tasks": 0, "done": 0, "commits": 0, "lanes": 0, "stages": set()})
        tl = lane_map.get(task["id"], []); tc = commit_map.get(task["id"], [])
        row["tasks"] += 1; row["commits"] += len(tc); row["lanes"] += len(tl)
        if task.get("stage"): row["stages"].add(task.get("stage"))
        if task_done(task, tl, tc):
            row["done"] += 1
    lines = ["", "## agents"]
    for name in sorted(agents):
        row = agents[name]
        stage = ",".join(sorted(row.get("stages", []))) or "-"
        lines.append(f"- {name} tasks:{row['done']}/{row['tasks']} "
                     f"commits:{row['commits']} lanes:{row['lanes']} "
                     f"stages:{stage}")
    return lines



def wave_rows(lanes_rows: list[dict]) -> list[str]:
    waves: dict[str, dict] = {}
    for row in lanes_rows:
        name = row.get("wave", "W001")
        item = waves.setdefault(name, {"lanes": 0, "done": 0, "agents": set()})
        item["lanes"] += 1; item["agents"].add(row.get("agent", ""))
        if row.get("status") in {"done", "merged"}: item["done"] += 1
    lines = ["", "## waves"]
    for name in sorted(waves):
        row = waves[name]; agents = ",".join(sorted(row["agents"]))
        lines.append(f"- {name} lanes:{row['done']}/{row['lanes']} agents:{agents}")
    return lines

def task_lines(task: dict, tl: list[dict], tc: list[dict]) -> list[str]:
    mark = "x" if task_done(task, tl, tc) else " "
    skills = ",".join(task.get("skills", [])); tid = task["id"]
    lane_done = sum(1 for x in tl if x.get("status") in {"done", "merged"})
    lane_text = f" lanes:{lane_done}/{len(tl)}" if tl else ""
    wave = task.get("wave", "")
    stage = task.get("stage", "")
    head = f"- [{mark}] {tid} {task['title']} [{task.get('agent','')}] {skills}"
    if stage: head += f" stage:{stage}"
    lines = [head + (f" wave:{wave}" if wave else "")]
    lines.append(f"  commits:{len(tc)}{lane_text}")
    lines += contract_lines(task, "  ")
    for lane in tl:
        lm = "x" if lane.get("status") in {"done", "merged"} else " "
        tail = f" last:{lane.get('commit')}" if lane.get("commit") else ""
        wave = f" wave:{lane.get('wave')}" if lane.get('wave') else ""
        stage = f" stage:{lane.get('stage')}" if lane.get("stage") else ""
        deps = ",".join(lane.get("deps", [])) or "-"
        wname = f" worker:{lane.get('worker_name')}" if lane.get('worker_name') else ""
        lines.append(f"  - [{lm}] {lane['id']} {lane['agent']} {lane['title']}"
                     f"{stage}{wave} deps:{deps}{wname}{tail}")
        lines += contract_lines(lane, "    ")
    for row in tc:
        summary, shown = file_parts(row.get("files", []))
        lines.append(f"  - commit {row.get('short')} lane:{row.get('lane_id') or '-'} {summary}")
        for item in shown:
            lines.append(f"    - {item}")
    return lines


def render(cur: dict, tasks: list[dict]) -> None:
    lane_rows = lanes(cur); commit_rows = commits(cur)
    lane_map = by_task(lane_rows); commit_map = by_task(commit_rows)
    done = sum(1 for t in tasks if task_done(t, lane_map.get(t["id"], []),
                                              commit_map.get(t["id"], [])))
    lines = ["# TASKS", "", f"title: {cur.get('title')}",
             f"branch: {cur.get('branch')}", f"base: {cur.get('base_branch')}",
             f"workflow: {cur.get('workflow')}", f"phase: {cur.get('phase')}",
             f"run_version: {cur.get('run_version')}",
             f"project_version: {cur.get('project_version')}",
             f"next_version: {cur.get('next_version')}",
             f"created_at: {cur.get('created_at')}",
             f"progress: {done}/{len(tasks)}"]
    lines += wave_rows(lane_rows)
    lines += agent_rows(tasks, lane_map, commit_map)
    lines += ["", "## tasks"]
    for task in tasks:
        lines += task_lines(task, lane_map.get(task["id"], []), commit_map.get(task["id"], []))
    (Path(cur["path"]) / "TASKS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
