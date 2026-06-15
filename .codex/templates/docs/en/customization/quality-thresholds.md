# Customize Quality Thresholds

Quality thresholds are controlled by `.codex/script/codex_quality.py` arguments.

The default source file limit is 200 lines.

The default frontend component limit is 160 lines.

The default page limit is 120 lines.

## Examples

```text
$codex-quality gate --front-lines 140 --page-lines 100 --for-ai
```

```text
$codex-quality gate --strict --for-ai
```

Strict mode treats warnings as failures.

If the team standard is stronger, make hooks call strict mode.

## Recommended settings

For small projects, use front-lines 140.

For large projects, apply shared/ui and features separation first.

For legacy JS projects, create a migration TASK and move to TS.
