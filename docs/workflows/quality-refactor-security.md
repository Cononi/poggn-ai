# 품질, 리팩토링, 보안 절차

모든 구현은 검증 없이 완료하지 않습니다.

MAW와 SAW는 검증 방식이 다릅니다.

## MAW 절차

MAW는 큰 작업이므로 별도 TASK와 lane을 사용할 수 있습니다.

```text
구현 -> 테스트 -> QA -> 품질 gate -> 리팩토링 판단 -> 보안 gate -> 최종 리뷰
```

MAW의 기능 lane commit은 먼저 품질 gate를 통과해야 합니다.

```text
$codex-quality gate --staged --for-ai
```

테스트와 보안은 별도 test, qa, security TASK에서 다룰 수 있습니다.

## SAW 절차

SAW는 작은 작업이므로 별도 agent chain을 만들지 않습니다.

하지만 테스트와 보안 검사는 생략하지 않습니다.

SAW는 아래 하나의 gate로 검증합니다.

```text
$codex-verify gate --staged --for-ai
```

이 gate는 아래를 실행합니다.

```text
staged budget gate
staged quality gate
staged security gate
changed-code targeted test
```

코드가 바뀌었는데 테스트 명령이 없으면 실패합니다.
기본 검증은 modified 파일과 untracked 신규 파일을 함께 봅니다.

테스트 명령은 아래 파일에 설정합니다.

```text
.codex/state/verify.json
```

## 리팩토링 판단

리팩토링은 항상 동작 보존이어야 합니다.

공개 API, DB 스키마, 인증 정책은 승인 없이 바꾸지 않습니다.

필요 여부는 script로 먼저 확인합니다.

```text
$codex-refactor analyze --for-ai
```

## 보안 기준

보안 gate는 secret, token, private key, password 흔적을 검사합니다.

보안 이슈가 있으면 PR 또는 MR 준비 단계로 넘어가지 않습니다.
