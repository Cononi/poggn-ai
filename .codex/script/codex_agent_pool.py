#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import lib, codex_state, codex_trace_view

KO_AGENT = {"architecture": "아키텍처", "backend": "백엔드", "frontend": "프론트",
            "database": "DB", "test_writer": "테스트작성",
            "test_runner": "테스트실행", "qa": "QA",
            "refactor": "리팩터", "security": "보안"}
KO_STAGE = {
    "foundation": "기반", "implement": "구현", "test_writer": "테스트작성",
    "test_runner": "테스트실행", "test_write": "테스트작성",
    "test_run": "테스트실행", "qa": "QA", "refactor": "리팩터",
    "security": "보안", "final_refactor": "최종리팩터",
    "final_security": "최종보안",
}
EN_STAGE = {
    "foundation": "foundation", "implement": "implement",
    "test_writer": "test-writer", "test_runner": "test-runner",
    "test_write": "test-write", "test_run": "test-run",
    "qa": "qa", "refactor": "refactor", "security": "security",
    "final_refactor": "final-refactor", "final_security": "final-security",
}
DEFAULT = {
    "reuse_mode": "scoped_fresh",
    "reset_on_new_maw": True,
    "close_completed_on_wave_end": True,
    "max_context_jobs_per_thread": 3,
}


def cfg_path() -> Path:
    return lib.find_codex() / "state" / "agent_runtime.json"


def cfg() -> dict:
    data = lib.read_json(cfg_path(), DEFAULT)
    out = dict(DEFAULT); out.update(data); return out


def save(data: dict) -> None:
    lib.write_json(cfg_path(), data)


def current() -> dict:
    return codex_state.current()


def label(row: dict) -> str:
    lang = lib.language(); stage = row.get("stage", "implement")
    feature = lib.safe_slug(row.get("feature") or row.get("task_id", "task"))
    if lang == "ko":
        agent = KO_AGENT.get(row.get("agent", ""), row.get("agent", "agent"))
        stage_name = KO_STAGE.get(stage, stage)
    else:
        agent = row.get("agent", "agent").replace("_", "-")
        stage_name = EN_STAGE.get(stage, stage).replace("_", "-")
    return f"{agent}-{feature}-{stage_name}-{row.get('id')}"


def reuse_key(row: dict) -> str:
    mode = cfg().get("reuse_mode", "scoped_fresh")
    if mode == "role_thread":
        return f"{row.get('agent')}:{row.get('stage')}"
    if mode == "feature_thread":
        return f"{row.get('agent')}:{row.get('feature')}:{row.get('stage')}"
    return label(row)


def rows() -> list[dict]:
    cur = current()
    if not cur:
        return []
    return codex_trace_view.lanes(cur)


def cmd_policy(args) -> int:
    print(json.dumps(cfg(), ensure_ascii=False, indent=2)); return 0


def cmd_set_mode(args) -> int:
    data = cfg(); data["reuse_mode"] = args.mode; data["updated_at"] = lib.now()
    save(data); print(args.mode); return 0


def cmd_labels(args) -> int:
    out = []
    for row in rows():
        out.append({"lane_id": row.get("id"), "task_id": row.get("task_id"),
                    "agent": row.get("agent"), "stage": row.get("stage"),
                    "worker_label": label(row), "reuse_key": reuse_key(row)})
    print(json.dumps(out, ensure_ascii=False, indent=2)); return 0


def cmd_status(args) -> int:
    data = {"policy": cfg(), "labels": []}
    for row in rows():
        if row.get("status") not in {"done", "merged"}:
            data["labels"].append({"lane_id": row.get("id"),
                                    "label": label(row),
                                    "reuse_key": reuse_key(row),
                                    "status": row.get("status")})
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("policy"); sub.add_parser("labels"); sub.add_parser("status")
    s = sub.add_parser("set-mode")
    s.add_argument("mode", choices=["scoped_fresh", "feature_thread", "role_thread"])
    args = p.parse_args(); return globals()["cmd_" + args.cmd.replace("-", "_")](args)


if __name__ == "__main__":
    raise SystemExit(main())
