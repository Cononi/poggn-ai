#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
import codex_risk, codex_skills, codex_state, codex_work_items, lib


def split(v: str) -> list[str]:
    return [x.strip() for x in v.split(',') if x.strip()]


def words(t: str) -> set[str]:
    return codex_work_items.words(t)


def primary_agent(text: str, explicit: str = '') -> str:
    if explicit:
        return split(explicit)[0]
    w = words(text)
    table = [
        ('frontend', 'frontend react next ui 화면 page component tsx'),
        ('database', 'database db schema migration index entity'),
        ('docs', 'docs readme 문서 wiki guide'),
        ('security', 'security auth permission secret token 보안'),
        ('test', 'test 테스트 spec junit vitest pytest'),
        ('refactor', 'refactor clean duplicate 리팩토링 중복'),
    ]
    for agent, keys in table:
        if w & words(keys):
            return agent
    return 'backend'


def risk_flags(text: str) -> list[str]:
    w = words(text); flags = []
    if w & words('auth permission role security secret token payment 결제'):
        flags.append('security_review')
    if w & words('database migration schema order payment state 동시성'):
        flags.append('change_risk')
    if w & words('frontend react component ui form checkout'):
        flags.append('frontend_quality')
    return flags


def compact_title(text: str) -> str:
    return codex_work_items.compact(text, 64) or 'saw-task'


def plan(text: str, agents: str = '') -> dict:
    agent = primary_agent(text, agents)
    skills = codex_skills.recommend(text, agent)
    if agent == 'frontend' and 'frontend-component-architecture' not in skills:
        skills.append('frontend-component-architecture')
    if 'verify-gate' not in skills:
        skills.append('verify-gate')
    feats = codex_work_items.infer_features(text, '')
    risk_args = type('Args', (), {'text': text, 'cwd': '', 'staged': False,
                                  'base': '', 'for_ai': True})()
    risk = codex_risk.classify(risk_args)
    maw = risk['workflow'] == 'maw' or len(feats) > 1
    maw = maw or {'backend', 'frontend'} <= {agent, *split(agents)}
    row = {'title': compact_title(text), 'agent': agent, 'feature': feats[0],
           'stage': 'implement'}
    contract = codex_work_items.contract_for(row, text)
    return {'mode': 'saw-lite', 'agent': agent, 'skills': skills,
            'risk': risk['risk'], 'risk_areas': risk['areas'],
            'risk_flags': risk_flags(text), 'recommend_maw': maw,
            'task_policy': 'one task, one commit, mandatory verify gate',
            'verify_policy': 'quality + targeted test + staged security',
            **contract}


def current_saw() -> dict:
    cur = codex_state.current()
    if not cur or 'path' not in cur:
        raise SystemExit('workflow not initialized')
    if cur.get('workflow') != 'saw':
        raise SystemExit('current workflow is not saw')
    return cur


def add_task(cur: dict, title: str, agent: str, skills: list[str], text: str) -> str:
    tasks = codex_state.read_tasks(cur); tid = f'T{len(tasks) + 1:03d}'
    feats = codex_work_items.infer_features(text, '')
    row = {'title': title, 'agent': agent, 'feature': feats[0], 'stage': 'implement'}
    contract = codex_work_items.contract_for(row, text)
    tasks.append({'id': tid, 'title': title, 'agent': agent, 'skills': skills,
                  'status': 'todo', 'commit': '', 'commits': [],
                  'mode': 'saw-lite', 'request': text, 'feature': feats[0],
                  'stage': 'implement', **contract})
    codex_state.write_tasks(cur, tasks)
    codex_state.events(cur, 'task_add', {'id': tid, 'agent': agent,
                                         'mode': 'saw-lite'})
    return tid


def make_task(cur: dict, text: str, title: str = '', agents: str = '') -> dict:
    p = plan(text, agents); task_title = title or compact_title(text)
    tid = add_task(cur, task_title, p['agent'], p['skills'], text)
    finish = f'$codex-task commit {tid} --message "{task_title}"'
    return {'task_id': tid, 'finish': finish, **p}


def cmd_init(args) -> int:
    args.workflow = 'saw'; codex_state.cmd_init(args)
    cur = current_saw(); cur['saw_mode'] = 'lite'; codex_state.save_current(cur)
    if args.text:
        data = make_task(cur, args.text, args.title, args.agents)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def cmd_suggest(args) -> int:
    print(json.dumps(plan(args.text, args.agents), ensure_ascii=False, indent=2))
    return 0


def cmd_apply(args) -> int:
    data = make_task(current_saw(), args.text, args.title, args.agents)
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0


def next_task(cur: dict) -> dict | None:
    for task in codex_state.read_tasks(cur):
        if task.get('status') != 'done':
            return task
    return None


def cmd_next(args) -> int:
    print(json.dumps(next_task(current_saw()) or {'done': True},
                     ensure_ascii=False, indent=2)); return 0


def cmd_prompt(args) -> int:
    task = next_task(current_saw())
    if not task:
        print('all SAW tasks are complete'); return 0
    skills = ','.join(task.get('skills', [])) or '-'
    print(f'NEXT {task["id"]} {task.get("agent", "")}: {task["title"]}')
    print('mode: saw-lite; edit only required files')
    if task.get('purpose'):
        print('purpose: ' + task['purpose'])
    if task.get('acceptance'):
        print('acceptance: ' + task['acceptance'])
    print(f'skills: {skills}')
    print('$codex-verify gate --mode saw --for-ai')
    print('commit will re-run the same gate on staged files')
    print(f'$codex-task commit {task["id"]} --message "{task["title"]}"')
    return 0


def run_script(name: str, args: list[str]) -> dict:
    path = lib.find_codex() / 'script' / name
    proc = subprocess.run([sys.executable, str(path), *args], cwd=str(lib.root_dir()),
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = (proc.stdout or proc.stderr).strip()[:3000]
    return {'ok': proc.returncode == 0, 'code': proc.returncode, 'out': out}


def cmd_gate(args) -> int:
    checks = {
        'verify': run_script('codex_verify.py',
                             ['gate', '--mode', 'saw', '--for-ai']),
        'refactor': run_script('codex_refactor.py', ['analyze', '--for-ai']),
    }
    ok = checks['verify']['ok']
    print(json.dumps({'ok': ok, 'checks': checks}, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def cmd_followup(args) -> int:
    agent = {'test': 'test', 'refactor': 'refactor',
             'security': 'security'}[args.kind]
    text = args.title or f'{args.kind} follow up'
    skills = codex_skills.recommend(text, agent)
    tid = add_task(current_saw(), text, agent, skills, text)
    print(json.dumps({'task_id': tid, 'agent': agent, 'skills': skills},
                     ensure_ascii=False, indent=2)); return 0


def cmd_status(args) -> int:
    cur = current_saw(); tasks = codex_state.read_tasks(cur)
    data = [{'id': t['id'], 'agent': t.get('agent'), 'status': t.get('status'),
             'feature': t.get('feature'), 'purpose': t.get('purpose'),
             'acceptance': t.get('acceptance'),
             'commits': len(t.get('commits', [])), 'title': t.get('title')}
            for t in tasks]
    print(json.dumps({'mode': cur.get('saw_mode', 'lite'), 'tasks': data},
                     ensure_ascii=False, indent=2)); return 0


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest='cmd', required=True)
    i = sub.add_parser('init'); i.add_argument('--title', required=True)
    i.add_argument('--branch', required=True); i.add_argument('--base-branch', default='main')
    i.add_argument('--bump', choices=['major', 'minor', 'patch'], default='patch')
    i.add_argument('--text', default=''); i.add_argument('--agents', default='')
    for name in ['suggest', 'apply']:
        s = sub.add_parser(name); s.add_argument('--text', required=True)
        s.add_argument('--agents', default=''); s.add_argument('--title', default='')
    sub.add_parser('next'); sub.add_parser('prompt'); sub.add_parser('status')
    sub.add_parser('gate')
    f = sub.add_parser('followup'); f.add_argument('--kind', required=True,
        choices=['test', 'refactor', 'security'])
    f.add_argument('--title', default='')
    args = p.parse_args(); return globals()['cmd_' + args.cmd](args)


if __name__ == '__main__':
    raise SystemExit(main())
