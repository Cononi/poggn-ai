#!/usr/bin/env python3
from __future__ import annotations
import json, shlex, subprocess, sys
from pathlib import Path
import lib

MAP = {
    "$codex-language": "codex_language.py",
    "$codex-locale": "codex_locale.py",
    "$codex-state": "codex_state.py",
    "$codex-lanes": "codex_lanes.py",
    "$codex-pipeline": "codex_pipeline.py",
    "$codex-events": "codex_event_bus.py",
    "$codex-queue": "codex_event_bus.py",
    "$codex-pool": "codex_agent_pool.py",
    "$codex-agent-pool": "codex_agent_pool.py",
    "$codex-finalize": "codex_finalizer.py",
    "$codex-scheduler": "codex_scheduler.py",
    "$codex-waves": "codex_waves.py",
    "$codex-task": "codex_task_git.py",
    "$codex-work-items": "codex_work_items.py",
    "$codex-saw": "codex_saw.py",
    "$codex-agents": "codex_agents.py",
    "$codex-agent-roles": "codex_agent_roles.py",
    "$codex-extend": "codex_extend.py",
    "$codex-capabilities": "codex_extend.py",
    "$codex-capability": "codex_extend.py",
    "$codex-agent": "codex_agents.py",
    "$codex-skills": "codex_skills.py",
    "$codex-refactor": "codex_refactor.py",
    "$codex-security": "codex_security.py",
    "$codex-quality": "codex_quality.py",
    "$codex-verify": "codex_verify.py",
    "$codex-budget": "codex_budget.py",
    "$codex-context": "codex_context.py",
    "$codex-risk": "codex_risk.py",
    "$codex-doctor": "codex_doctor.py",
    "$codex-wiki": "codex_wiki.py",
    "$codex-git": "codex_git_bootstrap.py",
}

USAGE = """Codex shortcut commands:
$codex-language ko|en|status
$codex-locale set Asia/Seoul --country KR
$codex-state summary --for-ai
$codex-saw init --title fix --branch hotfix/fix --text "fix dto"
$codex-work-items apply --text "shop order payment" --agents backend,test,qa,refactor,security
$codex-verify gate --staged --mode saw --for-ai
$codex-budget suggest --text "order payment rest api" --for-ai
$codex-budget gate --staged --mode saw --for-ai
$codex-context pack --staged --for-ai
$codex-risk classify --staged --for-ai
$codex-doctor --deep --for-ai
$codex-pipeline status|ready|prepare|csv --ready|prompt
$codex-events process --lane L001 --for-ai
$codex-events enqueue --from-lane L001 --for-ai
$codex-events workers --for-ai
$codex-pool labels|policy|status
$codex-finalize status|apply --for-ai
$codex-scheduler ready|csv --ready|prompt|policy
$codex-waves assign|plan|next|prompt
$codex-lanes list|status|csv|prompt|prepare --wave W001
$codex-task trace --for-ai
$codex-task commit T001 --message "fix order dto"
$codex-wiki build
$codex-agent-roles implementers --text "shop order" --agents backend,frontend
$codex-extend scan --text "payment webhook" --for-ai
$codex-capabilities inspect --text "payment webhook" --for-ai
$codex-extend check agent --name mobile --purpose "React Native UI"
$codex-extend create skill --name grpc --purpose "gRPC API" --approve
""".strip()


def parse(prompt: str) -> list[str] | None:
    text = prompt.strip()
    if not text.startswith("$codex-"):
        return None
    try:
        parts = shlex.split(text)
    except ValueError as exc:
        return ["__error__", str(exc)]
    return parts or None


def trim(text: str, limit: int = 0) -> str:
    if not limit:
        try:
            import codex_budget
            limit = codex_budget.limit_value('shortcut_limit')
        except Exception:
            limit = 3000
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... truncated by codex_shortcuts.py"


def block(reason: str) -> dict:
    return {"decision": "block", "reason": trim(reason)}


def run(parts: list[str]) -> dict:
    if not parts:
        return {}
    if parts[0] == "__error__":
        return block(parts[1])
    script = MAP.get(parts[0])
    if not script:
        return block(USAGE)
    path = lib.find_codex() / "script" / script
    cmd = [sys.executable, str(path), *parts[1:]]
    proc = subprocess.run(cmd, cwd=str(lib.root_dir()), text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = proc.stdout.strip() or proc.stderr.strip() or "ok"
    if proc.returncode:
        text = "failed:\n" + text
    return block(text)


def main() -> int:
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    parts = parse(prompt)
    if not parts:
        return 1
    print(json.dumps(run(parts), ensure_ascii=False)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
