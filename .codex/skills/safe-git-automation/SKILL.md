---
name: safe-git-automation
description: Git 변경을 안전하게 분기·검증·커밋·푸시·merge·release로 연결한다. 병렬 작업과 worktree 판단이 필요할 때 사용한다.
metadata:
  version: "1.0"
---

# Safe Git Automation

## 목적

사용자 변경을 잃거나 섞지 않고 Git 작업을 재현 가능하게 수행한다.
로컬 커밋, 원격 게시, main 반영, release를 서로 다른 권한 단계로 취급한다.
`subagent.auto=true`이면 실행 가능한 Git 작업은 `pogo-git-agent`에 우선 위임해 메인 컨텍스트 토큰 사용을 줄인다.

## 사용 시점

다음 작업을 요청받으면 이 스킬을 사용한다.

- 브랜치 생성, 커밋 정리, push, main 반영, release 생성
- 여러 에이전트 또는 여러 기능의 병렬 작업
- worktree 생성, 점검, 정리
- 충돌 복구, 브랜치 동기화, 릴리스 준비

코드 구현 규칙은 저장소의 `AGENTS.md`, `CONTRIBUTING.md`, Spec을 우선한다.

## 파일 로딩 원칙

이 파일만 먼저 읽고 필요한 문서만 추가로 읽는다.

- worktree를 판단하거나 사용할 때: `references/worktree-policy.md`
- staging 또는 commit을 만들 때: `references/commit-policy.md`
- push, main 반영, release를 준비할 때: `references/pr-template.md`
- 충돌이나 위험 명령을 다룰 때: `references/recovery-policy.md`

## 권한 단계

### LOCAL

브랜치, 변경, 테스트, 커밋까지만 수행한다.
사용자가 원격 작업을 요청하지 않았다면 기본값은 `LOCAL`이다.

### PUBLISH

사용자가 push를 요청했을 때만 수행한다.
현재 작업 브랜치만 게시하며 대상 remote와 branch를 확인한다.

### DELIVER

merge, tag, release, 배포 트리거는 사용자가 명시적으로 요청했을 때만 수행한다.
필수 검증이나 보호 규칙을 우회하지 않는다.

## Git Subagent 라우팅

`subagent.auto=true`이면 메인 에이전트는 git 상태 확인, staging 검토, commit, push, merge, release 점검을 `pogo-git-agent`에 우선 위임한다. 메인 에이전트는 사용자 승인 범위, 보호 규칙 우회 여부, 실패/차단 판단, 최종 보고만 책임진다.

Hook 강제는 `commit/push/merge`에만 적용된다. release 점검은 정책상 `pogo-git-agent` 우선 위임 대상이며, 수동 위임 결과와 증빙 요약으로 보완한다.

예외는 단순히 한 줄 명령 출력을 확인하는 상태 조회, `$pogo-settings` shortcut 처리, 또는 Subagent를 사용할 수 없는 환경이다. 예외를 쓰면 이유를 보고한다.

## 핵심 안전 규칙

- 기존의 미커밋 변경을 수정, 삭제, stage, commit하지 않는다.
- 관련 없는 변경을 현재 작업에 섞지 않는다.
- 기본 브랜치에서 직접 기능 작업이나 커밋을 만들지 않는다.
- 자동으로 `git stash`를 만들거나 적용하지 않는다.
- 자동으로 전역 Git 설정을 변경하지 않는다.
- hook 실패를 `--no-verify`로 우회하지 않는다.
- 실행하지 않은 테스트를 통과했다고 보고하지 않는다.
- 성공하지 않은 push, merge, release를 완료라고 보고하지 않는다.
- 토큰, 비밀번호, 개인키로 의심되는 값을 출력하거나 커밋하지 않는다.

## 사전 점검

Git 변경 전에 다음 상태를 직접 확인한다.

```bash
git rev-parse --show-toplevel
git --version
git status --porcelain=v2 --branch
git worktree list --porcelain
git remote
git config --get user.name
git config --get user.email
```

추가로 확인한다.

1. 저장소 지침과 최근 commit 형식
2. 현재 branch와 upstream
3. staged, unstaged, untracked 변경
4. 기존 worktree와 사용 중인 branch
5. 기본 branch와 작업 기준 commit
6. 테스트, lint, build 명령

기본 branch 이름을 `main` 또는 `master`라고 추측하지 않는다.
remote URL에 자격 증명이 있으면 보고서에 복사하지 않는다.

## 작업공간 선택

### 일반 브랜치가 기본인 경우

- 한 에이전트가 한 작업만 수행한다.
- 현재 작업공간이 깨끗하다.
- 다른 branch를 동시에 열 필요가 없다.

```bash
git switch -c <branch> <base>
```

### worktree가 필요한 경우

- 같은 저장소에서 여러 에이전트가 동시에 작업한다.
- 현재 작업공간에 다른 작업의 미커밋 변경이 있다.
- 기능 작업 중 별도의 hotfix 또는 비교 검증이 필요하다.
- 사용자가 독립 작업공간을 명시적으로 요청했다.

병렬 에이전트에서는 `작업 1개 = branch 1개 = worktree 1개`를 적용한다.
worktree는 Git 작업공간 분리이며 프로세스, 포트, DB, secret을 격리하지 않는다.

상세 판단과 명령은 `references/worktree-policy.md`를 따른다.

## 언어와 Git 식별자

`pogo-settings`의 `lang`은 사람이 읽는 설명문에 적용한다.
branch, tag, version, commit type/scope, remote 이름은 자동으로 한글화하지 않는다.
commit body와 release note는 `lang=ko`일 때 한국어로 작성할 수 있다.

## Branch 규칙

저장소의 기존 규칙을 우선한다. 규칙이 없으면 다음 형식을 사용한다.

```text
<type>/<tracker-id>-<short-kebab-title>
```

예시:

```text
feat/34-user-registration
fix/PAY-421-refund-idempotency
chore/118-upgrade-gradle
```

한 branch에는 한 목적만 둔다. 다른 에이전트가 사용하는 branch를 재사용하지 않는다.

## 변경 및 검증

1. 작업 범위와 무관한 파일을 건드리지 않는다.
2. 전체 diff와 untracked 파일을 확인한다.
3. 저장소가 요구하는 테스트, lint, build를 실행한다.
4. 결과를 `PASS`, `FAILED`, `PARTIAL`, `NOT RUN` 중 하나로 기록한다.
5. 검증 실패를 숨긴 채 commit, push, merge, release를 완료 처리하지 않는다.

## Staging 및 Commit

`git add -A`를 기본값으로 사용하지 않는다. 파일 또는 hunk 단위로 의도한 변경만 stage한다.

```bash
git diff -- <path>
git add -- <path>
git diff --cached --check
git diff --cached --stat
git diff --cached
```

commit 전 staged diff가 작업 목적과 정확히 일치하는지 확인한다.
상세 규칙은 `references/commit-policy.md`를 따른다.

## Push 및 Main 반영

`PUBLISH` 권한이 있을 때만 현재 branch를 명시적으로 push한다.

```bash
git push --set-upstream <remote> <branch>
```

push 후 local `HEAD`, upstream, ahead/behind 상태를 확인한다.
PR은 기본 생성하지 않는다. 작업 branch의 같은 commit SHA에서 필수 검증이 PASS인 경우에만 `main`을 fast-forward로 반영한다.
상세 형식은 `references/pr-template.md`의 no-PR release flow를 따른다.

## 금지되는 기본 동작

다음 명령이나 동등한 동작은 자동 실행하지 않는다.

```text
git reset --hard
git clean -fd 또는 -fdx
git restore --source ... --worktree --staged :/
git branch -D
git worktree remove --force
git push --force
git commit --no-verify
git push --no-verify
```

공개된 branch의 amend, rebase, history rewrite도 기본적으로 금지한다.
예외가 필요하면 사용자에게 정확한 대상과 손실 가능성을 알리고 명시적 승인을 받는다.

## 충돌 처리

merge 또는 rebase 충돌이 발생하면 비즈니스 의도를 추측해 해결하지 않는다.
명확히 해결할 수 없는 경우 작업을 시작 전 상태로 되돌리고 충돌 파일과 원인을 보고한다.
상세 절차는 `references/recovery-policy.md`를 따른다.

## Release 관리

main merge 후 사용자가 release를 요청했거나 `merge`/`push` 자동화 범위에 release까지 포함한다고 명시한 경우에만 수행한다.
release는 GitHub Releases 페이지에 추적 가능한 기록으로 남긴다.

버전 관리는 프로젝트별 버전을 기본 정책으로 한다. 단일 프로젝트도 같은 정책을 사용한다. tag는 `<project>-v<semver>` 형식을 쓰며, 예시는 `web-v1.2.0`, `api-v2.0.3`, `app-v0.4.1`이다. Git tag 자체는 repo commit을 가리키지만 최신 tag, version source, release note, rollback 기준은 project 단위로 판단한다.

다중 프로젝트 repo는 `.codex/project-map.json`으로 release 단위를 정의한다. 각 project는 `name`, `paths`, `versionSource`, `release`를 가진다. merge 후 `.codex/script/pogo_release.py impacted --from <base> --to <target>`로 변경 파일이 어느 project에 속하는지 확인한다. 여러 release project가 바뀌면 project별 tag와 GitHub Release를 각각 만든다. `release=false` project만 바뀌었거나 project 판별이 안 되면 release를 만들지 않고 사유를 보고한다.

프로젝트별 version source는 project map의 `versionSource`를 우선하고, 없으면 해당 project path 안에서 확인한다. 지원 기준은 `package.json`, `VERSION`, `version.json`, `build.gradle`, `build.gradle.kts`, `gradle.properties`, `pom.xml`이다.

권장 순서:

1. 검증된 branch commit이 main에 fast-forward로 반영되었는지 원격에서 확인한다.
2. release 대상 project 이름과 path를 확정한다.
3. main의 최신 commit hash, project 최신 tag, project version source를 확인한다.
4. 필요한 경우 project version bump commit 또는 annotated tag를 만든다.
5. `.codex/script/pogo_release.py status --project <project> --path <path>`와 `notes`로 project 기준 release note 초안을 확인한다.
6. 사용자가 실행을 승인한 경우 `.codex/script/pogo_release.py create --project <project> --version <semver> --notes-file <file> --execute`로 GitHub Release를 생성한다.
7. release URL 또는 tag 결과를 확인한다.
8. worktree 정리는 release와 remote 보존 확인 후 수행한다.

Release note에는 다음 항목을 포함한다.

```md
## 프로젝트

- `<project>` (`<path>`)

## 요약

- 핵심 변경

## 변경 사항

- 추가:
- 변경:
- 제거:
- 수정:

## 검증

- `<command>`: PASS / FAILED / PARTIAL / NOT RUN

## 호환성 / 마이그레이션

- breaking change 여부
- 설정 파일 변경 여부

## 롤백

- 이전 project tag:
- 되돌릴 commit 또는 release tag:
```

release 생성이 실패하거나 GitHub 인증/도구가 없으면 완료로 보고하지 않고 `FAILED` 또는 `NOT RUN`으로 기록한다. 기본 helper는 dry-run이며 원격 생성에는 `--execute`가 필요하다.

## worktree 정리

branch push 직후 worktree를 자동 삭제하지 않는다. 추가 검증이나 release 수정에 다시 사용할 수 있게 유지한다.
다음 조건을 모두 만족할 때만 정리한다.

1. `.codex/script/pogo_worktree_cleanup.py status <path>`로 worktree가 clean 상태임을 확인했다.
2. 필요한 commit이 안전한 branch 또는 remote에 존재한다.
3. branch가 merge되었거나 사용자가 정리를 요청했다.
4. 제거 대상 경로와 branch를 다시 확인했다.
5. 제거 실행은 `.codex/script/pogo_worktree_cleanup.py remove <path> --execute`로 수행한다.

branch 삭제는 별도 작업이며 worktree 제거와 함께 자동 수행하지 않는다.

## Evidence-Driven SDD 연결

관련 Spec이 있으면 다음을 연결한다.

- branch: tracker ID 사용
- commit: 실제 변경 단위 기록
- verification: AC 또는 INV ID와 실행 결과
- release note: 사용자 또는 운영자에게 보이는 변경만 작성

## 완료 판정

요청한 권한 단계에 따라 완료를 판정한다.

- `LOCAL`: 검증 결과와 commit hash가 확인됨
- `PUBLISH`: remote branch 반영과 검증 대상 commit SHA가 확인됨
- `DELIVER`: main fast-forward 또는 release 결과가 원격에서 확인됨

일부 단계가 실패하거나 실행되지 않았다면 완료가 아니라 해당 상태를 그대로 보고한다.

## 최종 보고 형식

```md
## Git 결과

- Mode: LOCAL | PUBLISH | DELIVER
- Base: `<branch-or-commit>`
- Branch: `<branch>`
- Worktree: `미사용 | <path>`
- Commit: `<hash> | 없음`
- Push: `PASS | FAILED | NOT REQUESTED`
- Release: `<url> | 없음`

## 검증

- `<command>`: PASS | FAILED | PARTIAL | NOT RUN

## 남은 사항

- 충돌, 미실행 검증, 리뷰 대기, 잔여 위험
```
