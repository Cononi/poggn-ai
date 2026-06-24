#!/usr/bin/env python3
"""Detect database-related repository signals without printing secrets."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable


MANIFEST_NAMES = {
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "gradle.properties",
    "libs.versions.toml",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
    "go.mod",
    "Cargo.toml",
    "Gemfile",
}

CONFIG_NAMES = {
    "application.properties",
    "application.yml",
    "application.yaml",
    "schema.prisma",
    "alembic.ini",
}

SKIP_DIRS = {
    ".git",
    ".idea",
    ".gradle",
    ".mvn",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "build",
    "dist",
    "out",
}

SIGNALS = {
    "database": {
        "postgresql": (
            "org.postgresql",
            "jdbc:postgresql:",
            "postgresql",
        ),
        "mysql": (
            "mysql-connector",
            "jdbc:mysql:",
            "com.mysql",
        ),
        "mariadb": (
            "mariadb-java-client",
            "jdbc:mariadb:",
            "org.mariadb",
        ),
        "h2": (
            "com.h2database",
            "jdbc:h2:",
        ),
    },
    "data_access": {
        "spring-data-jpa": (
            "spring-boot-starter-data-jpa",
            "spring-data-jpa",
        ),
        "hibernate": (
            "hibernate-core",
            "org.hibernate.orm",
            "jakarta.persistence",
        ),
        "mybatis": (
            "mybatis-spring-boot-starter",
            "org.mybatis",
            "mybatis",
        ),
        "jooq": (
            "org.jooq",
            "jooq",
        ),
        "spring-jdbc": (
            "spring-jdbc",
            "spring-boot-starter-jdbc",
        ),
        "sqlalchemy": (
            "sqlalchemy",
        ),
        "prisma": (
            "@prisma/client",
            "prisma",
        ),
        "ef-core": (
            "microsoft.entityframeworkcore",
        ),
        "django": (
            "django",
        ),
        "typeorm": (
            "typeorm",
        ),
    },
    "migration": {
        "flyway": (
            "flyway-core",
            "org.flywaydb",
            "flyway",
        ),
        "liquibase": (
            "liquibase-core",
            "org.liquibase",
            "liquibase",
        ),
        "alembic": (
            "alembic",
        ),
    },
}


def iter_candidate_files(root: Path, max_files: int) -> Iterable[Path]:
    count = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            path = Path(current) / name
            is_manifest = name in MANIFEST_NAMES or name.endswith(".csproj")
            is_config = name in CONFIG_NAMES
            if not is_manifest and not is_config:
                continue
            yield path
            count += 1
            if count >= max_files:
                return


def read_lower(path: Path, max_bytes: int) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="ignore").lower()
    except OSError:
        return ""


def detect(root: Path, max_files: int, max_bytes: int) -> dict[str, object]:
    matches: dict[str, dict[str, list[str]]] = {
        category: {} for category in SIGNALS
    }
    inspected: list[str] = []

    for path in iter_candidate_files(root, max_files):
        relative = str(path.relative_to(root))
        inspected.append(relative)
        text = read_lower(path, max_bytes)
        for category, technologies in SIGNALS.items():
            for technology, tokens in technologies.items():
                if any(token in text for token in tokens):
                    matches[category].setdefault(technology, []).append(relative)

    migration_dirs = []
    for candidate in (
        "src/main/resources/db/migration",
        "src/main/resources/db/changelog",
        "db/migration",
        "migrations",
        "prisma/migrations",
        "alembic/versions",
    ):
        if (root / candidate).exists():
            migration_dirs.append(candidate)

    references = []
    data_access = matches["data_access"]
    migration = matches["migration"]
    database = matches["database"]

    if "postgresql" in database:
        references.append("references/engine-postgresql.md")
    if "mysql" in database or "mariadb" in database:
        references.append("references/engine-mysql.md")
    if "flyway" in migration:
        references.append("references/migration-flyway.md")
    if "liquibase" in migration:
        references.append("references/migration-liquibase.md")
    if "spring-data-jpa" in data_access:
        references.extend(
            [
                "references/orm-jpa-hibernate.md",
                "references/orm-spring-data-jpa.md",
            ]
        )
    elif "hibernate" in data_access:
        references.append("references/orm-jpa-hibernate.md")
    if "prisma" in data_access:
        references.append("references/orm-prisma.md")
    if "sqlalchemy" in data_access:
        references.append("references/orm-sqlalchemy.md")
    if "ef-core" in data_access:
        references.append("references/orm-ef-core.md")
    if "django" in data_access:
        references.append("references/orm-django.md")
    if "typeorm" in data_access:
        references.append("references/orm-typeorm.md")
    if "mybatis" in data_access:
        references.append("references/orm-mybatis.md")
    if "jooq" in data_access or "spring-jdbc" in data_access:
        references.append("references/data-access-jdbc-jooq.md")

    return {
        "root": str(root),
        "inspected_files": inspected,
        "signals": matches,
        "migration_directories": migration_dirs,
        "suggested_references": sorted(set(references)),
        "warning": (
            "Signals are candidates only. Confirm exact runtime versions and "
            "targets before database operations."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect DB stack signals without printing file contents."
    )
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--max-files", type=int, default=300)
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    result = detect(root, args.max_files, args.max_bytes)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
