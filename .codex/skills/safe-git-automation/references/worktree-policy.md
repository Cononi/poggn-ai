# Worktree Policy

## 결론

worktree는 모든 작업의 기본값이 아니다.
간단한 설명, read-only 확인, 단일 파일 소규모 수정은 현재 workspace가 clean하면 worktree 없이 처리한다.
여러 파일/프로젝트가 섞이거나 release 준비, 병렬 작업, 기존 미커밋 변경과 충돌 위험이 있으면 worktree를 사용한다.
Single Agent와 Multi Agent 모두 동일 판단 기준을 적용한다.

## 선택 표

| 상황 | 선택 | 이유 |
|---|---|---|
| 설명/질문 답변 | worktree 불필요 | 파일 변경이나 branch 전환이 없다. |
| 단순 read-only 확인 | worktree 불필요 | 상태 조회만 수행한다. |
| 단일 파일 소규모 수정, clean workspace | worktree 불필요 | worktree 생성 비용이 더 크다. |
| 여러 파일 또는 여러 project path 수정 | worktree 권장 | main 작업공간과 project 변경을 분리한다. |
| multi-project repo의 release 준비 | worktree 권장 | project별 version, tag, release 판단을 분리한다. |
| 여러 에이전트가 같은 저장소에서 작업 | worktree 필수 | branch 전환과 파일 충돌을 줄인다. |
| 현재 tree에 다른 작업의 미커밋 변경 존재 | worktree 필수 | 기존 변경을 건드리지 않는다. |
| 현재 tree에 이번 대상 미커밋 변경만 존재 | 일반 branch 예외 | 변경 이동 과정에서 누락/혼입될 위험을 피한다. |
| 기능 작업 중 별도 hotfix | worktree 권장 | 두 branch를 동시에 유지한다. |
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

deterministic script(고정명령)로 위 절차를 기록하고, LLM은 결과 요약만 수행한다.

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

## 통합 절차

worktree의 결과는 최종적으로 하나의 통합 branch 또는 `main`으로 모은다.

1. 각 worktree에서 작업 범위별 commit을 만든다.
2. 검증이 끝난 commit만 통합 branch 또는 `main`에 fast-forward/merge한다.
3. 여러 worktree 결과가 있으면 통합 branch에서 순서대로 merge하고 충돌을 해결한다.
4. 원격 branch, `main`, tag, release가 필요한 위치에 보존되었는지 확인한다.
5. 보존 확인 전에는 worktree를 제거하지 않는다.

## Release 기준

worktree 생성은 release 조건이 아니다. worktree는 반복 수정과 검증을 위한 작업공간이며, release는 최종안 공표 단계다.

1. 같은 주제에서 수정이 반복되는 동안에는 중간 commit, branch push, worktree cleanup마다 release하지 않는다.
2. 최종안이 확정되고 검증된 commit이 `main`에 반영된 뒤에만 release를 검토한다.
3. release note는 worktree의 모든 중간 상태가 아니라 직전 release 이후 최종 `main`에 반영된 변경 전체를 기준으로 작성한다.
4. 중간 commit이 남아 있어도 release는 최종 project version/tag 하나로만 생성한다.
5. 최종안이 아직 불명확하면 release 대신 검증 결과와 남은 결정을 보고한다.

## 정리 절차

정리 전 상태를 확인한다.

```bash
.codex/script/pogo_worktree_cleanup.py status <path>
git worktree list --porcelain
```

clean 상태이며 보존할 commit이 안전한 branch 또는 remote에 있을 때만 제거한다.
제거는 파일 시스템 삭제가 아니라 Git 등록 해제를 먼저 수행한다.

```bash
.codex/script/pogo_worktree_cleanup.py remove <path> --execute
git worktree prune --dry-run
```

`git worktree prune`은 dry-run 결과를 확인한 뒤 필요한 경우에만 실행한다.
worktree 제거는 branch 삭제가 아니다. branch 삭제는 별도 승인 대상으로 둔다.
`.worktrees` 아래 파일을 직접 삭제하지 않는다.
