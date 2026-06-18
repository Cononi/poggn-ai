# 빠른 시작

프로젝트 루트에 ZIP을 풉니다.

```bash
python3 .codex/script/setup_links.py
```

언어를 확인합니다.

```text
$codex-language status
```

한국어로 전환합니다.

```text
$codex-language ko
```

Git 상태를 확인합니다.

```text
$codex-git doctor
```

MAW를 시작합니다.

```text
$maw spring boot 쇼핑몰 order payment rest api swagger jpa
```

Codex는 한 번에 하나의 질문만 해야 합니다.
요구사항이 충분해지면 agent 추천을 보여줍니다.
사용자는 추천 목록을 보고 필요한 agent를 선택하거나 추가합니다.

상태 조회는 아래처럼 shortcut을 사용합니다.

```text
$codex-state summary --for-ai
$codex-task trace --for-ai
```

## SAW 최소 토큰 예

```text
$codex-saw suggest --text "dto 필드 매핑 오류 수정"
```



## 초기 설계 gate

큰 요청은 구현 전에 product type, platform/runtime, framework/engine,
capability, stack decision을 먼저 분류합니다.

```text
$codex-work-items suggest --text "spring boot react 커뮤니티" --agents backend,frontend
```

Spring Boot가 명시되면 domain-first Java 패키지 구조 계약이 붙습니다.
React만 명시되면 Vite SPA와 Next.js/SSR 선택을 먼저 확인합니다.
Next.js가 명시되면 `src/app` App Router와 server/client 경계를 계약으로 둡니다.
