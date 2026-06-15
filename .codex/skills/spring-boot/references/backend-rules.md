# Spring Boot Backend Rules

## Must

- Controller는 HTTP shape, validation, principal, response mapping만 담당합니다.
- Service는 transaction, business rule, state transition을 담당합니다.
- Repository는 persistence access만 담당하고 business branching을 숨기지 않습니다.
- REST API는 request/response DTO와 stable error shape를 사용합니다.
- 인증 기능은 identity 확인과 ownership/role authorization을 분리합니다.

## Never

- password, token, secret을 log, response, exception message에 노출하지 않습니다.
- controller transaction으로 lazy loading 문제를 덮지 않습니다.
- request body의 userId를 authenticated owner 대신 신뢰하지 않습니다.

## Blocker

권한 없는 mutation, service transaction 누락, entity response는 완료 차단입니다.
