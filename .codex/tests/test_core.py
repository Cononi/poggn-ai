#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "script"))
import lib
from codex_state import bump


def test_bump_patch():
    assert bump("1.2.3", "patch") == "1.2.4"


def test_bump_minor():
    assert bump("1.2.3", "minor") == "1.3.0"


def test_slug():
    assert lib.safe_slug("Release Shop API") == "release-shop-api"


def test_add_commit_short_value():
    item = {"commits": []}
    import codex_state
    codex_state.add_commit(item, "abcdef1234567890")
    assert item["commit"] == "abcdef123456"
    assert item["commits"] == ["abcdef1234567890"]


def test_refactor_repeat_score():
    import codex_refactor
    lines = ["value = call_service(item)" for _ in range(4)]
    assert codex_refactor.repeat_score(lines) == 2


def test_skills_filter_by_agent():
    import codex_skills
    data = codex_skills.recommend("spring boot jpa swagger", "security")
    assert data == [] or data == ["security-gate", "verify-gate"]


def test_task_done_needs_commit():
    import codex_trace_view
    task = {"status": "done", "commits": []}
    assert not codex_trace_view.task_done(task, [], [])


def test_quality_rejects_jsx_extension(tmp_path):
    import codex_quality
    rel = "src/components/Bad.jsx"
    path = tmp_path / rel
    path.parent.mkdir(parents=True)
    path.write_text("export function Bad(){return <button/>}")
    class Args:
        max_lines = 200
        front_lines = 160
        repeat_limit = 6
    issues = codex_quality.analyze_file(tmp_path, rel, Args())
    kinds = {x["kind"] for x in issues}
    assert "frontend-tsx-required" in kinds


def test_saw_lite_single_task_plan():
    import codex_saw
    data = codex_saw.plan("fix order dto mapping")
    assert data["mode"] == "saw-lite"
    assert data["agent"] == "backend"
    assert data["task_policy"] == "one task, one commit, mandatory verify gate"
    assert "targeted test" in data["verify_policy"]


def test_saw_frontend_primary_agent():
    import codex_saw
    data = codex_saw.plan("react tsx button variant fix")
    assert data["agent"] == "frontend"
    assert "frontend-component-architecture" in data["skills"]


def test_verify_docs_only_policy(tmp_path):
    import subprocess
    import codex_verify
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.PIPE)
    path = tmp_path / "README.md"
    path.write_text("docs")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    class Args:
        cwd = str(tmp_path)
        staged = True
        base = ""
        mode = "saw"
        for_ai = True
        allow_no_test = False
        timeout = 5
    data = codex_verify.verify(Args())
    assert data["test_policy"] == "skipped_docs_or_no_code"


def test_budget_text_recommends_maw():
    import codex_budget
    class Args:
        cwd = ""
        staged = False
        base = ""
        mode = "auto"
        text = "order payment rest api"
        for_ai = True
    data = codex_budget.analyze(Args())
    assert data["decision"] in {"maw_split_waves", "maw_single_wave"}


def test_context_pack_empty():
    import codex_context
    class Args:
        cwd = ""
        staged = False
        base = ""
        task = ""
        snippets = False
        max_files = 2
        max_lines = 5
        for_ai = True
    data = codex_context.pack(Args())
    assert "cwd" in data


def test_risk_recommends_maw_for_payment_auth():
    import codex_risk
    Args = type('Args', (), {'text': 'payment auth api 수정', 'cwd': '',
                             'staged': False, 'base': '', 'for_ai': True})
    data = codex_risk.classify(Args())
    assert data['risk'] == 'high'
    assert data['workflow'] == 'maw'


def test_budget_suggest_recommends_maw_for_order_payment():
    import codex_budget
    Args = type('Args', (), {'text': 'order payment rest api'})
    # exercise parser-free helper path via analyze text branch
    Full = type('Full', (), {'text': Args.text, 'cwd': '', 'staged': False,
                             'base': '', 'mode': 'auto', 'for_ai': True})
    data = codex_budget.analyze(Full())
    assert data['decision'] in {'maw_split_waves', 'maw_single_wave'}


def test_context_pack_without_workflow_fails_cleanly():
    import subprocess
    proc = subprocess.run([sys.executable, '.codex/script/codex_context.py', 'pack'],
                          cwd=str(Path(__file__).parents[2]), text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.returncode in {0, 1, 2}


def test_maw_uses_all_selected_implementation_agents():
    import codex_work_items
    rows = codex_work_items.plan(
        "shop order payment webhook react rest api",
        agents="backend,frontend,integration,test_writer,qa"
    )
    impl = {(r["agent"], r["feature"]) for r in rows if r["stage"] == "implement"}
    assert ("backend", "order") in impl
    assert ("backend", "payment") in impl
    assert ("frontend", "order") in impl
    assert ("integration", "payment") in impl


def test_agent_roles_classifies_implementation_groups():
    import codex_agent_roles
    data = codex_agent_roles.implementers(
        "shop order react", "backend,frontend,qa,security"
    )
    assert "backend" in data["feature"]
    assert "frontend" in data["feature"]
    assert "qa" not in data["feature"]

def test_work_items_general_implementation_agents():
    import codex_work_items
    rows = codex_work_items.plan(
        "react webhook order payment rest api",
        "order,payment",
        "backend,frontend,integration,test_writer,qa",
        "auto",
    )
    keys = {x["key"] for x in rows}
    assert "impl:order:backend" in keys
    assert "impl:payment:frontend" in keys
    assert "impl:order:integration" in keys


def test_event_policy_triggers_only_producer_stage():
    import codex_event_bus
    row = {"stage": "implement", "agent": "frontend"}
    pol = {"producer_stages": ["implement"], "producer_agents": ["frontend"]}
    assert codex_event_bus.is_producer(pol, row)
    row = {"stage": "qa", "agent": "qa"}
    assert not codex_event_bus.is_producer(pol, row)

def test_verify_detects_gradle_build_file_for_java(tmp_path):
    import codex_verify
    (tmp_path / 'build.gradle').write_text('plugins { id \"java\" }')
    cmds = codex_verify.detected_commands(tmp_path, ['src/main/java/App.java'], 'saw')
    assert ['gradle', 'test', '--no-daemon'] in cmds


def test_verify_prefers_gradle_wrapper_over_maven(tmp_path):
    import codex_verify
    (tmp_path / 'gradlew').write_text('#!/bin/sh')
    (tmp_path / 'pom.xml').write_text('<project/>')
    cmds = codex_verify.detected_commands(tmp_path, ['src/main/java/App.java'], 'saw')
    assert cmds == [['./gradlew', 'test', '--no-daemon']]



def test_task_commit_message_parts_include_body_and_footer():
    import codex_task_git
    args = type('Args', (), {'id': 'T123', 'lane': 'L007', 'message': '회원 주문 생성'})()
    task = {'id': 'T123', 'title': '회원 주문 생성', 'agent': 'backend',
            'skills': ['spring-boot'], 'stage': 'implement',
            'purpose': '주문 생성 API를 구현합니다.',
            'acceptance': '검증과 TASK 추적이 완료됩니다.'}
    lane = {'id': 'L007', 'agent': 'backend', 'stage': 'implement'}
    cur = {'workflow': 'maw', 'path': '/tmp/v1-order'}
    subject, body, footer = codex_task_git.commit_message_parts(args, task, cur, lane, 'maw')
    assert subject == 'feat: 회원 주문 생성'
    assert '목적: 주문 생성 API를 구현합니다.' in body
    assert '검증: codex_verify gate --staged --mode maw' in body
    assert 'Codex-Task: T123' in footer
    assert 'Codex-Lane: L007' in footer
    assert 'Codex-Verification: codex_verify gate --staged --mode maw' in footer


def test_task_commit_message_keeps_existing_conventional_subject():
    import codex_task_git
    task = {'id': 'T001', 'title': 'fallback', 'stage': 'implement'}
    assert codex_task_git.commit_subject('fix: correct dto mapping', task) == 'fix: correct dto mapping'
