#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys, py_compile
from pathlib import Path
import lib


def run(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, timeout=15,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.returncode == 0, (p.stdout or p.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, 'timeout'


def py_compile_check(codex: Path) -> tuple[bool, str]:
    bad = []
    for path in sorted((codex / 'script').glob('*.py')):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            bad.append(str(path.relative_to(codex.parent)) + ': ' + str(exc)[-200:])
    return not bad, '\n'.join(bad) or 'ok'


def line_gate(codex: Path) -> tuple[bool, str]:
    bad = []
    for path in codex.rglob('*.py'):
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
        if len(lines) > 200:
            bad.append(f'{path.relative_to(codex.parent)} lines:{len(lines)}')
    md_files = list(codex.rglob('*.md')) + list((codex.parent / 'docs').rglob('*.md'))
    for path in md_files:
        for i, line in enumerate(path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
            if len(line) > 100 and not line.startswith('|'):
                bad.append(f'{path.relative_to(codex.parent)}:{i} chars:{len(line)}')
                break
    return not bad, '\n'.join(bad[:20]) or 'ok'


def check(args) -> dict:
    root = lib.root_dir(); codex = lib.find_codex(); rows = []
    def add(name: str, ok: bool, detail: str = '', level: str = 'error') -> None:
        rows.append({'name': name, 'ok': ok, 'level': level, 'detail': detail[:300]})
    add('python', True, sys.version.split()[0], 'info')
    add('git-command', lib.has_cmd('git'), level='error')
    git_repo = False
    if lib.has_cmd('git'):
        git_repo, out = run(['git', 'rev-parse', '--is-inside-work-tree'], root)
        add('git-repo', git_repo, out or 'ok', 'warn')
        ok, out = run(['git', 'remote', '-v'], root) if git_repo else (False, '')
        add('git-remote', ok and bool(out), out.splitlines()[0] if out else 'missing', 'warn')
    add('codex-dir', codex.exists(), str(codex), 'error')
    add('hooks-json', (codex / 'hooks.json').exists(), level='error')
    add('verify-config', (codex / 'state' / 'verify.json').exists(), level='error')
    add('token-policy', (codex / 'state' / 'token_policy.json').exists(), level='error')
    add('budget-config', (codex / 'state' / 'budget.json').exists(), level='error')
    skills = list((codex / 'skills').glob('*/SKILL.md'))
    agents = list((codex / 'agents').glob('*.toml'))
    add('skills', bool(skills), str(len(skills)), 'error')
    add('agents', bool(agents), str(len(agents)), 'error')
    link = root / '.agents' / 'skills'
    add('agents-skills-link', link.exists(), str(link), 'warn')
    if args.deep:
        ok, out = run([sys.executable, str(codex / 'script' / 'codex_docs.py'), 'gate'], root)
        add('docs-gate', ok, out[-300:], 'error')
        ok, out = py_compile_check(codex); add('py-compile', ok, out, 'error')
        ok, out = line_gate(codex); add('line-gate', ok, out, 'error')
        ok, out = run([sys.executable, str(codex / 'script' / 'codex_agents.py'),
                       'check'], root)
        add('agent-schema', ok, out[-300:], 'error')
    fatal_ok = all(x['ok'] for x in rows if x['level'] == 'error')
    return {'ok': fatal_ok, 'warnings': [x for x in rows if x['level'] == 'warn' and not x['ok']],
            'checks': rows}


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument('--deep', action='store_true')
    p.add_argument('--for-ai', action='store_true')
    args = p.parse_args(); data = check(args)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if data['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
