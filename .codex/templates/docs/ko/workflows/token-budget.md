# 토큰 예산과 wave budget

SAW는 작은 패치 전용입니다.

변경 파일, 코드 파일, 변경 줄 수가 예산을 넘으면 SAW를 멈춥니다.
이때 MAW 또는 follow-up TASK로 분리합니다.

MAW는 다릅니다.

MAW budget은 전체 신규 구현의 총량 상한이 아닙니다.

```text
전체 epic은 80개 파일이나 3000줄을 넘을 수 있습니다.
단, 한 lane과 한 wave는 예산 안에 들어와야 합니다.
```

기본 기준입니다.

```text
lane: 30 files, 900 changed lines
wave: 6 lanes, 80 files, 3000 changed lines
```

전체가 크면 wave를 나눕니다.

```text
W001 contract, schema
W002 order, payment, member backend
W003 product, cart, coupon backend
W004 frontend screens
W005 test, QA, quality, security
```

확인 명령입니다.

```text
$codex-budget status
$codex-budget suggest --text "order payment rest api" --for-ai
$codex-waves plan
$codex-waves next
```

특정 wave만 준비하고 실행합니다.

```text
$codex-lanes prepare --wave W002
$codex-lanes csv --wave W002
$codex-lanes prompt --wave W002
```

한 lane이 너무 커지면 기능을 더 나눕니다.

```text
order 전체 -> order create, order read, order state, order cancel
payment 전체 -> payment request, payment callback, payment refund
```

AI가 전체 저장소를 읽기 전에는 context pack을 먼저 봅니다.

```text
$codex-context pack --for-ai
$codex-context pack --task T001 --for-ai
```

전체 diff나 전체 파일 읽기는 마지막 수단입니다.
