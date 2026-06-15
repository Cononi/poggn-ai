# 개요

이 템플릿은 Codex를 Git 기반 개발 자동화에 안전하게 쓰기 위한 구조입니다.
목표는 AI가 코드를 작성하되, 상태 추적과 반복 작업은 스크립트가 맡는 것입니다.
그래서 TASK, lane, commit, diff, rollback은 사람이 보기 좋은 문서와 별개로
JSONL 원본 상태에 기록됩니다.

핵심 원칙은 네 가지입니다.

- agent는 역할입니다.
- skill은 반복 가능한 절차입니다.
- lane은 병렬 실행 단위입니다.
- TASK는 commit과 연결되는 추적 단위입니다.

예를 들어 쇼핑몰 REST API를 만든다면 backend agent 하나가 모든 것을 하지 않습니다.
Order REST API와 Payment REST API는 서로 다른 lane으로 나뉩니다.
하지만 Spring Boot, JPA, Swagger는 agent가 아니라 backend agent가 쓰는 skill입니다.

토큰 최적화는 긴 문서를 계속 읽지 않는 방식으로 달성합니다.
$codex-state, $codex-task, $codex-quality 같은 shortcut은 hook에서 처리됩니다.
따라서 상태 조회, 완료 처리, 품질 검사 결과는 모델로 보내지지 않습니다.
