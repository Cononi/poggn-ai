# JPA Persistence Rules

## Must

- DTO mapping이 접근하는 lazy association을 모두 식별합니다.
- list/detail 응답은 EntityGraph, fetch join, projection, DTO query로 fetch plan을 고정합니다.
- aggregate mutation은 하나의 service transaction 안에서 처리합니다.
- stock, balance, ownership, status invariant는 write transaction 안에서 검증합니다.
- lost update가 의미 있으면 optimistic lock 또는 명시적 lock을 검토합니다.

## Never

- OSIV로 lazy loading 문제나 N+1을 숨기지 않습니다.
- entity를 REST response로 직접 반환하지 않습니다.
- aggregate 경계를 넘는 cascade remove를 기본값처럼 쓰지 않습니다.
- owner scope 없는 update/delete query를 만들지 않습니다.

## Blocker

N+1 위험, transaction 누락, entity response, owner scope 누락은 완료 차단입니다.
