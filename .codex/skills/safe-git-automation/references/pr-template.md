# Pull Request Policy and Template

## 게시 전 조건

push 또는 PR은 `PUBLISH` 요청이 있을 때만 수행한다.

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

## Provider 도구

remote host와 설치된 도구를 확인한 후 사용한다.

- GitHub: `gh auth status` 후 `gh pr create`
- GitLab: `glab auth status` 후 `glab mr create`

인증 실패나 CLI 부재를 성공처럼 처리하지 않는다.
도구가 없으면 push까지만 완료하고 PR 생성은 `NOT RUN`으로 보고한다.

## PR 제목

저장소 규칙을 우선한다. 규칙이 없으면 핵심 commit과 같은 형식을 사용한다.
PR 제목에는 PR 번호를 강제하지 않는다. PR 번호는 provider가 PR 생성 후 부여하며, 최종 squash merge commit 끝에 남긴다.

```text
feat(user): add registration endpoint
```

## PR 본문 원칙

PR 본문은 리뷰어가 의도, 변경, 검증, rollback 기준을 빠르게 판단할 수 있을 만큼만 작성한다.
작은 변경(T0)은 기본 템플릿만 사용한다.
고위험 변경, API/데이터/보안/migration 영향, 긴 리뷰가 필요한 변경만 확장 템플릿을 추가한다.

## 기본 템플릿

```md
## Summary

- Why:
- What:
- Verify:
- Risk/Rollback:
```

작성 기준:

- `Why`: 왜 필요한지 한 줄로 쓴다. Issue나 Spec이 있으면 번호 또는 링크만 붙인다.
- `What`: 실제 변경된 동작이나 문서/설정 경로를 한 줄로 쓴다.
- `Verify`: 실행한 검증과 결과를 한 줄로 쓴다. 예: `git diff --check` - PASS
- `Risk/Rollback`: 남은 위험과 되돌릴 방법을 한 줄로 쓴다. 위험이 낮으면 `낮음 / revert PR`.

## 확장 템플릿

필요할 때만 기본 템플릿 아래에 추가한다.

```md
## Details

- Scope:
- Excluded:
- Acceptance:
- Migration:
- Review:
- Release:
```

확장 기준:

- T0 문서, 설정, 좁은 수정: 기본 템플릿만 사용한다.
- T1 기능, 버그, UX/API 변경: reviewer가 바로 판단하기 어렵다면 `Details`를 추가한다.
- T2 고위험, migration, 보안, 데이터, 호환성 변경: `Details`를 추가하고 rollback 기준을 구체화한다.
- 검증이 여러 개면 표를 사용할 수 있지만, 한두 개면 한 줄 목록을 우선한다.
- 외부 동작 변화가 없으면 Release 항목은 생략한다.

## GitHub Release

main merge 후 release를 요청받은 경우 `.codex/script/pogo_release.py status`와 `notes`로 기준을 확인하고 GitHub Releases 페이지에 다음을 남긴다.

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
- 되돌릴 commit 또는 PR:
```

## Draft 판단

다음 중 하나라도 해당하면 draft PR을 우선한다.

- 필수 검증이 `FAILED`, `PARTIAL`, `NOT RUN`
- Spec의 차단되는 `[OPEN]` 항목이 남음
- migration 또는 rollback 검증이 끝나지 않음
- 리뷰를 위한 중간 결과를 게시하는 목적

## Merge

PR 생성과 merge는 별도 권한이다.
`DELIVER` 요청 없이 merge하지 않는다.
보호 규칙, required checks, 승인 정책을 우회하지 않는다.
기본 merge 전략은 squash merge를 우선한다. 최종 squash merge commit 제목은 `<type>(<scope>): <summary> (#<pr-number>)` 형식을 사용한다.
일반 merge 또는 rebase merge가 필요한 경우 PR 번호 추적 방식이 달라질 수 있으므로 merge 전 사용자에게 확인한다.
merge 결과와 최종 commit을 원격에서 확인한 뒤 완료라고 보고한다.
