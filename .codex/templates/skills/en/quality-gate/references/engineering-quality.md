# Engineering Quality Gate

## Blocking Issues

- Business rules are scattered across controllers, UI, config, or scripts.
- Public APIs expose persistence entities or internal enums.
- Authorization, ownership, or tenant boundaries are missing.
- List/detail serialization risks N+1 or lazy loading failures.
- Multi-step writes lack transaction boundaries.
- Test, build, or security failures are missing exact evidence.
- Files exceed 200 lines or frontend components exceed 160 without reason.
- Validation, mapping, or business rules are duplicated.

## Done

A quality lane reports pass/fail, file/line, command evidence, and follow-up TASKs.
