# Recovery and Destructive Operation Policy

## 원칙

복구 작업의 첫 목표는 사용자 변경 보존이다.
상태를 이해하기 전에 삭제, reset, clean, force 명령을 실행하지 않는다.

## 충돌 발생 시

먼저 상태와 충돌 파일을 확인한다.

```bash
git status --porcelain=v2 --branch
git diff --name-only --diff-filter=U
```

명확한 기계적 충돌만 해결한다.
비즈니스 규칙, 데이터 의미, API 계약 판단이 필요한 충돌은 추측하지 않는다.

자동화가 시작한 merge 또는 rebase를 안전하게 해결할 수 없으면 원래 상태로 되돌린다.

```bash
git merge --abort
git rebase --abort
```

해당 작업이 실제로 진행 중일 때만 알맞은 abort 명령을 사용한다.

## 위험 명령 승인 조건

다음 작업은 명시적이고 구체적인 사용자 승인 없이는 실행하지 않는다.

- uncommitted 변경 삭제
- untracked 또는 ignored 파일 삭제
- branch 강제 삭제
- remote history 강제 갱신
- published commit rewrite
- 강제 worktree 제거

승인 전 다음을 알린다.

1. 정확한 명령
2. 영향 받는 branch, path, commit
3. 되돌릴 수 없는 데이터
4. 더 안전한 대안

## Clean

`git clean`은 untracked 파일을 삭제한다.
필요한 경우 먼저 dry-run만 수행한다.

```bash
git clean -nd
git clean -ndx
```

출력을 확인해도 실제 삭제는 별도 승인 없이는 수행하지 않는다.

## Reset 및 Restore

전체 working tree 또는 index를 덮는 명령을 자동 실행하지 않는다.
특정 파일을 복구해야 하면 해당 파일과 복구 기준 commit을 명시한다.
사용자 변경인지 현재 작업 변경인지 구분되지 않으면 중단한다.

## Force Push

일반 `git push --force`는 사용하지 않는다.
사용자가 history rewrite를 명시적으로 승인하더라도 다음을 확인한다.

- 대상이 보호 branch가 아닌가
- 다른 사용자의 commit을 덮지 않는가
- remote를 fetch한 뒤 기대한 tip인가
- release note와 협업자에게 영향이 기록되었는가

자동화의 기본 동작은 history를 보존하는 새 commit이다.

## Worktree 오류

worktree 경로를 파일 시스템에서 직접 삭제하지 않는다.
먼저 다음을 확인한다.

```bash
git worktree list --porcelain
git -C <path> status --porcelain=v2 --branch
```

정상 제거는 `git worktree remove <path>`를 사용한다.
누락 경로 정리는 먼저 다음 dry-run을 사용한다.

```bash
git worktree prune --dry-run
```

## 복구 보고

```md
## Recovery Status

- Operation:
- Original state:
- Current state:
- Preserved commits or paths:
- Unresolved conflicts:
- Commands executed:
- Destructive commands: NOT RUN | APPROVED AND RUN
```
