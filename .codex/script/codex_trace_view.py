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


def by_id(rows: list[dict]) -> dict[str, dict]:
    return {row.get("id", ""): row for row in rows if row.get("id")}


LABELS = {
    "ko": {
        "heading": "# 태스크", "summary": "요약", "commit_map": "커밋 맵",
        "item": "항목", "value": "값", "title": "제목", "workflow": "워크플로",
        "phase": "단계", "progress": "진행률", "branch": "브랜치", "base": "기준",
        "run_version": "실행버전", "project_version": "프로젝트버전", "next_version": "다음버전",
        "created_at": "생성시각", "tasks": "태스크", "lanes": "레인", "commits": "커밋",
        "changed_files": "변경 파일", "commit": "커밋", "task": "TASK", "lane": "Lane",
        "agent": "에이전트", "type": "유형", "summary_col": "요약", "revert": "되돌리기",
        "done": "완료", "instruction": "작업 지시", "completed_at": "완료 시간",
        "files_summary": "변경 요약 및 파일", "file_type": "유형", "file": "파일",
        "no_commit": "연결된 커밋 없음", "no_file": "변경 파일 없음", "none": "-",
    },
    "en": {
        "heading": "# TASKS", "summary": "Summary", "commit_map": "Commit Map",
        "item": "Item", "value": "Value", "title": "Title", "workflow": "Workflow",
        "phase": "Phase", "progress": "Progress", "branch": "Branch", "base": "Base",
        "run_version": "Run Version", "project_version": "Project Version", "next_version": "Next Version",
        "created_at": "Created At", "tasks": "Tasks", "lanes": "Lanes", "commits": "Commits",
        "changed_files": "Changed Files", "commit": "Commit", "task": "TASK", "lane": "Lane",
        "agent": "Agent", "type": "Type", "summary_col": "Summary", "revert": "Revert",
        "done": "Done", "instruction": "Instruction", "completed_at": "Completed At",
        "files_summary": "Change Summary and Files", "file_type": "Type", "file": "File",
        "no_commit": "No linked commits", "no_file": "No changed files", "none": "-",
    },
}


def current_labels() -> dict:
    return LABELS.get(lib.language(), LABELS["ko"])


def md(value) -> str:
    text = str(value if value is not None else "-")
    return text.replace("|", "\\|").replace("\n", " ")


def code(value) -> str:
    value = str(value or "-")
    return f"`{md(value)}`" if value != "-" else "-"


def short_path(path: str, max_len: int = 96) -> str:
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


def table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    rows = rows or [["-" for _ in headers]]
    lines.extend("| " + " | ".join(md(cell) for cell in row) + " |" for row in rows)
    return lines


def info_table(rows: list[tuple[str, str]]) -> list[str]:
    labels = current_labels()
    return table([labels["item"], labels["value"]], [[k, v] for k, v in rows])


def file_code(raw: str) -> str:
    parts = raw.split("\t")
    raw_code = parts[0][:1] if parts else "?"
    return raw_code if raw_code in {"A", "M", "D", "R"} else "?"


def file_path(raw: str) -> str:
    parts = raw.split("\t")
    return parts[-1] if len(parts) > 1 else raw


def file_counts(rows: list[dict]) -> dict[str, int]:
    counts = {"A": 0, "M": 0, "D": 0, "R": 0}
    for row in rows:
        for raw in row.get("files", []):
            kind = file_code(raw)
            if kind in counts:
                counts[kind] += 1
    return counts


def changed_file_rows(rows: list[dict]) -> list[list[str]]:
    seen = set(); out = []
    for row in rows:
        for raw in row.get("files", []):
            item = (file_code(raw), file_path(raw))
            if item in seen:
                continue
            seen.add(item)
            out.append([item[0], code(short_path(item[1]))])
    return out


def commit_short(row: dict) -> str:
    return row.get("short") or str(row.get("commit", ""))[:7] or "-"


def commit_summary(row: dict, task: dict | None, lane: dict | None) -> str:
    return value_text(row.get("summary") or row.get("subject") or
                      (lane or {}).get("title") or (task or {}).get("title") or "-")


def commit_cell(rows: list[dict], task: dict, lane: dict | None = None) -> str:
    if not rows:
        return "-"
    return "<br>".join(f"{code(commit_short(row))} - {md(commit_summary(row, task, lane))}" for row in rows)


def completed_at(rows: list[dict]) -> str:
    return rows[0].get("time", "-") if rows else "-"


def row_worker(row: dict) -> str:
    return row.get("worker_name") or row.get("reuse_key") or row.get("agent") or "none"


def group_seed(item: dict, cur: dict) -> str:
    return (item.get("group_id") or item.get("work_id") or item.get("request_summary") or
            cur.get("request_summary") or cur.get("title") or "work")


def group_title(item: dict, cur: dict) -> str:
    return value_text(item.get("group_title") or item.get("work_title") or
                      item.get("request_summary") or cur.get("request_summary") or
                      cur.get("title") or "work", 96)


def task_done(task: dict, task_lanes: list[dict], task_commits: list[dict]) -> bool:
    if task.get("status") != "done":
        return False
    if task_lanes:
        ok = all(x.get("status") in {"done", "merged"} for x in task_lanes)
        return ok and bool(task_commits)
    return bool(task.get("commits") or task_commits)


def commit_map_rows(tasks: list[dict], lane_rows: list[dict], commit_rows: list[dict]) -> list[list[str]]:
    labels = current_labels(); tasks_by_id = by_id(tasks); lanes_by_id = by_id(lane_rows); out = []
    for row in commit_rows:
        task = tasks_by_id.get(row.get("task_id", ""), {})
        lane = lanes_by_id.get(row.get("lane_id", ""), {})
        short = commit_short(row)
        out.append([
            code(short), row.get("task_id", "-"), row.get("lane_id") or "-",
            row_worker(lane or row or task), lane.get("stage") or task.get("stage") or "-",
            commit_summary(row, task, lane), code(f"git revert {short}") if short != "-" else labels["none"],
        ])
    return out


def summary_lines(cur: dict, tasks: list[dict], lane_rows: list[dict], commit_rows: list[dict]) -> list[str]:
    labels = current_labels(); lane_map = by_task(lane_rows); commit_map = by_task(commit_rows)
    done = sum(1 for task in tasks if task_done(task, lane_map.get(task.get("id", ""), []),
                                                commit_map.get(task.get("id", ""), [])))
    counts = file_counts(commit_rows)
    return [
        f"## {labels['summary']}",
        *info_table([
            (labels["title"], cur.get("title", "-")),
            (labels["workflow"], cur.get("workflow", "-")),
            (labels["phase"], cur.get("phase", "-")),
            (labels["progress"], f"{done}/{len(tasks)}"),
            (labels["branch"], cur.get("branch", "-")),
            (labels["base"], cur.get("base_branch", "-")),
            (labels["run_version"], str(cur.get("run_version", "-"))),
            (labels["project_version"], cur.get("project_version", "-")),
            (labels["next_version"], cur.get("next_version", "-")),
            (labels["created_at"], cur.get("created_at", "-")),
            (labels["tasks"], str(len(tasks))),
            (labels["lanes"], str(len(lane_rows))),
            (labels["commits"], str(len(commit_rows))),
            (labels["changed_files"], f"A{counts['A']} M{counts['M']} D{counts['D']} R{counts['R']}"),
        ]),
    ]


def lane_work_row(task: dict, lane: dict, commits_for_lane: list[dict]) -> list[str]:
    labels = current_labels(); done = "[x]" if lane.get("status") in {"done", "merged"} else "[ ]"
    return [done, task.get("id", "-"), lane.get("id", "-"), lane.get("stage") or lane.get("agent", "-"),
            value_text(lane.get("title") or task.get("title")), completed_at(commits_for_lane),
            commit_cell(commits_for_lane, task, lane)]


def task_work_row(task: dict, commits_for_task: list[dict]) -> list[str]:
    done = "[x]" if task.get("status") == "done" and commits_for_task else "[ ]"
    return [done, task.get("id", "-"), "-", task.get("stage") or task.get("agent", "-"),
            value_text(task.get("title")), completed_at(commits_for_task), commit_cell(commits_for_task, task)]


def details_block(commit_rows: list[dict]) -> list[str]:
    labels = current_labels(); counts = file_counts(commit_rows)
    rows = changed_file_rows(commit_rows) or [["-", labels["no_file"]]]
    return [
        "",
        "<details>",
        f"<summary>{labels['files_summary']}</summary>",
        "",
        *table(["ADD", "UPDATE", "DELETE", "RENAME"],
               [[str(counts["A"]), str(counts["M"]), str(counts["D"]), str(counts["R"])] ]),
        "",
        *table([labels["file_type"], labels["file"]], rows),
        "",
        "</details>",
    ]


def grouped_sections(cur: dict, tasks: list[dict], lane_rows: list[dict], commit_rows: list[dict]) -> list[str]:
    labels = current_labels(); lane_map = by_task(lane_rows); commit_map = by_task(commit_rows)
    tasks_by_id = by_id(tasks); group_order: list[str] = []; groups: dict[str, dict] = {}
    for task in tasks:
        seed = group_seed(task, cur)
        if seed not in groups:
            groups[seed] = {"index": len(groups) + 1, "title": group_title(task, cur), "tasks": []}
            group_order.append(seed)
        groups[seed]["tasks"].append(task)
    lines: list[str] = []
    for seed in group_order:
        group = groups[seed]; gid = seed if str(seed).startswith("G") else f"G{group['index']:03d}"
        lines += ["", f"# {gid} - {group['title']}"]
        agent_rows: dict[str, list[list[str]]] = {}; agent_commits: dict[str, list[dict]] = {}
        for task in group["tasks"]:
            lanes_for_task = lane_map.get(task.get("id", ""), [])
            commits_for_task = commit_map.get(task.get("id", ""), [])
            if not lanes_for_task:
                worker = task.get("agent", "none")
                agent_rows.setdefault(worker, []).append(task_work_row(task, commits_for_task))
                agent_commits.setdefault(worker, []).extend(commits_for_task)
                continue
            for lane in lanes_for_task:
                worker = row_worker(lane)
                lane_commits = [row for row in commits_for_task if row.get("lane_id") == lane.get("id")]
                agent_rows.setdefault(worker, []).append(lane_work_row(task, lane, lane_commits))
                agent_commits.setdefault(worker, []).extend(lane_commits)
        for worker in sorted(agent_rows):
            agent = worker.split("-")[0] if worker else "none"
            lines += ["", f"## {agent} - {worker}"]
            lines += table([labels["done"], labels["task"], labels["lane"], labels["type"],
                            labels["instruction"], labels["completed_at"], labels["commit"]], agent_rows[worker])
            lines += details_block(agent_commits.get(worker, []))
    return lines


def render(cur: dict, tasks: list[dict]) -> None:
    labels = current_labels(); lane_rows = lanes(cur); commit_rows = commits(cur)
    lines = [labels["heading"], ""]
    lines += summary_lines(cur, tasks, lane_rows, commit_rows)
    lines += ["", f"## {labels['commit_map']}"]
    lines += table([labels["commit"], labels["task"], labels["lane"], labels["agent"], labels["type"],
                    labels["summary_col"], labels["revert"]],
                   commit_map_rows(tasks, lane_rows, commit_rows) or
                   [["-", "-", "-", "-", "-", labels["no_commit"], "-"]])
    lines += grouped_sections(cur, tasks, lane_rows, commit_rows)
    (Path(cur["path"]) / "TASKS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
