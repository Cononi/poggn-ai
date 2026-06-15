---
name: ci-cd
description: Use for CI workflows, Docker, deployment, and release pipeline changes.
---

# ci-cd

Apply `../_references/core-rules.md` first.

## Must

- Check trigger, branch guard, and environment guard first.
- Pass secrets only through masked env or protected secret stores.
- Fail the pipeline when tests fail; do not hide failures.

## Procedure

- Include lockfile and runtime version in cache keys.
- Keep secrets out of Docker build context, layers, and logs.
- Add approval, rollback, and environment split to deploy jobs.
- Separate migration jobs from app deploy order.

## Expert Rules

- Design pipelines to expose failure early and open deploy slowly.
- Make caches reproducible and uncontaminated before making them fast.
- Track secrets across env, logs, artifacts, and image layers.
- Review deploy branch, tag, environment, and approval gates together.
- Include rollback order for migrations and app rollout.
- Separate supported runtime matrix from deployed runtime.
- Review permissions and deploy paths by PR, push, tag, and manual trigger.
- Treat pull_request_target checkout ref and secret exposure as blockers.

## Expert Checks

- Check for `|| true` or `continue-on-error` hiding failures.
- Check that production deploy requires tag or branch guards.
- Check artifact retention for secrets and build output leaks.

## Failure Modes

- continue-on-error hides required test failures.
- pull_request jobs use write tokens or production secrets.
- Docker layers contain .env or build-arg secrets.
- Rollback job shares the same failure condition as deploy.
- Deploy can race without concurrency or environment lock.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Production deploy has no environment guard.
- Secret is written to repo, cache, artifact, or image layer.
- Test failure is intentionally ignored.

## Verify

- workflow lint.
- dry-run or local build.
- secret exposure review.

## Evidence

- Workflow triggers and permission diff were reviewed.
- Failure paths stop the pipeline.
- Artifacts and caches contain no sensitive files.
- Frozen lockfile install and cache-key basis were checked.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
