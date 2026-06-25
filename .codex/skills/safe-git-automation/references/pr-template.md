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
검증 통과 전에는 main에 push하지 않는다.

```bash
git push --set-upstream <remote> <branch>
gh run list --branch <branch> --workflow "Pogo Policy" --limit 1
git switch main
git merge --ff-only <branch>
git push <remote> main
```

`--ff-only`가 실패하면 main을 갱신하고 재검증한다. 새 merge commit을 만들지 않는다.

## GitHub Release

main fast-forward 후 release를 요청받은 경우 `.codex/script/pogo_release.py status`와 `notes`로 기준을 확인하고 GitHub Releases 페이지에 다음을 남긴다.

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
