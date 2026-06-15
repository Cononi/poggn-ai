# Extension governance

Agents and skills can grow without a fixed upper bound.

Random creation is not allowed.

First check whether an existing agent or skill can handle the request.

```text
$codex-extend scan --text "payment webhook review" --for-ai
```

Or inspect explicit agent and skill candidates.

```text
$codex-capabilities inspect --text "request" --agents "name" --skills "name"
```

Reuse an existing capability when a similar item exists.

Create only when the purpose is unique and clear.

```text
$codex-edit-mode on
$codex-extend create-agent --name webhook-reviewer \
  --purpose "review webhook changes only" \
  --approve --reason "no duplicate"
$codex-edit-mode off
```

A new skill must cover one repeatable workflow only.

```text
$codex-edit-mode on
$codex-extend create-skill --name webhook-safety \
  --purpose "webhook verification workflow" \
  --domain "backend integration" --approve
$codex-edit-mode off
```

A new agent performs only its own mission.

backend implements product source code only.

test_writer writes test code only.

test_runner runs tests and summarizes failures only.

QA, refactor, and security are created only when event policy needs them.

A new skill includes purpose, trigger, steps, cautions, clean code, and checks.

Write concrete domain structure and module-boundary guidance.

Block spaghetti code, giant files, duplicate logic, and hidden side effects.

You can add custom downstream rules after approval.

```text
$codex-extend add-downstream --agent webhook-reviewer \
  --stage webhook_review --after-stage implement \
  --title "Webhook review" --keywords webhook,payment --approve
```

Check after creation.

```text
$codex-agents check
$codex-skills list
$codex-extend check
```
