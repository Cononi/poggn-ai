---
name: spring-boot
description: Use for Spring Boot API, service, transaction, and auth boundaries.
---

# spring-boot

Apply `../_references/core-rules.md` first.

## Must

- Fix API, service, transaction, and auth boundaries first.
- Separate request DTO, response DTO, and service command.
- Place transaction boundaries on service methods.

## Build Tool Contract

- Inspect the existing project build tool first.
- Treat gradlew, build.gradle, or settings.gradle as a Gradle project.
- In Gradle projects, do not create or suggest pom.xml, mvnw, or mvn commands.
- Prefer ./gradlew test and ./gradlew bootRun for verification and run commands.
- If only Gradle files exist, use gradle test and ask before adding a wrapper.

## Procedure

- Keep controllers to principal handling and DTO mapping.
- Keep repositories to use-case queries and persistence access.
- Use Bean Validation plus domain guards.
- Provide a stable error shape through exception handlers.

## Expert Rules

- Keep controllers as protocol adapters and mutations in services.
- Put transactions on service use-case boundaries, not repositories.
- Separate request DTO, command, and response DTO.
- Verify resource owner, not only annotations.
- Give exception handlers stable error contract and log-sensitivity rules.
- Use typed validated configuration for fast bootstrap failure.
- Distinguish @Transactional(readOnly=true) from write transaction placement.
- Rebuild owner scope for async, event, and scheduler work without principal.

## Expert Checks

- Check whether business mutation lives in controllers.
- Check whether principal and resource owner are both verified.
- Check whether configuration properties use typed binding.
- Check whether Maven files or mvn commands were added to a Gradle project.

## Failure Modes

- Controller mutates entities and calls repositories directly.
- Password, token, or internal entity leaks in response.
- readOnly/write transaction meaning mismatches actual mutation.
- Validation exists in controller but not domain invariants.
- Controller performs entity lookup, mutation, or repository calls.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Multi-step write lacks a transaction boundary.
- Resource ownership check is missing.
- Entity, password, or token leaks through a response.
- Maven build files or Maven commands are added to a Gradle project.

## Verify

- Spring integration test.
- MVC auth/validation test.
- quality gate.

## Evidence

- MVC tests cover auth, validation, and error shape.
- Service integration tests cover transactions and owner checks.
- Entities are not returned directly by API responses.
- Validation, auth, and conflict failures have fixed status and error codes.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
