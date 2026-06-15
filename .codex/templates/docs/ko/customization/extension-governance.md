# 확장 거버넌스

agent와 skill은 계속 확장할 수 있습니다.

하지만 무작위 생성은 금지합니다.

먼저 기존 agent와 skill이 처리할 수 있는지 검사합니다.

```text
$codex-extend scan --text "payment webhook 검증" --for-ai
```

또는 agent와 skill 후보를 명시해서 검사합니다.

```text
$codex-capabilities inspect --text "요청" --agents "name" --skills "name"
```

유사 항목이 있으면 새로 만들지 않고 기존 capability를 재사용합니다.

중복이 없고 목적이 명확할 때만 생성합니다.

```text
$codex-edit-mode on
$codex-extend create-agent --name webhook-reviewer \
  --purpose "webhook 변경만 검토" \
  --approve --reason "중복 없음"
$codex-edit-mode off
```

새 skill은 하나의 반복 workflow만 담당해야 합니다.

```text
$codex-edit-mode on
$codex-extend create-skill --name webhook-safety \
  --purpose "webhook 검증 절차" \
  --domain "backend integration" --approve
$codex-edit-mode off
```

새 agent는 자기 사명만 수행합니다.

구현 agent는 자기 영역의 소스 구현만 담당합니다.

test_writer는 테스트 코드 작성만 담당합니다.

테스트 실행은 test_runner가 담당합니다.

QA, refactor, security는 필요한 조건에서만 후속 이벤트로 생성됩니다.

새 skill은 목적, 트리거, 단계, 금지사항, clean code, 검증을 포함합니다.

그 분야 전문가가 권장하는 모듈 경계와 구조를 구체적으로 적습니다.

스파게티 코드, 거대 파일, 중복 로직, 숨은 부작용을 금지합니다.

custom downstream rule도 승인 후 추가할 수 있습니다.

```text
$codex-extend add-downstream --agent webhook-reviewer \
  --stage webhook_review --after-stage implement \
  --title "Webhook review" --keywords webhook,payment --approve
```

생성 후 아래를 확인합니다.

```text
$codex-agents check
$codex-skills list
$codex-extend check
```
