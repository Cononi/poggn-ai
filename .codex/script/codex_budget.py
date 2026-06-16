#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path
import lib, codex_state

CODE = {'.java', '.kt', '.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs'}
DOC = {'.md', '.txt', '.adoc', '.rst'}
RISK = re.compile(r'(?i)(auth|role|permission|security|payment|secret|token|'
                  r'migration|schema|deploy|ci|workflow|password|key)')
DEFAULTS = {
    'saw': {'max_files': 6, 'max_code_files': 4,
            'max_lines': 260, 'max_new_files': 3},
    'maw': {'max_lanes_per_wave': 4, 'max_files_per_wave': 32,
            'max_lines_per_wave': 1400, 'max_files_per_lane': 8,
            'max_lines_per_lane': 350, 'allow_epic_total_over_budget': True},
}


def config() -> dict:
    path = lib.find_codex() / 'state' / 'budget.json'
    data = lib.read_json(path, {})
    out = json.loads(json.dumps(DEFAULTS))
    for key in DEFAULTS:
        out[key] = {**DEFAULTS[key], **data.get(key, {})}
    return out


def run(cmd: list[str], cwd: Path) -> str:
    p = subprocess.run(cmd, cwd=str(cwd), text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout if p.returncode == 0 else ''


def names(cwd: Path, staged: bool, base: str) -> list[str]:
    if staged:
        cmd = ['git', 'diff', '--cached', '--name-only']
    elif base:
        cmd = ['git', 'diff', '--name-only', f'{base}..HEAD']
    else:
        cmd = ['git', 'diff', '--name-only', 'HEAD']
    return [x for x in run(cmd, cwd).splitlines() if x.strip()]


def numstat(cwd: Path, staged: bool, base: str) -> list[dict]:
    if staged:
        cmd = ['git', 'diff', '--cached', '--numstat']
    elif base:
        cmd = ['git', 'diff', '--numstat', f'{base}..HEAD']
    else:
        cmd = ['git', 'diff', '--numstat', 'HEAD']
    rows = []
    for line in run(cmd, cwd).splitlines():
        a, d, path, *_ = (line.split('\t') + ['', '', ''])[:3]
        rows.append({'path': path, 'add': int(a) if a.isdigit() else 0,
                     'del': int(d) if d.isdigit() else 0})
    return rows


def text_features(text: str) -> list[str]:
    table = {'order': 'order 주문', 'payment': 'payment 결제',
             'member': 'member user 회원', 'product': 'product 상품',
             'cart': 'cart 장바구니', 'coupon': 'coupon 쿠폰',
             'post': 'post article board community forum 게시글 게시판 커뮤니티',
             'comment': 'comment reply community forum 댓글 커뮤니티',
             'frontend': 'frontend react ui 화면'}
    low = text.lower(); found = []
    for name, keys in table.items():
        if any(k in low for k in keys.split()) and name not in found:
            found.append(name)
    return found


def estimate_lanes(features: list[str], agents: str) -> int:
    selected = {x.strip() for x in agents.split(',') if x.strip()}
    domain = [x for x in features if x != 'frontend'] or ['api']
    wants = lambda x: x in selected
    default_agents = not selected
    impl = 0
    if wants('database'):
        impl += 1
    if default_agents or wants('backend'):
        impl += max(1, len(domain))
    if (default_agents and 'frontend' in features) or wants('frontend'):
        impl += max(1, len(domain))
    if wants('integration'):
        impl += max(1, len(domain))
    contract_agents = {
        'backend', 'frontend', 'database', 'integration', 'devops', 'docs',
        'performance', 'test_writer', 'test_runner', 'qa', 'refactor', 'security',
        'architecture'
    }
    count = 1 if default_agents or selected & contract_agents else 0
    count += impl
    per_impl_guards = ['test_writer', 'test_runner', 'qa', 'refactor', 'security']
    for guard in per_impl_guards:
        if wants(guard):
            count += max(1, impl)
    if wants('test'):
        count += max(1, impl)
    return count or 1


def mode(args) -> str:
    if args.mode != 'auto': return args.mode
    cur = codex_state.current()
    return cur.get('workflow', 'saw') if cur else 'saw'


def scope(args) -> str:
    if args.scope != 'auto': return args.scope
    if mode(args) == 'maw': return 'lane' if args.staged else 'wave'
    return 'patch'


def analyze_text(args) -> dict:
    feats = text_features(args.text); lim = config()['maw']
    lanes = estimate_lanes(feats, getattr(args, 'agents', ''))
    per = int(lim['max_lanes_per_wave'])
    waves = max(1, (lanes + per - 1) // per)
    decision = 'maw_split_waves' if waves > 1 else 'maw_single_wave'
    if len([x for x in feats if x != 'frontend']) <= 1:
        decision = 'saw_ok_or_maw_single_wave'
    return {'mode': 'route', 'decision': decision, 'ok': True,
            'features': feats, 'estimated_lanes': lanes,
            'max_lanes_per_wave': per, 'estimated_waves': waves,
            'note': 'MAW budget is per wave/lane, not whole epic.'}


def analyze(args) -> dict:
    cwd = Path(args.cwd).resolve() if args.cwd else lib.root_dir()
    if args.text: return analyze_text(args)
    files = names(cwd, args.staged, args.base)
    stats = numstat(cwd, args.staged, args.base)
    adds = sum(x['add'] for x in stats); dels = sum(x['del'] for x in stats)
    code = [x for x in files if Path(x).suffix in CODE]
    docs = [x for x in files if Path(x).suffix in DOC]
    new_files = [x['path'] for x in stats if x['add'] and not x['del']]
    risky = [x for x in files if RISK.search(x)]
    m = mode(args); sc = scope(args); lim = config()[m]
    reasons = []
    if m == 'saw':
        if len(files) > lim['max_files']: reasons.append('too_many_files')
        if len(code) > lim['max_code_files']: reasons.append('too_many_code_files')
        if adds + dels > lim['max_lines']: reasons.append('too_many_changed_lines')
        if len(new_files) > lim['max_new_files']: reasons.append('too_many_new_files')
    elif sc == 'lane':
        if len(files) > lim['max_files_per_lane']: reasons.append('lane_too_many_files')
        if adds + dels > lim['max_lines_per_lane']: reasons.append('lane_too_many_lines')
    elif sc == 'wave':
        if len(files) > lim['max_files_per_wave']: reasons.append('wave_too_many_files')
        if adds + dels > lim['max_lines_per_wave']: reasons.append('wave_too_many_lines')
    ok = not reasons or sc == 'epic'
    decision = 'ok' if ok else ('split_or_maw' if m == 'saw' else 'split_wave_or_lane')
    return {'mode': m, 'scope': sc, 'decision': decision, 'ok': ok,
            'files': len(files), 'code_files': len(code), 'docs': len(docs),
            'added': adds, 'deleted': dels, 'risky_files': risky[:12],
            'reasons': reasons, 'limits': lim,
            'note': 'MAW total epic may exceed budget; each lane/wave must fit.'}


def token_path() -> Path: return lib.find_codex() / 'state' / 'token_policy.json'


def token_policy() -> dict:
    default = {'shortcut_limit': 3000, 'for_ai_limit': 2000,
               'diff_file_limit': 40, 'trace_task_limit': 20}
    data = lib.read_json(token_path(), {})
    default.update(data if isinstance(data, dict) else {})
    return default


def limit_value(name: str, default: int = 3000) -> int:
    try: return int(token_policy().get(name, default))
    except Exception: return default


def cmd_status(args) -> int:
    print(json.dumps({'scope_budget': config(), 'token_policy': token_policy()},
                     ensure_ascii=False, indent=2)); return 0


def cmd_set(args) -> int:
    data = token_policy()
    if args.shortcut_limit is not None: data['shortcut_limit'] = args.shortcut_limit
    if args.for_ai_limit is not None: data['for_ai_limit'] = args.for_ai_limit
    lib.write_json(token_path(), data)
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest='cmd', required=True)
    sub.add_parser('status')
    st = sub.add_parser('set'); st.add_argument('--shortcut-limit', type=int)
    st.add_argument('--for-ai-limit', type=int)
    for name in ['analyze', 'gate', 'suggest']:
        s = sub.add_parser(name); s.add_argument('--cwd', default='')
        s.add_argument('--staged', action='store_true'); s.add_argument('--base', default='')
        s.add_argument('--mode', choices=['auto', 'saw', 'maw'], default='auto')
        s.add_argument('--scope', choices=['auto', 'patch', 'lane', 'wave', 'epic'], default='auto')
        s.add_argument('--text', default=''); s.add_argument('--agents', default='')
        s.add_argument('--for-ai', action='store_true')
    args = p.parse_args()
    if args.cmd == 'status': return cmd_status(args)
    if args.cmd == 'set': return cmd_set(args)
    data = analyze(args)
    if args.for_ai: data.pop('limits', None)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if args.cmd in {'analyze', 'suggest'} or data.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
