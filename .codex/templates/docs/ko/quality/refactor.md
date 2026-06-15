# 리팩토링 지침

리팩토링은 구현 직후 무조건 하는 작업이 아닙니다.
quality gate와 refactor 분석 결과가 필요하다고 판단할 때 수행합니다.

```text
$codex-refactor analyze --for-ai
$codex-quality gate --for-ai
```

리팩토링 원칙입니다.

- 동작을 보존합니다.
- 테스트가 실패 중이면 먼저 테스트 실패를 고칩니다.
- 공개 API와 DB 계약을 승인 없이 바꾸지 않습니다.
- 큰 파일을 책임 단위로 나눕니다.
- 중복 로직을 공통 함수로 이동합니다.
- 프론트는 primitive, feature component, hook, api client로 나눕니다.

리팩토링도 TASK와 commit으로 추적합니다.
여러 기능을 건드리면 별도 refactor TASK를 만들어 연결합니다.
