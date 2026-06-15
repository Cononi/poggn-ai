#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import lib


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


LABELS = {
    "ko": {
        "title": "제목", "branch": "브랜치", "base": "기준",
        "workflow": "워크플로", "phase": "단계", "run_version": "실행버전",
        "project_version": "프로젝트버전", "next_version": "다음버전",
        "created_at": "생성시각", "progress": "진행률", "waves": "웨이브",
        "agents": "에이전트", "tasks": "태스크", "commits": "커밋",
        "lanes": "레인", "stages": "단계", "purpose": "목적",
        "acceptance": "완료기준", "non_goals": "제외범위",
        "worker": "작업자", "last": "마지막", "deps": "의존성",
        "lane": "레인", "stage": "단계", "wave": "웨이브",
        "commit": "커밋", "more_files": "외 {hidden}개 파일 더 있음 (표시 {shown}/{total} 전체)",
        "no_file": "파일 없음",
    },
    "en": {
        "title": "title", "branch": "branch", "base": "base",
        "workflow": "workflow", "phase": "phase", "run_version": "run_version",
        "project_version": "project_version", "next_version": "next_version",
        "created_at": "created_at", "progress": "progress", "waves": "waves",
        "agents": "agents", "tasks": "tasks", "commits": "commits",
        "lanes": "lanes", "stages": "stages", "purpose": "purpose",
        "acceptance": "acceptance", "non_goals": "non_goals",
        "worker": "worker", "last": "last", "deps": "deps",
        "lane": "lane", "stage": "stage", "wave": "wave",
        "commit": "commit", "more_files": "+{hidden} more files (showing {shown}/{total} total)",
        "no_file": "no-file",
    },
}


def current_labels() -> dict:
    return LABELS.get(lib.language(), LABELS["ko"])


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
    labels = current_labels()
    purpose = value_text(item.get("purpose") or fallback_purpose(item))
    acceptance = value_text(item.get("acceptance") or fallback_acceptance(item))
    non_goals = value_text(item.get("non_goals"), 160)
    out = [f"{indent}{labels['purpose']}:{purpose}", f"{indent}{labels['acceptance']}:{acceptance}"]
    if non_goals:
        out.append(f"{indent}{labels['non_goals']}:{non_goals}")
    return out


def file_parts(files: list[str], limit: int = 8) -> tuple[str, list[str]]:
    labels = current_labels()
    counts = {"A": 0, "M": 0, "D": 0, "R": 0, "?": 0}; shown = []
    for raw in files:
        parts = raw.split("\t"); code = parts[0][:1] if parts else "?"
        code = code if code in counts else "?"; counts[code] += 1
        path = parts[-1] if len(parts) > 1 else raw
        if len(shown) < limit:
            shown.append(f"{code} {short_path(path)}")
    summary = " ".join(f"{k}{v}" for k, v in counts.items() if v)
    if len(files) > limit:
        shown.append(labels["more_files"].format(hidden=len(files) - limit, shown=limit, total=len(files)))
    return summary or labels["no_file"], shown


def task_done(task: dict, task_lanes: list[dict], task_commits: list[dict]) -> bool:
    if task.get("status") != "done":
        return False
    if task_lanes:
        ok = all(x.get("status") in {"done", "merged"} for x in task_lanes)
        return ok and bool(task_commits)
    return bool(task.get("commits") or task_commits)


def agent_rows(tasks: list[dict], lane_map: dict, commit_map: dict) -> list[str]:
    labels = current_labels()
    agents: dict[str, dict] = {}
    for task in tasks:
        name = task.get("agent", "none")
        row = agents.setdefault(name, {"tasks": 0, "done": 0, "commits": 0, "lanes": 0, "stages": set()})
        tl = lane_map.get(task["id"], []); tc = commit_map.get(task["id"], [])
        row["tasks"] += 1; row["commits"] += len(tc); row["lanes"] += len(tl)
        if task.get("stage"): row["stages"].add(task.get("stage"))
        if task_done(task, tl, tc):
            row["done"] += 1
    lines = ["", f"## {labels['agents']}"]
    for name in sorted(agents):
        row = agents[name]
        stage = ",".join(sorted(row.get("stages", []))) or "-"
        lines.append(f"- {name} {labels['tasks']}:{row['done']}/{row['tasks']} "
                     f"{labels['commits']}:{row['commits']} {labels['lanes']}:{row['lanes']} "
                     f"{labels['stages']}:{stage}")
    return lines



def wave_rows(lanes_rows: list[dict]) -> list[str]:
    labels = current_labels()
    waves: dict[str, dict] = {}
    for row in lanes_rows:
        name = row.get("wave", "W001")
        item = waves.setdefault(name, {"lanes": 0, "done": 0, "agents": set()})
        item["lanes"] += 1; item["agents"].add(row.get("agent", ""))
        if row.get("status") in {"done", "merged"}: item["done"] += 1
    lines = ["", f"## {labels['waves']}"]
    for name in sorted(waves):
        row = waves[name]; agents = ",".join(sorted(row["agents"]))
        lines.append(f"- {name} {labels['lanes']}:{row['done']}/{row['lanes']} {labels['agents']}:{agents}")
    return lines

def task_lines(task: dict, tl: list[dict], tc: list[dict]) -> list[str]:
    labels = current_labels()
    mark = "x" if task_done(task, tl, tc) else " "
    skills = ",".join(task.get("skills", [])); tid = task["id"]
    lane_done = sum(1 for x in tl if x.get("status") in {"done", "merged"})
    lane_text = f" {labels['lanes']}:{lane_done}/{len(tl)}" if tl else ""
    wave = task.get("wave", "")
    stage = task.get("stage", "")
    head = f"- [{mark}] {tid} {task['title']} [{task.get('agent','')}] {skills}"
    if stage: head += f" {labels['stage']}:{stage}"
    lines = [head + (f" {labels['wave']}:{wave}" if wave else "")]
    lines.append(f"  {labels['commits']}:{len(tc)}{lane_text}")
    lines += contract_lines(task, "  ")
    for lane in tl:
        lm = "x" if lane.get("status") in {"done", "merged"} else " "
        tail = f" {labels['last']}:{lane.get('commit')}" if lane.get("commit") else ""
        wave = f" {labels['wave']}:{lane.get('wave')}" if lane.get('wave') else ""
        stage = f" {labels['stage']}:{lane.get('stage')}" if lane.get("stage") else ""
        deps = ",".join(lane.get("deps", [])) or "-"
        wname = f" {labels['worker']}:{lane.get('worker_name')}" if lane.get('worker_name') else ""
        lines.append(f"  - [{lm}] {lane['id']} {lane['agent']} {lane['title']}"
                     f"{stage}{wave} {labels['deps']}:{deps}{wname}{tail}")
        lines += contract_lines(lane, "    ")
    for row in tc:
        summary, shown = file_parts(row.get("files", []))
        lines.append(f"  - {labels['commit']} {row.get('short')} {labels['lane']}:{row.get('lane_id') or '-'} {summary}")
        for item in shown:
            lines.append(f"    - {item}")
    return lines


def render(cur: dict, tasks: list[dict]) -> None:
    labels = current_labels()
    lane_rows = lanes(cur); commit_rows = commits(cur)
    lane_map = by_task(lane_rows); commit_map = by_task(commit_rows)
    done = sum(1 for t in tasks if task_done(t, lane_map.get(t["id"], []),
                                              commit_map.get(t["id"], [])))
    heading = "# 태스크" if lib.language() == "ko" else "# TASKS"
    lines = [heading, "", f"{labels['title']}: {cur.get('title')}",
             f"{labels['branch']}: {cur.get('branch')}", f"{labels['base']}: {cur.get('base_branch')}",
             f"{labels['workflow']}: {cur.get('workflow')}", f"{labels['phase']}: {cur.get('phase')}",
             f"{labels['run_version']}: {cur.get('run_version')}",
             f"{labels['project_version']}: {cur.get('project_version')}",
             f"{labels['next_version']}: {cur.get('next_version')}",
             f"{labels['created_at']}: {cur.get('created_at')}",
             f"{labels['progress']}: {done}/{len(tasks)}"]
    lines += wave_rows(lane_rows)
    lines += agent_rows(tasks, lane_map, commit_map)
    lines += ["", f"## {labels['tasks']}"]
    for task in tasks:
        lines += task_lines(task, lane_map.get(task["id"], []), commit_map.get(task["id"], []))
    (Path(cur["path"]) / "TASKS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
