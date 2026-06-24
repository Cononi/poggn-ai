---
name: security
description: Security review and threat modeling for code changes, APIs, authentication, authorization, input validation, secrets, dependency risk, data exposure, injection, file handling, SSRF, XSS, CSRF, access control, privacy, logging, and abuse cases. Use when work touches user data, permissions, network calls, file uploads, payments, admin features, tokens, credentials, or external integrations.
---

# Security Skill

## 목적

변경이 악용될 수 있는 경로를 구현 전에 발견하고, 구현 후에는 검증 가능한 증거로 닫는다. 보안 검토는 일반 버그 리뷰와 분리해서 인증, 권한, 입력, 데이터, 비밀값, 의존성, 운영 노출을 따로 본다.

## 기본 원칙

- 신뢰 경계를 먼저 찾는다: browser, API, database, queue, third-party, filesystem, admin surface.
- 사용자 입력은 위치와 형식에 상관없이 불신한다.
- 인증(authentication)과 권한(authorization)을 분리해서 확인한다.
- 클라이언트 검증은 UX일 뿐이다. 보안 검증은 서버에서 한다.
- 민감 데이터는 response, log, error, analytics, cache에 새지 않게 한다.
- 보안 위험을 추측으로 PASS 처리하지 않는다. 확인 불가하면 `UNABLE_TO_JUDGE`나 남은 위험으로 남긴다.
- 보안 수정은 좁게 하고, 임의로 광범위한 정책 변경을 끼워 넣지 않는다.

## 사용 절차

1. 변경 표면을 식별한다: endpoint, UI action, job, webhook, file, dependency, config, secret.
2. 보호 자산을 정한다: user data, token, credential, money, admin action, internal URL, audit log.
3. 공격자를 가정한다: unauthenticated user, normal user, tenant user, malicious admin, compromised webhook sender.
4. 위험 범주를 확인한다: auth bypass, IDOR, injection, XSS, CSRF, SSRF, path traversal, deserialization, race, secret leak.
5. 기존 보안 패턴을 찾는다: middleware, guards, validators, sanitizers, permission helpers, audit helpers.
6. 필요한 검증을 정한다: unit, integration, permission matrix, negative test, dependency scan, manual review.
7. 결과를 PASS/FAILED/PARTIAL/NOT RUN/UNABLE_TO_JUDGE로 남긴다.

## 필수 점검 영역

### 인증과 세션

- 인증이 필요한 작업이 public route로 노출되지 않았는가.
- token/session 만료와 refresh 흐름이 기존 정책과 맞는가.
- cookie는 필요한 경우 `HttpOnly`, `Secure`, `SameSite` 정책을 따른다.
- password, token, API key는 평문 저장/로그 출력/URL 전달을 하지 않는다.

### 권한과 테넌시

- 리소스 접근은 user id만이 아니라 owner, organization, tenant, role을 확인한다.
- object id를 바꾸는 IDOR 시나리오를 테스트한다.
- admin action은 일반 사용자 경로와 분리하고 서버에서 다시 권한을 확인한다.
- list/search/export는 행 단위 권한 필터가 빠지지 않았는지 확인한다.

### 입력 검증과 injection

- SQL/NoSQL/query builder 사용 시 parameter binding 또는 안전한 API를 사용한다.
- command execution, template rendering, dynamic import/eval, regex는 입력 주입 위험을 확인한다.
- HTML/Markdown/user content는 escaping/sanitization 정책을 따른다.
- file name, path, MIME type, archive extraction은 path traversal과 type spoofing을 확인한다.

### 네트워크와 외부 연동

- webhook은 signature, timestamp, replay 방지를 확인한다.
- outbound URL fetch는 SSRF, internal IP, metadata endpoint, redirect를 제한한다.
- third-party API 오류는 민감 정보를 노출하지 않고 retry/backoff 정책을 따른다.
- callback URL, redirect URL은 allowlist 또는 엄격한 검증을 사용한다.

### 데이터와 개인정보

- response에 필요한 필드만 포함한다.
- log, analytics, error reporting에 개인정보와 secret을 남기지 않는다.
- export/download는 권한, audit, rate limit 필요 여부를 확인한다.
- cache key가 tenant/user 경계를 섞지 않는지 확인한다.

### 프론트엔드 보안

- XSS 위험이 있는 HTML 삽입, dangerouslySetInnerHTML, v-html, innerHTML 사용을 확인한다.
- CSRF 방어가 필요한 mutation 요청인지 확인한다.
- 권한에 따른 UI 숨김은 보조 수단이다. 서버 권한 검증이 있어야 한다.
- 토큰을 localStorage/sessionStorage에 저장하는 경우 기존 정책과 위험을 확인한다.

### 의존성과 설정

- 새 dependency는 유지보수 상태, install script, transitive risk, license/policy를 확인한다.
- secret, .env, credential, private key가 repo에 추가되지 않았는지 확인한다.
- debug flag, permissive CORS, test credential, verbose error가 production path에 남지 않게 한다.

## 보안 산출물

필요한 경우 다음 형식으로 보고한다.

```md
Security Review:
- Surface: 검토한 변경 표면
- Assets: 보호해야 할 자산
- Threats: 확인한 위협
- Findings: 발견한 문제와 심각도
- Verification: 실행한 테스트/명령/수동 확인
- Result: PASS | FAILED | PARTIAL | NOT RUN | UNABLE_TO_JUDGE
- Residual Risk: 남은 위험과 후속 조치
```

## Multi Agent 연결

- 보안 영향이 독립적으로 검토 가능하면 `pogo-security-agent`를 사용한다.
- backend/front/architecture agent가 구현한 결과 중 인증, 권한, 데이터, 네트워크, 파일, secret이 걸리면 security agent 검토를 거친다.
- security agent는 직접 구현보다 발견, 재현 조건, 필요한 수정 방향, 검증 기준을 우선 반환한다.
- 심각한 보안 문제가 있으면 메인 에이전트가 작업을 중단하고 수정 범위를 재계획한다.

## 완료 체크리스트

- 인증과 권한 검증이 서버 경계에 있는가.
- IDOR, injection, XSS/CSRF/SSRF, path traversal 위험을 확인했는가.
- 민감 데이터가 response/log/error/cache에 새지 않는가.
- 새 dependency와 config가 보안 위험을 늘리지 않는가.
- 실패/공격 케이스 테스트 또는 검증 증거가 있는가.
