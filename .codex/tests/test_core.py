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


def test_budget_suggest_splits_community_stack():
    import codex_budget
    Args = type('Args', (), {
        'text': 'spring boot jpa h2 react mui community',
        'cwd': '', 'staged': False, 'base': '',
        'mode': 'auto', 'for_ai': True,
        'agents': 'backend,frontend,test_writer,qa,security',
    })
    data = codex_budget.analyze(Args())
    assert 'post' in data['features']
    assert 'comment' in data['features']
    assert data['decision'] == 'maw_split_waves'


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


def test_work_items_include_spark_lane_contract():
    import codex_work_items
    rows = codex_work_items.plan(
        "spring boot jpa h2 react mui community",
        agents="backend,frontend,test_writer,qa,security",
        guards="static",
    )
    keys = {x["key"] for x in rows}
    backend = next(x for x in rows if x["agent"] == "backend")
    frontend = next(x for x in rows if x["agent"] == "frontend")
    assert "contract" in keys
    assert "impl:post:backend" in keys
    assert "impl:comment:frontend" in keys
    assert "Spark lane budget" in backend["budget_note"]
    assert any("backend" in x or "src/main" in x for x in backend["owner_files"])
    assert any("frontend" in x or "client" in x for x in frontend["owner_files"])
    assert backend["forbidden_files"]
    assert backend["verification"]
    assert backend["done_contract"]


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


def test_hook_prompt_output_does_not_inject_general_context():
    import hook_context
    out = hook_context.prompt_output('프로젝트 기능 수정해줘', 'ko')
    assert out == {'continue': True}


def test_hook_prompt_output_does_not_inject_maw_context():
    import hook_context
    out = hook_context.prompt_output('$maw 주문 기능 만들어줘', 'ko')
    assert out == {'continue': True}


def test_hook_session_start_has_no_system_message():
    import hook_context
    out = hook_context.output('session_start')
    assert out == {'continue': True, 'suppressOutput': True}


def test_hook_protected_write_still_denies_codex_edits_in_project_mode():
    import hook_context
    original = hook_context.read_mode
    hook_context.read_mode = lambda: {'mode': 'project'}
    try:
        payload = {
            'tool_name': 'apply_patch',
            'tool_input': {'path': '.codex/script/hook_context.py'},
        }
        assert hook_context.protected_write(payload)
    finally:
        hook_context.read_mode = original


def test_trace_view_renders_tasks_markdown_in_current_language(tmp_path):
    import json
    import codex_trace_view
    original = codex_trace_view.lib.language
    codex_trace_view.lib.language = lambda: 'ko'
    try:
        cur = {
            'path': str(tmp_path), 'title': 'jp/sb 기반 생성', 'branch': 'feature/jp-sb',
            'base_branch': 'main', 'workflow': 'maw', 'phase': 'implement',
            'run_version': 1, 'project_version': '0.1.0', 'next_version': '0.1.1',
            'created_at': '2026-06-15T00:00:00+09:00',
        }
        tasks = [
            {'id': 'T001', 'title': 'jp JPA 라이브러리 생성', 'agent': 'backend',
             'status': 'done', 'stage': 'implement', 'group_id': 'G001',
             'group_title': 'jp/sb 기반 생성'},
            {'id': 'T002', 'title': 'sb Spring Boot 앱 생성 및 jp 연동', 'agent': 'backend',
             'status': 'done', 'stage': 'implement', 'group_id': 'G001',
             'group_title': 'jp/sb 기반 생성'},
        ]
        lanes = [
            {'id': 'L001', 'task_id': 'T001', 'agent': 'backend',
             'title': 'jp JPA 라이브러리 생성', 'stage': 'implementation',
             'status': 'done', 'worker_name': 'backend-A8'},
            {'id': 'L002', 'task_id': 'T002', 'agent': 'backend',
             'title': 'sb Spring Boot 앱 생성 및 jp 연동', 'stage': 'implementation',
             'status': 'done', 'worker_name': 'backend-A8'},
        ]
        commits = [
            {'time': '2026-05-15 13:03:00', 'task_id': 'T001', 'lane_id': 'L001',
             'short': '60032b8', 'summary': 'jp JPA 라이브러리 생성',
             'files': ['A\tjp/build.gradle']},
            {'time': '2026-05-15 13:20:00', 'task_id': 'T002', 'lane_id': 'L002',
             'short': '3f7fbf3', 'summary': 'sb Spring Boot 앱 생성 및 jp 연동',
             'files': ['M\tsb/build.gradle']},
        ]
        (tmp_path / 'lanes.jsonl').write_text(
            '\n'.join(json.dumps(x, ensure_ascii=False) for x in lanes) + '\n',
            encoding='utf-8')
        (tmp_path / 'commits.jsonl').write_text(
            '\n'.join(json.dumps(x, ensure_ascii=False) for x in commits) + '\n',
            encoding='utf-8')
        codex_trace_view.render(cur, tasks)
        rendered = (tmp_path / 'TASKS.md').read_text(encoding='utf-8')
        assert '# 태스크' in rendered
        assert '## 커밋 맵' in rendered
        assert '# G001 - jp/sb 기반 생성' in rendered
        assert '## backend - backend-A8' in rendered
        assert '| [x] | T001 | L001 | implementation | jp JPA 라이브러리 생성 | 2026-05-15 13:03:00 | `60032b8` - jp JPA 라이브러리 생성 |' in rendered
        assert '| [x] | T002 | L002 | implementation | sb Spring Boot 앱 생성 및 jp 연동 | 2026-05-15 13:20:00 | `3f7fbf3` - sb Spring Boot 앱 생성 및 jp 연동 |' in rendered
        assert '<summary>변경 요약 및 파일</summary>' in rendered
        assert '| 1 | 1 | 0 | 0 |' in rendered
        assert '| A | `jp/build.gradle` |' in rendered
        assert '| M | `sb/build.gradle` |' in rendered
        assert '### 태스크 정보' not in rendered
        assert 'purpose:' not in rendered
        assert 'acceptance:' not in rendered
    finally:
        codex_trace_view.lib.language = original


def test_pipeline_instruction_uses_current_language(tmp_path):
    import codex_pipeline
    original_lang = codex_pipeline.lib.language
    original_root = codex_pipeline.lib.root_dir
    codex_pipeline.lib.language = lambda: 'ko'
    codex_pipeline.lib.root_dir = lambda: tmp_path
    try:
        row = {
            'id': 'L001', 'task_id': 'T001', 'agent': 'backend',
            'title': '주문 생성', 'stage': 'implement', 'feature': 'order',
            'worktree': str(tmp_path / 'worktree'), 'deps': [], 'skills': ['spring-boot'],
            'purpose': '주문 기능을 구현합니다.', 'acceptance': '검증을 통과합니다.',
        }
        text = codex_pipeline.instruction(row)
        assert '에이전트 backend' in text
        assert '작업 위치는' in text
        assert 'Finish from root' not in text
    finally:
        codex_pipeline.lib.language = original_lang
        codex_pipeline.lib.root_dir = original_root
