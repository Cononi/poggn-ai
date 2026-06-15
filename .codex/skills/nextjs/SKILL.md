---
name: nextjs
description: Next.js route, server/client boundary, cache 정책 작업에 사용합니다.
---

# nextjs

먼저 `../_references/core-rules.md`를 적용합니다.

## Must

- server component와 client component 경계를 먼저 정합니다.
- page.tsx는 route composition과 data boundary만 담당합니다.
- secret이나 server-only env가 client bundle에 들어가지 않게 합니다.

## Procedure

- server action은 validation, authz, mutation을 분리합니다.
- cache, revalidate, dynamic 정책을 데이터 성격에 맞춥니다.
- loading, error, not-found boundary를 route 수준에서 검토합니다.
- form mutation은 optimistic update와 rollback을 고려합니다.

## Expert Rules

- server/client boundary는 import graph로 검증해야 합니다.
- server action은 validation, authz, mutation, revalidation을 분리합니다.
- cache policy는 데이터 민감도와 mutation 빈도에 맞게 명시합니다.
- route segment별 loading/error/not-found는 사용자 흐름을 막지 않아야 합니다.
- client component는 interaction state만 갖고 secret이나 server env를 몰라야 합니다.
- SEO metadata는 route 책임이며 client-only 데이터에 의존하지 않습니다.
- use client는 leaf component로 제한하고 page/layout 확산을 차단합니다.
- cookies, headers, auth session 사용 시 static rendering 영향을 검토합니다.

## Expert Checks

- client-only dependency가 server path에 들어갔는지 봅니다.
- stale-sensitive mutation에 cache policy가 있는지 봅니다.
- metadata와 SEO 책임이 route에 맞는지 봅니다.

## Failure Modes

- server-only module이 client bundle로 흘러가는 상태.
- mutation 후 stale cache가 권한이나 결제 상태를 잘못 보여주는 상태.
- form validation이 client에만 있고 server action에 없는 상태.
- dynamic rendering 필요 페이지가 static cache로 굳는 상태.
- middleware matcher가 넓어 redirect loop를 만드는 상태.

## Never

- TASK 범위 밖 파일을 수정하지 않습니다.
- 실패한 검증을 성공처럼 보고하지 않습니다.
- unrelated user change를 stage하거나 revert하지 않습니다.

## Blocker

- client component에서 secret 참조.
- page 하나에 data, mutation, UI state 혼합.
- cache/revalidate 누락으로 stale bug 유발.

## Verify

- Next build/typecheck.
- route smoke test.
- bundle boundary review.

## Evidence

- build 또는 bundle check가 통과합니다.
- server action test가 validation과 authz를 검증합니다.
- cache/revalidate 정책이 코드와 문서에 남아 있습니다.
- mutation 후 revalidatePath 또는 revalidateTag 경로를 확인했습니다.

## Done

- 변경 파일, 실행 검증, 차단 사유, 남은 위험, TASK/commit 연결을 보고합니다.
