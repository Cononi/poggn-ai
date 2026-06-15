#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path
import lib, codex_state, codex_trace_view

MAX_FILES = 14
MAX_LINES = 40


def run(cmd: list[str], cwd: Path) -> str:
    p = subprocess.run(cmd, cwd=str(cwd), text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout if p.returncode == 0 else ''


def diff_names(cwd: Path, staged: bool, base: str) -> list[str]:
    if staged: cmd = ['git', 'diff', '--cached', '--name-status']
    elif base: cmd = ['git', 'diff', '--name-status', f'{base}..HEAD']
    else: cmd = ['git', 'diff', '--name-status', 'HEAD']
    return [x for x in run(cmd, cwd).splitlines() if x.strip()]


def head(path: Path, limit: int) -> list[str]:
    try:
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception:
        return []
    out = []
    for idx, line in enumerate(lines[:limit], 1):
        if any(x in line.lower() for x in ['secret', 'token', 'password', 'private key']):
            line = '<redacted>'
        out.append(f'{idx}: {line[:160]}')
    return out


def task(cur: dict, tid: str) -> dict:
    for item in codex_state.read_tasks(cur):
        if item.get('id') == tid: return item
    return {}


def pack(args) -> dict:
    cwd = Path(args.cwd).resolve() if args.cwd else lib.root_dir()
    cur = codex_state.current()
    token_policy_data = lib.read_json(lib.find_codex() / 'state' / 'token_policy.json', {})
    data = {'cwd': str(cwd), 'time': lib.now(), 'language': lib.language(),
            'token_policy': token_policy_data}
    if cur:
        data['workflow'] = {'type': cur.get('workflow'), 'phase': cur.get('phase'),
                            'title': cur.get('title'), 'path': cur.get('path')}
        wave_map = {}
        for row in codex_trace_view.lanes(cur):
            w = row.get('wave', 'W001')
            item = wave_map.setdefault(w, {'lanes': 0, 'done': 0})
            item['lanes'] += 1
            item['done'] += 1 if row.get('status') in {'done', 'merged'} else 0
        data['waves'] = wave_map
        if args.task:
            data['task'] = task(cur, args.task)
            data['commits'] = [x for x in codex_trace_view.commits(cur)
                               if x.get('task_id') == args.task][-5:]
    rows = diff_names(cwd, args.staged, args.base)
    data['change_count'] = len(rows)
    data['changes'] = rows[:MAX_FILES]
    if len(rows) > MAX_FILES:
        data['changes'].append(f'+{len(rows) - MAX_FILES} more changes '
                               f'(showing {MAX_FILES}/{len(rows)} total)')
    if args.snippets:
        snippets = {}
        for row in rows[:min(args.max_files, MAX_FILES)]:
            rel = row.split('\t')[-1]; path = cwd / rel
            if path.is_file(): snippets[rel] = head(path, args.max_lines)
        data['snippets'] = snippets
    return data


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('pack'); c.add_argument('--cwd', default='')
    c.add_argument('--staged', action='store_true'); c.add_argument('--base', default='')
    c.add_argument('--task', default=''); c.add_argument('--snippets', action='store_true')
    c.add_argument('--max-files', type=int, default=6); c.add_argument('--max-lines', type=int, default=MAX_LINES)
    c.add_argument('--for-ai', action='store_true')
    args = p.parse_args(); print(json.dumps(pack(args), ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
