# Skill 자동 선정

skill은 요청과 선택된 agent를 기준으로 자동 선정됩니다.
모든 skill을 항상 읽지 않습니다.

예를 들어 backend agent가 선택되고 요청에 JPA와 Swagger가 있으면
spring-boot, jpa, api-contract, openapi-swagger가 선택됩니다.

security agent에는 spring-boot나 jpa를 붙이지 않습니다.
security-gate만 선택됩니다.

확인 명령입니다.

```text
$codex-skills recommend --text "spring boot order api swagger" --agents backend,qa
```

사용자가 특정 skill을 빼라고 하면 그 지시를 우선합니다.
예를 들어 JPA 대신 MyBatis를 쓰라고 하면 jpa skill은 사용하지 않습니다.
