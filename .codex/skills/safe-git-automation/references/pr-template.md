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

```text
feat(scope): 간단한 변경 요약

- 변경 목적
- 핵심 동작 변경
- 영향 범위

Refs: <issue/branch>
Validation: <필수검증명령+결과>
Scope: <project/path>
Rollback: <되돌림 방법>
```

- 제목(title): `type(scope): ...` 형태(Conventional Commits 권장)
- body: 요약, 이유, 범위, 검증 항목을 최소 2줄 이상 작성
- footer: `Refs`, `Validation`, `Scope`, `Rollback`을 최소 1개 이상

main 반영은 fast-forward 우선 정책을 유지하고, merge record는 보완 경로에서만 사용한다.

## GitHub Release

main fast-forward 후 release를 요청받은 경우 `.codex/script/pogo_release.py status`와 `notes`/`merge-notes`로 기준을 확인하고 GitHub Releases 페이지에 다음을 남긴다.

```md
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

- 이전 tag:
- 되돌릴 commit 또는 release tag:
```

## 차단 기준

다음 중 하나라도 해당하면 main 반영과 release를 중단한다.

- 필수 검증이 `FAILED`, `PARTIAL`, `NOT RUN`
- branch commit SHA와 검증된 SHA가 다름
- `git merge --ff-only`가 실패함
- migration 또는 rollback 검증이 끝나지 않음
- release note에 실제 검증 증거를 넣을 수 없음

## Release

`DELIVER` 요청 없이 main 반영이나 release를 수행하지 않는다.
보호 규칙과 required checks를 우회하지 않는다.
main 반영 결과와 release tag/URL을 원격에서 확인한 뒤 완료라고 보고한다.
