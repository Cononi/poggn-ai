# Commit Policy

## 우선순위

1. 저장소의 `CONTRIBUTING.md`, `AGENTS.md`, commit lint 규칙
2. 같은 저장소의 최근 commit 관례
3. 이 문서의 기본 규칙

## Commit 단위

한 commit에는 하나의 논리적 목적만 둔다.

좋은 분리 예시:

```text
feat(user): add registration endpoint
test(user): cover duplicate email conflict
docs(user): document registration contract
```

단, 구현과 테스트를 분리하면 중간 commit이 깨지는 저장소에서는 함께 commit한다.
commit 수를 늘리는 것보다 각 commit이 검증 가능한 상태인지가 중요하다.

## Staging

기존 사용자 변경과 현재 작업을 분리한다.

```bash
git status --porcelain=v2 --branch
git diff -- <path>
git add -- <path>
git diff --cached --check
git diff --cached --stat
git diff --cached
```

부분 staging이 필요하면 저장소와 도구가 지원하는 방식으로 hunk 단위 stage를 사용한다.
의도하지 않은 파일이 보이면 commit하지 말고 staging을 수정한다.

`git add -A`와 `git commit -a`는 범위가 명확하고 전체 변경이 현재 작업일 때만 사용한다.
자동화의 기본값으로 사용하지 않는다.

## Secret 및 민감정보

staged diff에서 다음을 확인한다.

- private key, access token, password
- 실제 운영 endpoint와 credential
- 개인정보나 운영 데이터 dump
- `.env`, keystore, 인증 파일

의심되는 값을 발견하면 commit을 중단한다.
값 자체를 보고서, 로그, release note에 복사하지 않는다.
저장소에 secret scanner가 있으면 해당 검사를 실행한다.

## 메시지 형식

저장소 규칙이 없으면 다음 형식을 사용한다.

```text
<type>(<scope>): <imperative summary>
```

기본 type:

```text
feat | fix | test | refactor | docs | chore | build | ci | perf | revert
```

제목은 실제 변경을 설명하고 모호한 표현을 피한다.
작업 commit 제목에는 PR 번호를 강제하지 않는다. PR은 기본 생성하지 않으며, 최종 추적은 project-scoped release tag와 GitHub Release에서 한다.

나쁜 예:

```text
update files
fix stuff
changes
```

작업 commit은 제목, 본문, 푸터를 모두 남긴다. 제목은 "무엇이 바뀌었는지"를 한 줄로 말하고,
본문은 "왜 바꿨는지", "무엇을 바꿨는지", "영향 범위"를 최소 2줄 이상으로 적는다.
푸터는 추적과 검증을 위해 아래 항목을 남긴다.

- `Validation`: 실행한 검증 명령과 결과. 실행 전이면 계획값을 쓰지 말고 commit 직전 실제 결과를 적는다.
- `Scope`: 변경된 project/path.
- `Rollback`: 문제가 생겼을 때 되돌릴 기준.
- `Refs`: Issue, Spec, branch 등 연결할 대상이 있을 때 추가한다.

예시:

```text
docs(pogo-policy): require detailed release and commit records

릴리즈 노트가 버전별 변경 내용을 commit 제목만으로 요약하지 않도록 상세 변경 섹션을 요구한다.
작업 commit에도 제목, 본문, 푸터를 남겨 검증과 롤백 기준을 추적할 수 있게 한다.

Validation: PYTHONDONTWRITEBYTECODE=1 python3 .codex/script/pogo_policy_ci.py PASS
Scope: .codex/skills/safe-git-automation
Rollback: revert this commit
```

main 반영은 검증된 작업 commit을 fast-forward하는 것을 기본으로 한다. squash merge commit을 새로 만들지 않는다.

## Commit 전 검증

최소한 다음을 수행한다.

1. staged diff 전체 검토
2. `git diff --cached --check`
3. 관련 테스트, lint, build
4. 민감정보와 생성 파일 확인
5. author identity와 현재 branch 확인

검증하지 못한 항목은 `NOT RUN`으로 기록한다.

## Commit 후 검증

```bash
git rev-parse HEAD
git show --stat --oneline --decorate HEAD
git status --porcelain=v2 --branch
```

commit hash가 확인되어야 commit 완료라고 보고한다.
commit 후 남은 변경이 현재 작업인지 기존 사용자 변경인지 구분한다.

## History 변경

다음은 자동화하지 않는다.

- 공개된 commit의 amend
- 공개된 branch의 rebase
- commit 삭제 또는 순서 변경
- force push

사용자가 명시적으로 요청한 경우에도 대상 branch, remote 상태, 손실 가능성을 먼저 확인한다.
강제 갱신이 승인되면 일반 `--force`보다 보호 범위가 있는 방법을 검토한다.
