# Commit Policy

## 우선순위

1. 저장소의 `CONTRIBUTING.md`, `AGENTS.md`, commit lint 규칙
2. 같은 저장소의 최근 commit 관례
3. 이 문서의 기본 규칙

## Commit 단위

한 commit에는 하나의 논리적 목적만 둔다.
작업이 실제 파일 변경으로 끝났고 검증 가능한 상태라면 commit을 남기는 것을 기본값으로 한다.
commit은 과거의 작성자, 미래의 유지보수자, 인수인계자가 변경 흐름을 따라가도록 남기는 감사 기록이다.
따라서 "수정했다"가 아니라 "왜 지금 바꿨고, 무엇을 추가/변경/수정/삭제했으며, 검증과 되돌림 기준이 무엇인지"를 추적할 수 있어야 한다.

다음 중 하나라도 해당하면 commit하지 않는다.

- 사용자 또는 다른 작업자의 기존 변경과 현재 작업 변경이 분리되지 않음
- 필수 검증이 실패했거나, 실패 원인을 숨긴 채 완료처럼 보일 위험이 있음
- staged diff에 민감정보, 운영 데이터, 의도하지 않은 생성물이 의심됨
- 사용자 승인 범위 밖의 변경이 포함됨
- 변경이 없거나 commit 목적이 설명되지 않음

commit하지 않는 경우 최종 보고에 사유와 남은 조치를 명확히 남긴다.

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
제목은 1줄 요약이지만, 제목만으로 모든 맥락을 대신하지 않는다.
정책, release, migration, 운영 영향, 보안, 데이터, 사용자 흐름을 바꾸는 commit은 body와 footer를 생략하지 않는다.

나쁜 예:

```text
update files
fix stuff
changes
```

본문에는 필요할 때 다음을 적는다.

- 무엇보다 왜 바꿨는지
- 호환성 또는 migration 영향
- Issue 또는 Spec 식별자
- 의도적으로 제외한 내용

다음 항목 중 해당되는 내용은 body에 구체적으로 적는다.
해당 없음도 중요한 판단이면 `없음`이라고 쓴다.

```text
변경 목적:
- 왜 지금 이 변경이 필요한가
- 문제를 방치하면 어떤 운영/유지보수/사용자 위험이 있는가

변경 범위:
- 추가: 새로 만든 기능, 정책, 파일, 섹션
- 변경: 기존 동작, 정책, 형식, 흐름의 의미 변경
- 수정: 결함, 누락, 오해 소지가 있던 부분의 보정
- 삭제: 제거한 기능, 문서, 설정, 의존성

버전 영향:
- before: <이전 버전 또는 해당 없음>
- after: <새 버전 또는 해당 없음>
- version bump type: major | minor | patch | prerelease | none
- version bump reason: 왜 그 수준의 버전 변경이 필요한가

검증:
- <command>: PASS | FAILED | PARTIAL | NOT RUN
- 실패 또는 미실행 항목은 이유와 후속 조치

호환성/마이그레이션:
- breaking change 여부
- 설정, DB, API, 배포, 운영 절차 변경 여부

롤백:
- 되돌릴 commit/tag
- revert 또는 재릴리즈 절차
- 되돌릴 때 확인할 데이터/설정/운영 지표

인수인계:
- 다음 담당자가 확인해야 할 파일, 정책, 모니터링, TODO
```

footer에는 추적 가능한 키-값을 남긴다. 최소 1개 이상이 아니라, 변경 성격에 맞는 항목을 가능한 한 구체적으로 남긴다.

```text
Refs: <issue/spec/branch/release-request>
Validation: <command>=<PASS|FAILED|PARTIAL|NOT RUN>
Scope: <project/path>
Before: <version/tag/ref>
After: <version/tag/ref>
Rollback: <revert command 또는 release rollback 기준>
Handoff: owner=<name-or-role>, monitor=<metric-or-log>, follow-up=<todo-or-none>
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
