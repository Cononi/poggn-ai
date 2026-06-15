---
name: plugin-builder
description: Use for Codex plugin scaffolds, manifests, and skill bundles.
---

# plugin-builder

Apply `../_references/core-rules.md` first.

## Must

- Confirm this is a plugin request, not a normal feature request.
- Match manifest paths to real skills, commands, and assets.
- Keep plugin scope installable as an independent unit.

## Procedure

- Include trigger, blocker, and verification in skill bundles.
- Check cache-busting or reinstall steps during development.
- Set marketplace ordering and availability metadata.
- Keep plugin code separate from host project code.

## Expert Rules

- Keep plugins independently installable from the host project.
- Treat manifest as discovery contract, not metadata decoration.
- Include trigger, forbidden work, and verification in skill bundles.
- Place assets by whether they are output material or instruction.
- Make cache busting part of install verification.
- Review private plugins for path, secret, and organization leakage.
- Validate .codex-plugin/plugin.json schema and relative paths before install.
- Document command idempotency, cwd, and sandbox permissions.

## Expert Checks

- Check manifest required fields.
- Check private plugins for sensitive paths or secrets.
- Check install or cache refresh verification.

## Failure Modes

- Manifest points to missing or stale files.
- Host app code and plugin code mix in one commit.
- Files are created but discovery fails after install.
- Marketplace metadata does not match actual availability.
- Plugin and project code depend on each other both ways.

## Never

- Do not edit files outside TASK scope.
- Do not report failed verification as success.
- Do not stage or revert unrelated user changes.

## Blocker

- Manifest references missing files.
- Plugin leaks host-project private paths or secrets.
- Install path cannot be verified.

## Verify

- manifest validation.
- plugin discovery.
- install/cache refresh test.

## Evidence

- Manifest validation and discovery result exist.
- Install/reinstall or cache refresh was verified.
- Plugin scope and included files are reported.
- Marketplace id, order, visibility, and compatibility were checked.

## Done

- Report changed files, verification, blockers, residual risk, and TASK/commit link.
