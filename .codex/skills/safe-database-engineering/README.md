# Safe Database Engineering Skill

관계형 데이터베이스 변경을 안전하게 설계하고 검증하는 Agent Skill이다.

핵심 `SKILL.md`는 ORM 중립이다.
저장소에서 확인된 DB 엔진, migration 도구, ORM 문서만 선택적으로 읽는다.

## 구조

```text
safe-database-engineering/
├── SKILL.md
├── assets/
│   ├── database-change-spec-template.md
│   └── migration-runbook-template.md
├── references/
│   ├── schema-design.md
│   ├── migration-safety.md
│   ├── transactions-concurrency.md
│   ├── query-performance.md
│   ├── operations-security.md
│   ├── engine-postgresql.md
│   ├── engine-mysql.md
│   ├── migration-flyway.md
│   ├── migration-liquibase.md
│   ├── orm-jpa-hibernate.md
│   ├── orm-spring-data-jpa.md
│   ├── orm-prisma.md
│   ├── orm-sqlalchemy.md
│   ├── orm-ef-core.md
│   ├── orm-django.md
│   ├── orm-typeorm.md
│   ├── orm-mybatis.md
│   └── data-access-jdbc-jooq.md
└── scripts/
    └── detect_db_stack.py
```

## 선택적 로딩

Spring Data JPA가 확인되면 다음 두 문서만 함께 읽는다.

```text
references/orm-jpa-hibernate.md
references/orm-spring-data-jpa.md
```

Prisma 프로젝트에서는 JPA 문서를 읽지 않는다.

```text
references/orm-prisma.md
```

MyBatis는 ORM이 아니라 SQL mapper이므로 별도 문서를 읽는다.

```text
references/orm-mybatis.md
```

직접 JDBC 또는 jOOQ를 사용하면 ORM 문서 대신 다음을 읽는다.

```text
references/data-access-jdbc-jooq.md
```

## 읽기 전용 탐지

```bash
python3 scripts/detect_db_stack.py /path/to/repository
```

스크립트는 dependency와 설정에서 기술 후보와 관련 참조만 출력한다.
파일 내용, 연결 문자열, credential은 출력하지 않는다.
탐지 결과는 후보이므로 정확한 runtime 버전과 대상 환경을 다시 확인한다.

## AGENTS.md 연결 예시

```md
데이터베이스, SQL, migration, ORM 변경에는
`.agents/skills/safe-database-engineering/SKILL.md`를 읽고 따른다.
실제 저장소에서 확인된 DB 엔진과 ORM 참조만 추가로 읽는다.
```

파일을 저장소에 두기만 하면 모든 에이전트가 자동으로 읽는 것은 아니다.
사용 중인 에이전트가 skill catalog 또는 `AGENTS.md`를 통해 발견할 수 있어야 한다.
