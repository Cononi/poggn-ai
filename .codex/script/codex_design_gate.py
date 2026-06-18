#!/usr/bin/env python3
from __future__ import annotations
import re
import codex_feature_infer


def words(text: str) -> set[str]:
    """Return normalized request words used by design classifiers."""
    return codex_feature_infer.words(text)


def has(text: str, keys: str) -> bool:
    """Return whether text contains any classifier key by word or suffix."""
    return any(word_or_suffix(text, token) for token in words(keys))


def word_or_suffix(text: str, term: str) -> bool:
    """Match exact tokens and Korean suffix forms without broad substrings."""
    q = words(text); term = term.lower()
    if term in q:
        return True
    return any(w.startswith(term) and len(w) > len(term) and not w[len(term)].isascii()
               for w in q)


def explicit_stack(text: str) -> list[str]:
    """Extract user-explicit frameworks and libraries from request text."""
    lower = text.lower(); out = []
    checks = [
        ("Spring Boot", lambda: "spring boot" in lower or "springboot" in lower),
        ("React Native", lambda: "react native" in lower or "reactnative" in lower),
        ("TanStack Query", lambda: "tanstack" in lower or "react query" in lower),
        ("Next.js", lambda: word_or_suffix(text, "next") or "next.js" in lower or "nextjs" in lower),
        ("React", lambda: word_or_suffix(text, "react") or word_or_suffix(text, "jsx") or word_or_suffix(text, "tsx")),
        ("JPA", lambda: word_or_suffix(text, "jpa")),
        ("H2", lambda: word_or_suffix(text, "h2")),
        ("MUI", lambda: word_or_suffix(text, "mui") or "material ui" in lower),
        ("Axios", lambda: word_or_suffix(text, "axios")),
        ("Zustand", lambda: word_or_suffix(text, "zustand") or word_or_suffix(text, "justand")),
        ("Gradle", lambda: word_or_suffix(text, "gradle")),
        ("Maven", lambda: word_or_suffix(text, "maven") or word_or_suffix(text, "mvn")),
        ("Vue", lambda: word_or_suffix(text, "vue")),
        ("Svelte", lambda: word_or_suffix(text, "svelte")),
        ("Flutter", lambda: word_or_suffix(text, "flutter")),
        ("Unity", lambda: word_or_suffix(text, "unity")),
        ("Unreal", lambda: word_or_suffix(text, "unreal")),
        ("Godot", lambda: word_or_suffix(text, "godot")),
        ("Phaser", lambda: word_or_suffix(text, "phaser")),
        ("Three.js", lambda: "three.js" in lower or word_or_suffix(text, "threejs")),
        ("FastAPI", lambda: word_or_suffix(text, "fastapi")),
        ("Django", lambda: word_or_suffix(text, "django")),
        ("NestJS", lambda: word_or_suffix(text, "nestjs")),
        ("Electron", lambda: word_or_suffix(text, "electron")),
        ("Tauri", lambda: word_or_suffix(text, "tauri")),
    ]
    for name, ok in checks:
        if ok() and name not in out:
            out.append(name)
    return out


def spring_boot_package_layout() -> list[str]:
    """Return the Spring Boot domain-first package layout contract."""
    return [
        "spring-boot package layout: root package owns the Application class",
        "domain-first modules: member/post/comment/... before layer packages",
        "inside each domain: api, application, domain, infrastructure",
        "api owns Controller and request/response DTO",
        "application owns Service/use-case and command DTO",
        "domain owns Entity/value/domain rule/repository interface",
        "infrastructure owns JPA repository and external adapters",
        "shared owns response/exception/validation/util",
        "platform owns config/security/filter/web infrastructure",
        "do not create top-level controller/service/repository/entity packages by default",
    ]


def nextjs_frontend_layout() -> list[str]:
    """Return the Next.js App Router frontend layout contract."""
    return [
        "nextjs layout: use src/app App Router for routes, layouts, loading/error/not-found",
        "keep page.tsx as route composition and data boundary only",
        "keep domain UI/business code outside route files in src/features/<feature>",
        "feature modules own api, model, store, hooks, components",
        "shared owns ui, api client, lib, config, types",
        "providers live in src/app/providers and are client components only when needed",
        "use client is limited to leaf interactive components, not page/layout by default",
        "server-only env, cookies, headers, and secrets must not enter client bundle",
        "route groups like (marketing)/(app)/(admin) organize layouts without URL impact",
        "define cache/revalidate/dynamic policy for server data and mutations",
    ]


def react_spa_frontend_layout() -> list[str]:
    """Return the React SPA feature-first layout contract."""
    return [
        "react-spa layout: src/app for router/providers/bootstrap",
        "pages own route composition only",
        "features/<feature> owns api, model, store, hooks, components",
        "shared owns ui, api client, lib, config, types",
        "TanStack Query owns server state; Zustand owns client/UI state",
    ]


def frontend_layout_contract(decisions: dict) -> list[str]:
    """Return frontend layout rules only when a framework is explicit."""
    explicit = set(decisions["explicit"])
    if "Next.js" in explicit:
        return nextjs_frontend_layout()
    if "React" in explicit:
        return []
    return []


def product_types(text: str) -> list[str]:
    """Classify the requested product surface before implementation."""
    out = []
    checks = [
        ("game", "game 게임 unity unreal godot phaser gameplay multiplayer"),
        ("mobile app", "mobile app ios android flutter 앱"),
        ("web app", "web browser react vue svelte next 커뮤니티 community board"),
        ("api/service", "api backend server spring boot fastapi django nestjs webhook"),
        ("desktop app", "desktop electron tauri windows macos linux"),
        ("data/ai pipeline", "data pipeline etl ai ml batch airflow spark"),
        ("cli/tooling", "cli command tool automation script"),
        ("plugin/sdk/library", "plugin sdk library package npm maven gradle plugin"),
    ]
    for name, keys in checks:
        if has(text, keys):
            out.append(name)
    return out or ["unknown product type"]


def platform_gate(types: list[str]) -> list[str]:
    """Return platform/runtime questions for detected product types."""
    mapping = {
        "game": "confirm runtime: browser, Unity, Unreal, Godot, native desktop/mobile",
        "mobile app": "confirm platform: iOS, Android, cross-platform, webview",
        "web app": "confirm platform: browser SPA, SSR/public site, admin/backoffice",
        "api/service": "confirm runtime: server, serverless, container, internal API",
        "desktop app": "confirm runtime: Electron, Tauri, native desktop",
        "data/ai pipeline": "confirm runtime: batch, streaming, notebook, scheduled job",
        "cli/tooling": "confirm runtime: local CLI, CI tool, daemon",
    }
    return [mapping[t] for t in types if t in mapping] or ["confirm platform/runtime before implementation"]


def capability_gate(text: str, feats: list[str], types: list[str]) -> list[str]:
    """Return domain capability questions implied by product type and features."""
    out = []
    if "game" in types:
        out += ["gameplay rules", "engine/rendering", "assets", "save", "multiplayer if needed"]
    if "web app" in types or "api/service" in types:
        out += ["API contract", "auth/owner rules", "data model", "error shape", "test strategy"]
    if "mobile app" in types:
        out += ["navigation", "offline/cache", "push notification", "app distribution"]
    if "data/ai pipeline" in types:
        out += ["input schema", "job schedule", "storage", "monitoring", "retry policy"]
    if {"post", "comment"} & set(feats):
        out.append("community scope: board MVP vs SNS/realtime/moderation")
    return out[:8] or ["domain capability pending"]


def stack_decisions(text: str, feats: list[str], types: list[str]) -> dict:
    """Classify stack items into explicit, confirm, candidate, and defer groups."""
    explicit = explicit_stack(text); e = set(explicit); confirm = []; candidate = []; defer = []
    if "unknown product type" in types:
        confirm.append("product type: web, mobile, game, API/service, CLI, data pipeline, plugin")
    elif len(types) > 1:
        confirm.append("primary product type and included secondary surfaces")
    if "Spring Boot" in e:
        if not ({"Gradle", "Maven"} & e): confirm.append("backend build tool: Gradle or Maven")
        if not ({"JPA"} & e): candidate.append("JPA for relational CRUD unless reactive/no-SQL is confirmed")
        if not ({"H2"} & e): confirm.append("database: H2/dev only or production DB too")
        candidate.append("Spring MVC/REST unless reactive streaming is confirmed")
    if "React" in e or "Next.js" in e:
        if "Next.js" not in e: confirm.append("rendering: Vite SPA or SSR/Next.js")
        if "MUI" not in e: confirm.append("UI library: MUI, Tailwind, shadcn/ui, plain CSS, existing design system")
        if "Next.js" in e and "Axios" not in e:
            confirm.append("data access: Next server fetch/server actions or Axios client boundary")
        elif "Axios" not in e:
            confirm.append("HTTP client: Axios or fetch wrapper")
        if "Zustand" not in e: confirm.append("client state: Zustand, Redux, Context, local state")
        if "TanStack Query" not in e: confirm.append("server state/cache: TanStack Query or framework data APIs")
        candidate.append("TypeScript for React implementation")
    if "Next.js" in e:
        candidate.append("Next.js App Router unless Pages Router migration is confirmed")
    if "game" in types and not ({"Unity", "Unreal", "Godot", "Phaser", "Three.js"} & e):
        confirm.append("game engine/framework: Unity, Unreal, Godot, Phaser, Three.js, custom canvas")
    defer_rules = [
        ("WebFlux", "webflux reactive streaming sse", "defer WebFlux unless reactive streaming/backpressure is required"),
        ("WebSocket", "websocket realtime 실시간 chat 채팅", "defer WebSocket unless realtime/chat/live updates are required"),
        ("Redis", "redis cache session rate limit", "defer Redis unless cache/session/rate-limit is required"),
        ("OAuth", "oauth social kakao google naver", "defer OAuth/social login unless explicitly required"),
        ("GraphQL", "graphql", "defer GraphQL; REST/RPC is default unless query flexibility is required"),
    ]
    for _, keys, note in defer_rules:
        if not has(text, keys): defer.append(note)
    return {"explicit": explicit, "confirm": confirm[:8], "candidate": candidate[:6], "defer": defer[:6]}


def stack_contract(request_text: str) -> dict:
    """Build the architecture contract attached to foundation lanes."""
    feats = codex_feature_infer.infer_features(request_text, "")
    types = product_types(request_text)
    decisions = stack_decisions(request_text, feats, types)
    package_layout = (
        spring_boot_package_layout()
        if "Spring Boot" in decisions["explicit"] else []
    )
    frontend_layout = frontend_layout_contract(decisions)
    questions = []
    questions += decisions["confirm"][:3]
    questions += capability_gate(request_text, feats, types)[:2]
    stack = [
        "explicit=" + (", ".join(decisions["explicit"]) or "none"),
        "confirm=" + ("; ".join(decisions["confirm"][:3]) or "none"),
        "candidate=" + ("; ".join(decisions["candidate"][:3]) or "none"),
        "contract-first: product/platform/framework/API/data/auth/verification before implementation",
    ]
    return {
        "product_type_gate": types,
        "platform_gate": platform_gate(types),
        "framework_gate": decisions,
        "capability_gate": capability_gate(request_text, feats, types),
        "package_layout_contract": package_layout,
        "frontend_layout_contract": frontend_layout,
        "stack_contract": stack,
        "excluded_stack": decisions["defer"],
        "clarification_order": questions[:5] or ["confirm product type and primary runtime"],
        "auto_decisions": [
            "Do not create implementation lanes until product/platform/framework blockers are resolved",
            "Use explicit user stack as fixed input; classify missing stack as confirm/candidate/defer",
            "Ask only decisions that are expensive to change after implementation",
        ],
    }


def backend_contract(request_text: str) -> dict:
    """Build backend-specific contract rows for implementation lanes."""
    c = stack_contract(request_text); d = c["framework_gate"]
    rows = ["explicit=" + (", ".join(x for x in d["explicit"] if x in {"Spring Boot", "JPA", "H2", "Gradle", "Maven"}) or "none")]
    rows += [x for x in d["confirm"] if any(k in x for k in ["backend", "database", "build tool"])]
    rows += [x for x in d["candidate"] if any(k in x for k in ["JPA", "Spring", "REST"])]
    rows += ["entity is not API response; DTO/command/response are separated"]
    return {
        "backend_contract": rows[:8],
        "package_layout_contract": c.get("package_layout_contract", []),
    }
