# No-PR Release Flow

## 게시 전 조건

push는 `PUBLISH` 요청이 있을 때만 수행한다. PR은 기본 생성하지 않는다.

확인 사항:

1. 현재 branch가 기본 또는 보호 branch가 아니다.
2. remote와 destination branch가 명확하다.
3. commit hash와 staged 상태를 확인했다.
4. 필수 검증 결과를 알고 있다.
5. 민감정보가 diff와 remote URL에 없다.

## Push

현재 branch를 명시적으로 게시한다.

```bash

git push --set-upstream <remote> <branch>
```

push 후 확인한다.

```bash
git status --porcelain=v2 --branch
git rev-parse HEAD
git rev-parse @{upstream}
git rev-list --left-right --count @{upstream}...HEAD
```

local과 upstream이 일치하지 않으면 push 완료라고 보고하지 않는다.

## Main Fast-Forward

PR 없이 main에 반영하려면 작업 branch commit SHA와 검증된 SHA가 같아야 한다.
검증 통과 전에는 main을 갱신하지 않는다.

```bash
git push --set-upstream <remote> <branch>
gh run list --branch <branch> --workflow "Pogo Policy" --limit 1
git switch main
git merge --ff-only <branch>
git push <remote> main
```

`--ff-only`가 실패하면 기본 merge를 강제하지 않는다. 저장소 정책상 merge commit이 필요한 경우 아래 Merge 기록 템플릿을 사용해 merge record를 남긴 뒤 감사 가능하게 반영한다.

## Merge 기록 템플릿 (제목/Body/Footer 강제)

기본 merge 경로가 불가능할 때는 `git merge --no-ff` 등으로 merge commit을 만들되, 메시지는 다음 형식을 반드시 사용한다.
merge record는 단순 병합 흔적이 아니라 release note와 장애 분석의 원천이다.
따라서 미래의 유지보수자가 "왜 이 변경이 들어왔고, 무엇이 추가/변경/수정/삭제되었고, 어떤 버전/검증/롤백 기준을 따라야 하는지"를 읽을 수 있어야 한다.

```text
feat(scope): 간단한 변경 요약

- 변경 목적: 왜 지금 merge해야 하는가
- 변경 항목:
  - 추가:
  - 변경:
  - 수정:
  - 삭제:
- 영향 범위: 사용자/운영/API/데이터/정책 영향
- 버전 영향: before=<version-or-tag>, after=<version-or-tag>, bump=<major|minor|patch|prerelease|none>, reason=<이유>
- 호환성/마이그레이션: breaking change, 설정, DB, API, 배포 영향
- 인수인계: 담당 역할, 모니터링 지표, 남은 TODO

Refs: <issue/branch>
Validation: <필수검증명령+결과>
Scope: <project/path>
Before: <version/tag/ref>
After: <version/tag/ref>
Why-now: <릴리즈 또는 병합 필요성>
Rollback: <구체적 revert 명령 또는 새 릴리즈 대체 절차>
Handoff: owner=<name-or-role>, monitor=<metric-or-log>, follow-up=<todo-or-none>
```

- 제목(title): `type(scope): ...` 형태(Conventional Commits 권장)
- body: 요약, 이유, 추가/변경/수정/삭제, 버전 영향, 호환성, 인수인계를 작성
- footer: `Refs`, `Validation`, `Scope`, `Before`, `After`, `Why-now`, `Rollback`, `Handoff`를 작성

main 반영은 fast-forward 우선 정책을 유지하고, merge record는 보완 경로에서만 사용한다.

## GitHub Release

main fast-forward 후 release를 요청받은 경우 `.codex/script/pogo_release.py status`와 `notes`/`merge-notes`로 기준을 확인하고 GitHub Releases 페이지에 다음을 남긴다.
release note는 "배포 공지"가 아니라 버전 변경의 감사 기록이다.
작성자는 독자가 이전 맥락을 몰라도 왜 버전이 올라갔는지, 무엇이 바뀌었는지, 잘못되었을 때 어디를 되돌릴지 이해할 수 있게 써야 한다.

```md
## 프로젝트

- `<project>` (`<path>`)

## 릴리즈 필요성

- 왜 지금 릴리즈해야 하는가
- 릴리즈하지 않으면 남는 위험 또는 유지보수 비용

## 버전

- 이전 버전/tag:
- 현재 버전:
- 버전업 유형: major / minor / patch / prerelease / none
- 버전업 이유:

## 요약

- 핵심 변경

## 변경 항목

- 추가:
- 변경:
- 수정:
- 삭제:

## 변경 파일

- 주요 파일과 역할

## 검증

- `<command>`: PASS / FAILED / PARTIAL / NOT RUN

## 호환성 / 마이그레이션

- breaking change 여부
- 설정 파일 변경 여부

## 롤백

- 이전 tag:
- 되돌릴 commit 또는 release tag:
- 구체적 revert 또는 재릴리즈 절차:
- 롤백 후 확인할 지표:

## 인수인계

- 담당 역할:
- 모니터링 대상:
- 후속 작업:
```

## 차단 기준

다음 중 하나라도 해당하면 main 반영과 release를 중단한다.

- 필수 검증이 `FAILED`, `PARTIAL`, `NOT RUN`
- branch commit SHA와 검증된 SHA가 다름
- `git merge --ff-only`가 실패함
- migration 또는 rollback 검증이 끝나지 않음
- release note에 실제 검증 증거를 넣을 수 없음
- release note에 릴리즈 필요성, 버전 전후, 버전업 이유, 추가/변경/수정/삭제, 롤백, 인수인계가 없음

## Release

`DELIVER` 요청 없이 main 반영이나 release를 수행하지 않는다.
보호 규칙과 required checks를 우회하지 않는다.
main 반영 결과와 release tag/URL을 원격에서 확인한 뒤 완료라고 보고한다.
