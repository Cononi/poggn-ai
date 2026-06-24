# Worktree Policy

## 결론

worktree는 모든 Git 작업의 필수 조건이 아니다.
단일 작업에는 일반 branch를 사용하고 병렬 작업에는 worktree를 사용한다.

## 선택 표

| 상황 | 선택 | 이유 |
|---|---|---|
| 한 에이전트, 한 작업, clean tree | 일반 branch | 가장 단순하다. |
| 여러 에이전트가 같은 저장소에서 작업 | worktree 필수 | branch 전환과 파일 충돌을 줄인다. |
| 현재 tree에 다른 작업의 미커밋 변경 존재 | worktree 필수 | 기존 변경을 건드리지 않는다. |
| 기능 개발 중 별도 hotfix | worktree 권장 | 두 branch를 동시에 유지한다. |
| 두 버전 비교 또는 장시간 테스트 | worktree 권장 | 작업공간을 분리한다. |
| submodule 중심 superproject | 검증 전 사용 금지 | 다중 checkout 지원 제약을 확인해야 한다. |

## 중요한 한계

worktree는 별도 clone이 아니다.

- object database와 일반 refs를 같은 저장소와 공유한다.
- 각 worktree는 별도의 `HEAD`, index, working files를 가진다.
- 저장소 config는 기본적으로 공유된다.
- 같은 branch를 여러 worktree에서 동시에 checkout할 수 없다.
- process, port, database, cache, environment variable은 자동 격리되지 않는다.

따라서 병렬 테스트는 포트, 임시 디렉터리, DB schema도 별도로 지정해야 한다.

## 기준 branch 결정

기본 branch를 추측하지 않는다.

```bash
git remote
git symbolic-ref --quiet --short refs/remotes/<remote>/HEAD
git branch --show-current
git log -1 --oneline
```

remote 기준으로 시작해야 하면 먼저 fetch 성공 여부를 확인한다.
fetch가 실패하면 오래된 local ref를 최신이라고 표현하지 않는다.

## 경로 규칙

linked worktree는 저장소 내부가 아닌 sibling 경로에 만든다.
branch의 `/`는 worktree 디렉터리명에 사용하지 않는다.

```text
../.worktrees/<repository>/<tracker-id>-<slug>
```

예시:

```text
../.worktrees/payment-service/PAY-421-refund-idempotency
```

## 생성 절차

먼저 기존 worktree와 branch 사용 여부를 확인한다.

```bash
git worktree list --porcelain
git branch --list <branch>
git branch --remotes --list "*/<branch>"
```

새 branch와 worktree를 함께 만든다.

```bash
mkdir -p ../.worktrees/<repository>
git worktree add -b <branch> <path> <base>
```

생성 후 다음을 확인한다.

```bash
git -C <path> status --porcelain=v2 --branch
git worktree list --porcelain
```

이미 존재하는 branch를 사용할 때는 다른 worktree에서 사용 중인지 먼저 확인한다.
`--force`로 Git의 중복 checkout 보호를 우회하지 않는다.

## 에이전트 소유권

병렬 작업마다 다음 정보를 기록한다.

```text
Task:
Agent:
Branch:
Worktree:
Base:
Created:
```

같은 branch 또는 worktree를 두 에이전트에게 동시에 할당하지 않는다.
공유 파일 변경이 예상되면 작업을 분리하거나 순서를 정한다.

## 정리 절차

정리 전 상태를 확인한다.

```bash
git -C <path> status --porcelain=v2 --branch
git -C <path> log -1 --oneline
git worktree list --porcelain
```

clean 상태이며 보존할 commit이 안전한 위치에 있을 때만 제거한다.

```bash
git worktree remove <path>
git worktree prune --dry-run
```

`git worktree prune`은 dry-run 결과를 확인한 뒤 필요한 경우에만 실행한다.
worktree 제거는 branch 삭제가 아니다. branch 삭제는 별도 승인 대상으로 둔다.
