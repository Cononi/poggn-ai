---
name: architecture
description: Software architecture review and planning for module boundaries, dependencies, data flow, scalability, maintainability, migration risk, and cross-cutting design decisions. Use when changes affect multiple modules, public contracts, layering, shared abstractions, integration boundaries, or long-term code structure.
---

# Architecture Skill

## 목적

구현 전에 구조적 위험을 줄이고, 변경 범위를 명확히 나누며, 유지보수 가능한 방향을 선택한다. 코드 작성보다 먼저 경계, 책임, 의존성, 데이터 흐름, 검증 방법을 확인한다.

## 기본 원칙

- 기존 아키텍처와 디렉터리 구조를 먼저 읽는다.
- 새 추상화는 실제 중복, 복잡도, 계약 안정성 문제를 줄일 때만 만든다.
- 단일 기능을 위해 전역 구조를 바꾸지 않는다.
- public API, 데이터 계약, 모듈 경계가 바뀌면 영향 범위를 명시한다.
- 단기 구현 편의보다 변경 후 이해 가능성과 검증 가능성을 우선한다.
- 모르는 의존성, 런타임 제약, 배포 제약을 가정하지 않는다.

## 사용 절차

1. 변경 목표와 외부 동작 변화를 한 문장으로 정리한다.
2. 현재 구조를 확인한다: 진입점, 모듈 경계, shared layer, data flow, test boundary.
3. 변경 등급을 판단한다: 국소 변경, 모듈 간 변경, 계약 변경, 마이그레이션/호환성 변경.
4. 가능한 설계안을 1-3개로 제한하고 tradeoff를 비교한다.
5. 선택한 설계의 구현 단위를 작게 나누고 각 단위의 검증 방법을 붙인다.
6. 구조 변경 후 orphan import, 죽은 경로, 중복 책임이 생겼는지 확인한다.

## 판단 기준

### 좋은 구조

- 책임이 한 곳에 모여 있고 호출 방향이 예측 가능하다.
- domain, application, infrastructure, UI 계층이 뒤섞이지 않는다.
- shared 코드는 실제로 둘 이상에서 쓰이고 이름이 구체적이다.
- 외부 시스템 연동은 경계가 분명하고 mock/test seam이 있다.
- 실패 동작과 edge case가 호출자에게 명확히 전달된다.

### 피해야 할 구조

- 미래를 추측한 과도한 abstraction.
- 한 번 쓰는 factory, manager, registry, adapter.
- UI 상태와 서버 도메인 규칙의 혼합.
- 데이터 저장 구조와 API 응답 구조의 무분별한 공유.
- 순환 의존성, 암묵적 singleton, 전역 mutable state.
- 테스트를 어렵게 만드는 숨은 IO와 시간/랜덤 의존성.

## 설계 산출물

작업 전에 필요한 만큼만 다음 형식으로 남긴다.

```md
Architecture Decision:
- Recommendation: 선택한 접근
- Reason: 기존 구조와 맞는 이유
- Alternatives: 버린 대안과 이유
- Scope: 수정할 모듈/파일
- Contracts: 바뀌는 API, 타입, 데이터 계약
- Verification: 구조와 동작을 확인할 테스트/명령
- Risk: 남은 위험과 되돌리는 방법
```

## Multi Agent 연결

- 구조 탐색, 영향 범위 분석, 대안 비교가 독립적으로 가능하면 `pogo-architecture-agent`를 사용한다.
- 구현 자체가 여러 영역으로 나뉘면 architecture agent는 전체 방향과 경계만 제시하고, backend/front/designer agent가 각 영역을 맡는다.
- 구조 판단이 끝나기 전에는 여러 worker가 같은 파일을 병렬 편집하지 않게 한다.

## 검증 체크리스트

- 변경된 구조가 기존 호출 방향과 충돌하지 않는가.
- 새 abstraction이 실제 복잡도를 줄이는가.
- 삭제되거나 이동된 코드의 참조가 남아 있지 않은가.
- public contract 변경이 테스트와 문서에 반영되었는가.
- 실패/rollback 경로가 필요한 변경이면 계획에 포함되었는가.
