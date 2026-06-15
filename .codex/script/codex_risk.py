#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path
import lib

HIGH_WORDS = 'auth permission role security secret token payment 결제 권한 인증 deploy 배포'
DB_WORDS = 'database schema migration index ddl entity db 데이터베이스 마이그레이션'
FE_WORDS = 'frontend react next ui tsx component page 화면 컴포넌트'
BE_WORDS = 'backend api spring jpa controller service dto 서버'
INFRA_WORDS = 'docker kubernetes terraform actions gitlab-ci github-actions ci cd infra'
DOC_EXT = {'.md', '.txt', '.adoc', '.rst'}
CODE_EXT = {'.java', '.kt', '.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.rs'}


def words(text: str) -> set[str]:
    return set(re.findall(r'[A-Za-z0-9가-힣_]+', text.lower()))


def git_names(cwd: Path, staged: bool, base: str) -> list[str]:
    cmd = ['git', 'diff', '--cached', '--name-status'] if staged else ['git', 'diff', '--name-status']
    if base and not staged:
        cmd = ['git', 'diff', '--name-status', f'{base}..HEAD']
    p = subprocess.run(cmd, cwd=str(cwd), text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.splitlines() if p.returncode == 0 else []


def parse_files(rows: list[str]) -> list[dict]:
    out = []
    for row in rows:
        parts = row.split('\t')
        if not parts:
            continue
        status, path = parts[0], parts[-1]
        out.append({'status': status, 'path': path, 'ext': Path(path).suffix})
    return out


def areas(text: str, files: list[dict]) -> set[str]:
    w = words(text); out = set()
    joined = ' '.join(x['path'].lower() for x in files)
    if w & words(FE_WORDS) or any(x['ext'] in {'.tsx', '.jsx', '.vue'} for x in files):
        out.add('frontend')
    if w & words(BE_WORDS) or any('/controller' in x['path'].lower() for x in files):
        out.add('backend')
    if w & words(DB_WORDS) or re.search(r'migration|schema|entity|repository', joined):
        out.add('database')
    if w & words(INFRA_WORDS) or re.search(r'docker|k8s|workflow|gitlab-ci|terraform', joined):
        out.add('infra')
    if w & words(HIGH_WORDS):
        out.add('security')
    return out


def classify(args) -> dict:
    cwd = Path(args.cwd).resolve() if args.cwd else lib.root_dir()
    files = parse_files(git_names(cwd, args.staged, args.base))
    exts = {x['ext'] for x in files}
    doc_only = bool(files) and all(x in DOC_EXT for x in exts if x)
    code = any(x in CODE_EXT for x in exts)
    ar = areas(args.text, files)
    risk = 'low'; reasons = []
    if doc_only and not code:
        reasons.append('docs_only')
    if len(files) > 8:
        risk = 'medium'; reasons.append('many_files')
    if {'frontend', 'backend'} <= ar:
        risk = 'high'; reasons.append('cross_stack')
    if ar & {'security', 'database', 'infra'}:
        risk = 'high'; reasons.append('high_risk_area')
    if any(x['status'].startswith('D') for x in files):
        risk = 'high'; reasons.append('delete_detected')
    if args.text and len([x for x in re.split(r',|/|\s+', args.text) if x]) > 18:
        risk = 'medium' if risk == 'low' else risk
        reasons.append('broad_prompt')
    workflow = 'saw' if risk == 'low' and len(ar) <= 1 else 'maw'
    gates = ['quality', 'verify', 'security']
    if risk == 'high':
        gates += ['full-test', 'human-review']
    return {'risk': risk, 'workflow': workflow, 'areas': sorted(ar),
            'files': len(files), 'code_changed': code, 'docs_only': doc_only,
            'reasons': reasons, 'gates': gates}


def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('classify'); c.add_argument('--text', default='')
    c.add_argument('--cwd', default=''); c.add_argument('--staged', action='store_true')
    c.add_argument('--base', default=''); c.add_argument('--for-ai', action='store_true')
    args = p.parse_args(); data = classify(args)
    if args.for_ai:
        data.pop('reasons', None) if data.get('risk') == 'low' else None
    print(json.dumps(data, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
