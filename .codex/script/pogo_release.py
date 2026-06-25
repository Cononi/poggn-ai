#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
PROJECT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
GRADLE_VERSION = re.compile(r"^\s*version\s*=\s*[\"']([^\"']+)[\"']\s*$")
PROJECT_MAP_PATH = ROOT / ".codex" / "project-map.json"


def run(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def text_or_none(args: list[str]) -> str | None:
    proc = run(args)
    if proc.returncode:
        return None
    return proc.stdout.strip() or None


def _repo_relative(value: str, field: str) -> str:
    if not value or Path(value).is_absolute() or ".." in Path(value).parts:
        raise SystemExit(f"project-map {field} must be a repository-relative path")
    return value.rstrip("/") or "."


def load_project_map() -> dict:
    if not PROJECT_MAP_PATH.exists():
        return {"version": 1, "projects": []}
    try:
        data = json.loads(PROJECT_MAP_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid project map: {exc}") from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise SystemExit("project-map version must be 1")
    projects = data.get("projects")
    if not isinstance(projects, list):
        raise SystemExit("project-map projects must be a list")
    seen: set[str] = set()
    for project in projects:
        if not isinstance(project, dict):
            raise SystemExit("project-map project entries must be objects")
        name = project.get("name")
        if not isinstance(name, str) or not PROJECT.fullmatch(name):
            raise SystemExit("project-map project.name is invalid")
        if name in seen:
            raise SystemExit(f"duplicate project-map project: {name}")
        seen.add(name)
        raw_paths = project.get("paths", project.get("path"))
        if isinstance(raw_paths, str):
            paths = [raw_paths]
        elif isinstance(raw_paths, list):
            paths = raw_paths
        else:
            raise SystemExit(f"project-map {name}.paths must be a non-empty list")
        if not paths:
            raise SystemExit(f"project-map {name}.paths must not be empty")
        project["paths"] = [_repo_relative(str(item), f"{name}.paths") for item in paths]
        if "versionSource" in project and project["versionSource"] is not None:
            project["versionSource"] = _repo_relative(str(project["versionSource"]), f"{name}.versionSource")
        if "release" in project and not isinstance(project["release"], bool):
            raise SystemExit(f"project-map {name}.release must be true or false")
    return data


def mapped_project(name: str) -> dict | None:
    for project in load_project_map().get("projects", []):
        if project.get("name") == name:
            return project
    return None


def project_primary_path(project: dict) -> str:
    paths = project.get("paths") or [project.get("path") or "."]
    return str(paths[0])


def path_matches(changed_file: str, project_path: str) -> bool:
    normalized = project_path.rstrip("/")
    if normalized == ".":
        return True
    return changed_file == normalized or changed_file.startswith(normalized + "/")


def project_matches(project: dict, changed_file: str) -> bool:
    return any(path_matches(changed_file, project_path) for project_path in project.get("paths", []))


def rev_exists(ref: str) -> bool:
    proc = run(["git", "rev-parse", "--verify", "--quiet", ref])
    return proc.returncode == 0


def default_from_ref() -> str:
    for ref in ("origin/main", "main", "HEAD~1"):
        if rev_exists(ref):
            return ref
    return "HEAD"


def changed_files(from_ref: str | None, to_ref: str | None) -> list[str]:
    base = from_ref or default_from_ref()
    target = to_ref or "HEAD"
    if base == target:
        return []
    proc = run(["git", "diff", "--name-only", f"{base}...{target}"])
    if proc.returncode:
        proc = run(["git", "diff", "--name-only", f"{base}..{target}"])
    if proc.returncode:
        raise SystemExit(proc.stderr.strip() or "unable to collect changed files")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def default_project() -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", ROOT.name).strip("-") or "app"


def project_name(args: argparse.Namespace) -> str:
    project = args.project or default_project()
    if not PROJECT.fullmatch(project):
        raise SystemExit("project must match [A-Za-z0-9][A-Za-z0-9._-]*")
    return project


def project_path(args: argparse.Namespace) -> Path:
    project = mapped_project(args.project) if getattr(args, "project", None) else None
    value = args.path or (project_primary_path(project) if project else ".")
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit("--path must stay inside the repository") from exc
    return path


def display_path(path: Path) -> str:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return str(path)
    return str(relative) or "."


def read_package_json(path: Path, out: list[str]) -> None:
    package_json = path / "package.json"
    if not package_json.exists():
        return
    try:
        version = json.loads(package_json.read_text(encoding="utf-8")).get("version")
        if version:
            out.append(f"{display_path(package_json)}:{version}")
    except Exception as exc:
        out.append(f"{display_path(package_json)}:invalid ({exc})")


def read_version_files(path: Path, out: list[str]) -> None:
    version_file = path / "VERSION"
    if version_file.exists():
        out.append(f"{display_path(version_file)}:{version_file.read_text(encoding='utf-8').strip()}")
    version_json = path / "version.json"
    if version_json.exists():
        try:
            data = json.loads(version_json.read_text(encoding="utf-8"))
            out.append(f"{display_path(version_json)}:{data.get('version', 'missing')}")
        except Exception as exc:
            out.append(f"{display_path(version_json)}:invalid ({exc})")


def read_gradle(path: Path, out: list[str]) -> None:
    for name in ("build.gradle", "build.gradle.kts"):
        gradle = path / name
        if not gradle.exists():
            continue
        try:
            for line in gradle.read_text(encoding="utf-8").splitlines():
                match = GRADLE_VERSION.match(line)
                if match:
                    out.append(f"{display_path(gradle)}:{match.group(1)}")
                    break
            else:
                out.append(f"{display_path(gradle)}:version missing")
        except Exception as exc:
            out.append(f"{display_path(gradle)}:invalid ({exc})")
    gradle_properties = path / "gradle.properties"
    if gradle_properties.exists():
        try:
            for line in gradle_properties.read_text(encoding="utf-8").splitlines():
                if line.startswith("version="):
                    out.append(f"{display_path(gradle_properties)}:{line.split('=', 1)[1].strip()}")
                    break
        except Exception as exc:
            out.append(f"{display_path(gradle_properties)}:invalid ({exc})")


def read_pom(path: Path, out: list[str]) -> None:
    pom = path / "pom.xml"
    if not pom.exists():
        return
    try:
        root = ET.fromstring(pom.read_text(encoding="utf-8"))
        namespace = ""
        if root.tag.startswith("{"):
            namespace = root.tag.split("}", 1)[0] + "}"
        version = root.findtext(f"{namespace}version")
        out.append(f"{display_path(pom)}:{version or 'version missing'}")
    except Exception as exc:
        out.append(f"{display_path(pom)}:invalid ({exc})")


def read_version_source(source: Path) -> str:
    if source.name in {"package.json", "version.json"}:
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("version"), str):
            raise ValueError("version key missing")
        return data["version"]
    return source.read_text(encoding="utf-8").strip()


def version_sources(path: Path, project: dict | None = None) -> list[str]:
    out: list[str] = []
    if project and project.get("versionSource"):
        source = ROOT / project["versionSource"]
        if source.exists():
            try:
                out.append(f"{display_path(source)}:{read_version_source(source)}")
            except Exception as exc:
                out.append(f"{display_path(source)}:invalid ({exc})")
        else:
            out.append(f"{project['versionSource']}:missing")
        return out
    read_package_json(path, out)
    read_version_files(path, out)
    read_gradle(path, out)
    read_pom(path, out)
    return out


def tag_for(project: str, version: str) -> str:
    if not SEMVER.fullmatch(version):
        raise SystemExit("version must be semver, for example 1.2.3 or 1.2.3-beta.1")
    return f"{project}-v{version}"


def validate_tag(project: str, tag: str) -> None:
    prefix = f"{project}-v"
    if not tag.startswith(prefix):
        raise SystemExit(f"tag must use project prefix: {prefix}<semver>")
    version = tag[len(prefix) :]
    if not SEMVER.fullmatch(version):
        raise SystemExit("tag must use semver: <project>-v<semver>")


def latest_project_tag(project: str) -> str | None:
    proc = run(["git", "tag", "--list", f"{project}-v*", "--sort=-version:refname"])
    if proc.returncode:
        return None
    tags = proc.stdout.splitlines()
    return tags[0] if tags else None


def current_version(path: Path, project: dict | None) -> str | None:
    sources = version_sources(path, project)
    if not sources:
        return None
    value = sources[0].rsplit(":", 1)[-1].strip()
    return value if SEMVER.fullmatch(value) else None


def project_scope_paths(project: dict | None, path: Path) -> list[str]:
    if project and project.get("paths"):
        return [str(item) for item in project["paths"]]
    return [display_path(path)]


def collect_commits(rev_range: str, paths: list[str]) -> list[tuple[str, str]]:
    proc = run([
        "git",
        "log",
        "--no-merges",
        "--pretty=format:%h%x1f%s",
        rev_range,
        "--",
        *paths,
    ])
    if proc.returncode:
        raise SystemExit(proc.stderr.strip() or "Unable to collect git log")
    commits: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in proc.stdout.splitlines():
        if "\x1f" not in line:
            continue
        short, subject = line.split("\x1f", 1)
        if short in seen:
            continue
        seen.add(short)
        commits.append((short, subject))
    return commits


def collect_merge_commits(rev_range: str, paths: list[str]) -> list[dict[str, str]]:
    proc = run([
        "git",
        "log",
        "--merges",
        "--pretty=format:%H%x1f%h%x1f%s%x1f%b%x1e",
        rev_range,
        "--",
        *paths,
    ])
    if proc.returncode:
        raise SystemExit(proc.stderr.strip() or "Unable to collect merge git log")
    commits: list[dict[str, str]] = []
    seen: set[str] = set()
    for record in proc.stdout.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\x1f", 3)
        if len(parts) != 4:
            continue
        full, short, subject, body = parts
        if full in seen:
            continue
        seen.add(full)
        commits.append({
            "full": full,
            "short": short,
            "subject": subject.strip(),
            "body": body.strip(),
        })
    return commits


FOOTER = re.compile(r"^(?:[A-Za-z0-9-]+|BREAKING CHANGE):\s+.+$")


def split_body_footer(body: str) -> tuple[str, list[str]]:
    lines = [line.rstrip() for line in body.splitlines()]
    while lines and not lines[-1].strip():
        lines.pop()
    footer: list[str] = []
    while lines and FOOTER.match(lines[-1].strip()):
        footer.append(lines.pop().strip())
    while lines and not lines[-1].strip():
        lines.pop()
    footer.reverse()
    return "\n".join(lines).strip(), footer


def collect_changed_files(base: str | None, target: str, paths: list[str]) -> list[str]:
    files = changed_files(base, target)
    return [item for item in files if any(path_matches(item, path) for path in paths)]


def category_for(subject: str) -> str:
    lowered = subject.lower()
    if lowered.startswith("feat"):
        return "추가"
    if lowered.startswith("fix"):
        return "수정"
    if lowered.startswith(("docs", "chore", "ci", "build")):
        return "운영/문서"
    if lowered.startswith(("refactor", "perf")):
        return "개선"
    if lowered.startswith("test"):
        return "검증"
    return "변경"


def print_commit_groups(commits: list[tuple[str, str]]) -> None:
    groups = ["추가", "수정", "개선", "검증", "운영/문서", "변경"]
    grouped = {name: [] for name in groups}
    for short, subject in commits:
        grouped[category_for(subject)].append((short, subject))
    for name in groups:
        entries = grouped[name]
        if not entries:
            continue
        print(f"### {name}\n")
        for short, subject in entries:
            print(f"- {subject} (`{short}`)")
        print()


def add_scope_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", help="release project name; tag format is <project>-v<semver>")
    parser.add_argument("--path", help="project path inside the repository; defaults to repo root")


def status(args: argparse.Namespace) -> int:
    inside = text_or_none(["git", "rev-parse", "--is-inside-work-tree"])
    if inside != "true":
        print("Not a git worktree", file=sys.stderr)
        return 2
    project = project_name(args)
    mapped = mapped_project(project)
    path = project_path(args)
    print(f"project: {project}")
    print(f"path: {display_path(path)}")
    print("tag_policy: <project>-v<semver>")
    print(f"next_tag_example: {tag_for(project, '1.0.0')}")
    print(f"branch: {text_or_none(['git', 'branch', '--show-current']) or 'detached'}")
    print(f"head: {text_or_none(['git', 'rev-parse', '--short', 'HEAD']) or 'unknown'}")
    print(f"latest_project_tag: {latest_project_tag(project) or 'none'}")
    print(f"latest_repo_tag: {text_or_none(['git', 'describe', '--tags', '--abbrev=0']) or 'none'}")
    if mapped:
        print("release_enabled: " + str(bool(mapped.get("release", True))).lower())
        print("mapped_paths: " + ", ".join(mapped.get("paths", [])))
    sources = version_sources(path, mapped)
    print("version_sources: " + (", ".join(sources) if sources else "none"))
    print("gh: " + (shutil.which("gh") or "not found"))
    return 0


def notes(args: argparse.Namespace) -> int:
    project = project_name(args)
    mapped = mapped_project(project)
    path = project_path(args)
    base = args.from_ref or latest_project_tag(project)
    target = args.to_ref or "HEAD"
    rev_range = f"{base}..{target}" if base else target
    version = current_version(path, mapped)
    if not version:
        print("release version source must contain a valid semver version", file=sys.stderr)
        return 2
    if not args.verify:
        print("--verify is required so release notes include actual verification evidence", file=sys.stderr)
        return 2
    scope_paths = project_scope_paths(mapped, path)
    commits = collect_commits(rev_range, scope_paths)
    files = collect_changed_files(base, target, scope_paths)
    print(f"## 프로젝트\n\n- `{project}` ({', '.join(scope_paths)})\n")
    print("## 버전\n")
    print(f"- 현재 버전: `{version or 'unknown'}`")
    print(f"- 태그 정책: `{project}-v<semver>`")
    print(f"- 기준 ref/tag: `{base or 'none'}`\n")
    print("## 요약\n")
    if commits:
        for _, subject in commits[:3]:
            print(f"- {subject}")
    else:
        print("- 변경 commit 없음")
    print()
    print("## 변경 사항\n")
    if commits:
        print_commit_groups(commits)
    else:
        print("- 변경 commit 없음\n")
    print("## 변경 파일\n")
    if files:
        for item in files:
            print(f"- `{item}`")
    else:
        print("- 변경 파일 없음")
    print("\n## 검증\n")
    for item in args.verify:
        print(f"- `{item}`")
    print("\n## 호환성 / 마이그레이션\n")
    policy_changed = any(item.startswith((".codex/", ".github/", "AGENTS.md")) for item in files)
    print("- 데이터베이스/외부 API 마이그레이션: 없음")
    print(f"- 운영 정책 또는 설정 변경: {'있음' if policy_changed else '없음'}")
    print("\n## 롤백\n")
    print(f"- 기준 ref/tag: `{base or 'none'}`")
    print(f"- 문제가 있으면 `{target}`에 포함된 변경 commit을 revert하고 새 release를 생성하세요.")
    return 0


def merge_notes(args: argparse.Namespace) -> int:
    project = project_name(args)
    mapped = mapped_project(project)
    path = project_path(args)
    base = args.from_ref or latest_project_tag(project)
    target = args.to_ref or "HEAD"
    rev_range = f"{base}..{target}" if base else target
    version = current_version(path, mapped)
    version_label = version or "unknown"
    version_note = "valid semver" if version else "missing or invalid semver; release create still requires an explicit valid tag/version"
    if not args.verify:
        print("--verify is required so release notes include actual verification evidence", file=sys.stderr)
        return 2
    scope_paths = project_scope_paths(mapped, path)
    merges = collect_merge_commits(rev_range, scope_paths)
    files = collect_changed_files(base, target, scope_paths)
    print(f"## 프로젝트\n\n- `{project}` ({', '.join(scope_paths)})\n")
    print("## 릴리즈 판단\n")
    if merges:
        print("- 이전 릴리즈 이후 병합된 개발 건이 있어 릴리즈 검토를 권장합니다.")
        print("- 자동 릴리즈는 수행하지 않습니다. 사용자가 명시적으로 요청하면 release create 단계를 진행하세요.")
    else:
        print("- 기준 범위에서 병합 기록이 없어 즉시 릴리즈 필요성은 낮습니다.")
    print()
    print("## 버전\n")
    print(f"- 현재 버전: `{version_label}`")
    print(f"- 버전 상태: {version_note}")
    print(f"- 태그 정책: `{project}-v<semver>`")
    print(f"- 기준 ref/tag: `{base or 'none'}`")
    print(f"- 대상 ref: `{target}`\n")
    print("## 요약\n")
    if merges:
        for item in merges[:5]:
            print(f"- {item['subject']} (`{item['short']}`)")
    else:
        print("- 병합 commit 없음")
    print()
    print("## Merge 상세\n")
    if merges:
        for index, item in enumerate(merges, start=1):
            body, footer = split_body_footer(item["body"])
            print(f"### {index}. {item['subject']}\n")
            print(f"- Commit: `{item['short']}`")
            print("- Body:")
            if body:
                for line in body.splitlines():
                    print(f"  {line}" if line.strip() else "")
            else:
                print("  없음")
            print("- Footer:")
            if footer:
                for line in footer:
                    print(f"  - {line}")
            else:
                print("  - 없음")
            print()
    else:
        print("- 병합 commit 없음\n")
    print("## 변경 파일\n")
    if files:
        for item in files:
            print(f"- `{item}`")
    else:
        print("- 변경 파일 없음")
    print("\n## 검증\n")
    for item in args.verify:
        print(f"- `{item}`")
    print("\n## 호환성 / 마이그레이션\n")
    policy_changed = any(item.startswith((".codex/", ".github/", "AGENTS.md")) for item in files)
    print("- 데이터베이스/외부 API 마이그레이션: 확인 필요 시 별도 검증")
    print(f"- 운영 정책 또는 설정 변경: {'있음' if policy_changed else '없음'}")
    print("\n## 롤백\n")
    print(f"- 기준 ref/tag: `{base or 'none'}`")
    print(f"- 문제가 있으면 `{target}`에 포함된 merge 또는 관련 commit을 revert하고 새 release를 생성하세요.")
    return 0


def projects(args: argparse.Namespace) -> int:
    project_map = load_project_map()
    mapped = project_map.get("projects", [])
    if not mapped:
        print("projects: none")
        return 0
    for project in mapped:
        print(
            "{name}: paths={paths}, release={release}, versionSource={version_source}".format(
                name=project["name"],
                paths=",".join(project.get("paths", [])),
                release=str(bool(project.get("release", True))).lower(),
                version_source=project.get("versionSource") or "auto",
            )
        )
    return 0


def impacted(args: argparse.Namespace) -> int:
    files = changed_files(args.from_ref, args.to_ref)
    project_map = load_project_map()
    matches = [
        project for project in project_map.get("projects", [])
        if any(project_matches(project, changed_file) for changed_file in files)
    ]
    print("changed_files:")
    if files:
        for changed_file in files:
            print(f"- {changed_file}")
    else:
        print("- none")
    print("impacted_projects:")
    if matches:
        for project in matches:
            release = bool(project.get("release", True))
            print(f"- {project['name']} release={'yes' if release else 'no'} paths={','.join(project.get('paths', []))}")
    else:
        print("- none")
    releasable = [project["name"] for project in matches if project.get("release", True)]
    print("release_projects: " + (", ".join(releasable) if releasable else "none"))
    return 0


def create(args: argparse.Namespace) -> int:
    project = project_name(args)
    if args.version:
        args.tag = tag_for(project, args.version)
    if not args.tag:
        print("--tag or --version is required", file=sys.stderr)
        return 2
    validate_tag(project, args.tag)
    if not args.notes_file:
        print("--notes-file is required", file=sys.stderr)
        return 2
    if not Path(args.notes_file).exists():
        print(f"notes file not found: {args.notes_file}", file=sys.stderr)
        return 2
    cmd = ["gh", "release", "create", args.tag, "--notes-file", args.notes_file]
    cmd.extend(["--title", args.title or args.tag])
    if args.draft:
        cmd.append("--draft")
    if not args.execute:
        print("dry-run: " + " ".join(cmd))
        return 0
    if not shutil.which("gh"):
        print("gh not found", file=sys.stderr)
        return 127
    proc = run(cmd)
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    return proc.returncode


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Pogo project-scoped release helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    add_scope_args(s)
    s.set_defaults(fn=status)
    n = sub.add_parser("notes")
    add_scope_args(n)
    n.add_argument("--from", dest="from_ref")
    n.add_argument("--to", dest="to_ref")
    n.add_argument("--verify", action="append", help="verification evidence line to include in release notes")
    n.set_defaults(fn=notes)
    m = sub.add_parser("merge-notes", help="draft release notes from merge commit title/body/footer without creating a release")
    add_scope_args(m)
    m.add_argument("--from", dest="from_ref")
    m.add_argument("--to", dest="to_ref")
    m.add_argument("--verify", action="append", help="verification evidence line to include in release notes")
    m.set_defaults(fn=merge_notes)
    p = sub.add_parser("projects")
    p.set_defaults(fn=projects)
    i = sub.add_parser("impacted")
    i.add_argument("--from", dest="from_ref")
    i.add_argument("--to", dest="to_ref")
    i.set_defaults(fn=impacted)
    c = sub.add_parser("create")
    add_scope_args(c)
    c.add_argument("--tag")
    c.add_argument("--version", help="semver; converted to <project>-v<semver>")
    c.add_argument("--title")
    c.add_argument("--notes-file", required=True)
    c.add_argument("--draft", action="store_true")
    c.add_argument("--execute", action="store_true")
    c.set_defaults(fn=create)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
