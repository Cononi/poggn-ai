# Skill 설명

skill은 agent가 사용하는 반복 절차입니다.
agent와 달리 병렬 실행 단위가 아닙니다.

대표 skill입니다.

- spring-boot: Spring Boot 서버 구현 절차
- jpa: Entity, Repository, Transaction, Query 절차
- api-contract: request, response, error 계약 정리
- openapi-swagger: Swagger 또는 OpenAPI 문서화
- frontend-component-architecture: 재사용 컴포넌트 설계
- quality-gate: 대형 파일, 중복, 스파게티, 보안 흔적 검사
- refactor-clean-code: 동작 보존 리팩토링 절차
- security-gate: secret, token, 권한, 입력 검증 점검
- task-trace: TASK, lane, commit 추적

skill은 .codex/skills/{name}/SKILL.md에 있습니다.
setup_links.py는 .agents/skills를 .codex/skills로 연결합니다.
