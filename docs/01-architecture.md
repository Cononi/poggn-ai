# 구조 원리

이 템플릿의 작업 단위는 계층으로 나뉩니다.

```text
사용자 요청
  -> agent 추천
  -> skill 자동 선정
  -> TASK 생성
  -> lane 생성
  -> worktree 병렬 작업
  -> commit 연결
  -> quality/refactor/security gate
```

agent는 작업자의 역할입니다.
backend, frontend, database, integration처럼 책임을 나눕니다.
devops, docs, performance, test, qa, security, refactor도 분리합니다.

skill은 agent가 작업할 때 읽는 전문 절차입니다.
spring-boot, jpa, openapi-swagger, frontend-component-architecture처럼
작업에 필요한 절차만 선택됩니다.

lane은 실제 병렬 실행 단위입니다.
같은 backend agent라도 order, payment, member는 별도 lane으로 실행됩니다.

TASK는 추적 단위입니다.
TASK는 하나 이상의 lane과 하나 이상의 commit을 가질 수 있습니다.
TASK가 완료되려면 모든 lane이 done 또는 merged 상태여야 합니다.
또한 commit이 연결되어야 합니다.

TASKS.md는 사람이 보는 요약본입니다.
원본 상태는 state.json, tasks.jsonl, lanes.jsonl, commits.jsonl, events.jsonl입니다.
