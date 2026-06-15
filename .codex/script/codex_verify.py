#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shlex, subprocess, sys
from pathlib import Path
import lib

CODE_EXT = {'.java', '.kt', '.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs'}
DOC_EXT = {'.md', '.txt', '.adoc', '.rst'}
SKIP = {'.git', '.codex-state', 'node_modules', 'dist', 'build'}


def run(cmd: list[str], cwd: Path, timeout: int) -> dict:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = (p.stdout or p.stderr).strip()
        return {'cmd': ' '.join(shlex.quote(x) for x in cmd),
                'ok': p.returncode == 0, 'code': p.returncode,
                'out': out[-3000:]}
    except subprocess.TimeoutExpired:
        return {'cmd': ' '.join(cmd), 'ok': False, 'code': 124,
                'out': 'timeout'}


def git_names(cwd: Path, staged: bool, base: str) -> list[str]:
    if staged:
        cmd = ['git', 'diff', '--cached', '--name-only']
    elif base:
        cmd = ['git', 'diff', '--name-only', f'{base}..HEAD']
    else:
        cmd = ['git', 'diff', '--name-only', 'HEAD']
    p = subprocess.run(cmd, cwd=str(cwd), text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        return []
    return [x for x in p.stdout.splitlines() if x.strip()]


def useful(path: str) -> bool:
    return not any(part in SKIP for part in Path(path).parts)


def changed_files(args) -> list[str]:
    cwd = Path(args.cwd).resolve() if args.cwd else lib.root_dir()
    return [x for x in git_names(cwd, args.staged, args.base) if useful(x)]


def has_code(files: list[str]) -> bool:
    return any(Path(x).suffix in CODE_EXT for x in files)


def docs_only(files: list[str]) -> bool:
    return bool(files) and all(Path(x).suffix in DOC_EXT for x in files)

def load_config(cwd: Path) -> dict:
    path = lib.find_codex() / 'state' / 'verify.json'
    default = {'commands': [], 'test_commands': [], 'saw_commands': [],
               'maw_commands': [], 'code_requires_test': True}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            default.update(data)
        except json.JSONDecodeError:
            pass
    return default


def package_manager(cwd: Path) -> str:
    if (cwd / 'pnpm-lock.yaml').exists():
        return 'pnpm'
    if (cwd / 'yarn.lock').exists():
        return 'yarn'
    return 'npm'


def package_scripts(cwd: Path) -> dict:
    path = cwd / 'package.json'
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8')).get('scripts', {})
    except json.JSONDecodeError:
        return {}


def detected_commands(cwd: Path, files: list[str], mode: str) -> list[list[str]]:
    cmds: list[list[str]] = []
    scripts = package_scripts(cwd)
    if scripts:
        pm = package_manager(cwd)
        names = ['typecheck', 'lint', 'test'] if mode != 'maw' else ['typecheck', 'lint', 'test', 'e2e']
        for name in names:
            if name in scripts:
                cmds.append([pm, 'run', name])
    if any(Path(x).suffix == '.py' for x in files) and (cwd / 'tests').exists():
        cmds.append([sys.executable, '-m', 'pytest', '-q'])
    if any(Path(x).suffix == '.java' for x in files):
        if (cwd / 'gradlew').exists():
            cmds.append(['./gradlew', 'test', '--no-daemon'])
        elif (cwd / 'mvnw').exists():
            cmds.append(['./mvnw', 'test'])
        elif (cwd / 'pom.xml').exists():
            cmds.append(['mvn', 'test'])
    return cmds


def configured_commands(cwd: Path, mode: str) -> list[list[str]]:
    out = []
    conf = load_config(cwd)
    key = 'maw_commands' if mode == 'maw' else 'saw_commands'
    items = conf.get(key) or conf.get('test_commands') or conf.get('commands', [])
    for item in items:
        if isinstance(item, str):
            out.append(shlex.split(item))
        elif isinstance(item, list):
            out.append([str(x) for x in item])
    return out


def call_script(name: str, extra: list[str], cwd: Path, timeout: int) -> dict:
    path = lib.find_codex() / 'script' / name
    return run([sys.executable, str(path), *extra], cwd, timeout)


def analyze(args) -> dict:
    cwd = Path(args.cwd).resolve() if args.cwd else lib.root_dir()
    files = changed_files(args)
    data = {'files': files, 'docs_only': docs_only(files),
            'code_changed': has_code(files), 'checks': []}
    qargs = ['gate', '--cwd', str(cwd)] + (['--staged'] if args.staged else [])
    sargs = ['gate', '--cwd', str(cwd)] + (['--staged'] if args.staged else [])
    bargs = ['gate', '--cwd', str(cwd), '--mode', args.mode] + (['--staged'] if args.staged else [])
    data['checks'].append({'name': 'budget', **call_script('codex_budget.py', bargs, cwd, args.timeout)})
    data['checks'].append({'name': 'quality', **call_script('codex_quality.py', qargs, cwd, args.timeout)})
    data['checks'].append({'name': 'security', **call_script('codex_security.py', sargs, cwd, args.timeout)})
    if data['docs_only'] or not data['code_changed']:
        data['test_policy'] = 'skipped_docs_or_no_code'
        data['tests'] = {'status': 'skipped', 'reason': data['test_policy']}
    else:
        cmds = configured_commands(cwd, args.mode) or detected_commands(cwd, files, args.mode)
        if not cmds:
            data['test_policy'] = 'missing_test_command'
            data['tests'] = {'status': 'missing', 'reason': 'no test command detected'}
            data['checks'].append({'name': 'test', 'ok': bool(args.allow_no_test),
                                   'code': 2, 'cmd': '',
                                   'out': 'no test command detected'})
        else:
            data['test_policy'] = 'executed'
            data['tests'] = {'status': 'executed', 'count': len(cmds)}
            for idx, cmd in enumerate(cmds, 1):
                data['checks'].append({'name': f'test-{idx}', **run(cmd, cwd, args.timeout)})
    data['ok'] = all(x.get('ok') for x in data['checks'])
    return data


def verify(args) -> dict:
    return analyze(args)


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest='cmd', required=True)
    for name in ['analyze', 'gate']:
        s = sub.add_parser(name); s.add_argument('--cwd', default='')
        s.add_argument('--staged', action='store_true'); s.add_argument('--base', default='')
        s.add_argument('--allow-no-test', action='store_true')
        s.add_argument('--mode', choices=['saw', 'maw', 'auto'], default='auto')
        s.add_argument('--timeout', type=int, default=120)
        s.add_argument('--for-ai', action='store_true')
    args = p.parse_args(); data = analyze(args)
    if args.for_ai:
        data['checks'] = [{k: v for k, v in x.items() if k != 'out'} for x in data['checks']]
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if args.cmd == 'analyze' or data['ok'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
