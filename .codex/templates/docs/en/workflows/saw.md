# SAW low-token single workflow

$saw is for small changes that should finish with minimal context.

SAW does not skip verification.

Since v16, SAW uses a micro workflow with a mandatory verify gate.

## Goal

```text
one primary agent
one TASK
only required skills
a $codex-verify gate
one commit for traceability
```

SAW does not create test, QA, or security TASKs by default.

It still must run tests, quality checks, and security checks.

The difference is that scripts verify the change without extra agents.

## Required verification

The SAW verify gate has three parts.

```text
staged quality gate
changed-code targeted test
staged security gate
```

Use one command.

```text
$codex-verify gate --staged --for-ai
```

If code changed and no test command exists, the gate fails.

Configure test commands here.

```text
.codex/state/verify.json
```

Example:

```json
{
  "test_commands": ["npm test -- --runInBand"]
}
```

## Difference from MAW

MAW splits large work into feature lanes.

```text
order backend lane
payment backend lane
frontend checkout lane
test lane
security lane
```

SAW does not do that.

```text
T001 dto mapping fix
primary agent: backend
skills: spring-boot, api-contract
verify: script gate
```

## When to use SAW

- one bug fix
- DTO field mapping fix
- small API response fix
- one component prop cleanup
- one test update
- one documentation edit
- narrow refactor in a few files

Use MAW when there is more than one feature.

## Usage

Preview the plan.

```text
$codex-saw suggest --text "fix order DTO totalPrice mapping"
```

Create one workflow and one TASK.

```text
$codex-saw init --title dto-fix --branch hotfix/dto-fix --text "fix dto"
```

Print the next small instruction.

```text
$codex-saw prompt
```

Run the gate after editing.

```text
$codex-verify gate --staged --for-ai
```

Commit when the gate passes.

```text
$codex-task commit T001 --message "fix dto mapping"
```

The commit command re-runs the staged verify gate.

## Follow-up TASKs

Create follow-up TASKs only when the gate fails.

```text
$codex-saw followup --kind refactor --title "duplicate cleanup"
$codex-saw followup --kind security --title "auth rule check"
$codex-saw followup --kind test --title "missing regression test"
```

## Why this saves tokens

SAW avoids these defaults.

```text
no multi-agent chain
no extra TASKs by default
no lanes, worktrees, or CSV
no long TASKS.md reading
no long QA discussion
```

It uses short script output instead.

```text
$codex-state summary --for-ai
$codex-saw prompt
$codex-verify gate --staged --for-ai
$codex-task trace --for-ai
```
