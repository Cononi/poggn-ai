---
name: spring-boot
description: Spring Boot API, service, transaction, auth boundary 작업에 사용합니다.
---

# spring-boot

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- API, service, transaction, auth boundary를 먼저 고정합니다.
- request DTO, response DTO, service command를 분리합니다.
- service method에 transaction boundary를 둡니다.

## Build Tool Contract

- 기존 프로젝트의 build tool을 먼저 확인합니다.
- gradlew, build.gradle, settings.gradle이 있으면 Gradle 프로젝트로 봅니다.
- Gradle 프로젝트에서는 pom.xml, mvnw, mvn 명령을 새로 만들거나 제안하지 않습니다.
- 검증과 실행은 기본적으로 ./gradlew test, ./gradlew bootRun을 사용합니다.
- wrapper가 없고 Gradle 파일만 있으면 gradle test를 사용하되 wrapper 추가 여부를 확인합니다.

## Procedure

- controller는 principal과 DTO mapping까지만 담당합니다.
- repository는 use case query와 persistence access만 담당합니다.
- validation은 Bean Validation과 domain guard를 함께 씁니다.
- exception handler는 stable error shape를 제공합니다.

## Expert Rules

- controller는 protocol adapter이고 business mutation은 service에 둡니다.
- transaction은 repository가 아니라 use case service boundary에 둡니다.
- DTO는 request, command, response 목적에 따라 분리합니다.
- authorization은 annotation만 믿지 말고 resource owner를 검증합니다.
- exception handler는 stable error contract와 log 민감도 기준을 가져야 합니다.
- configuration은 typed properties와 validation으로 bootstrap 실패를 빠르게 만듭니다.
- @Transactional(readOnly=true)와 write transaction 적용 위치를 구분합니다.
- async, event, scheduler 작업은 principal 없이 owner scope를 재구성합니다.

## Expert Checks

- business mutation이 controller에 있는지 봅니다.
- principal과 resource owner가 함께 검증되는지 봅니다.
- configuration property가 typed binding인지 봅니다.
- Gradle 프로젝트에서 Maven 파일이나 mvn 명령을 추가했는지 봅니다.

## Failure Modes

- controller에서 entity를 수정하고 repository를 직접 호출하는 상태.
- password, token, internal entity가 response로 노출되는 상태.
- @Transactional readOnly/write 의미가 실제 mutation과 맞지 않는 상태.
- validation이 controller에는 있지만 domain invariant에는 없는 상태.
- controller에서 entity 조회, mutation, repository 호출이 있는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- transaction 없는 multi-step write.
- resource ownership check 누락.
- entity response 또는 password/token 노출.
- Gradle 프로젝트에 Maven 빌드 파일이나 Maven 명령을 추가함.

## Verify

- Spring integration test.
- MVC auth/validation test.
- $codex-quality gate --for-ai.

## Evidence

- MVC test가 auth, validation, error shape를 검증합니다.
- service integration test가 transaction과 owner check를 검증합니다.
- entity가 API response로 직접 노출되지 않습니다.
- validation, auth, conflict 실패의 status와 error code가 고정됩니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
