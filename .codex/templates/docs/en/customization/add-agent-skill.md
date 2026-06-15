# Add agents and skills

Add agents under .codex/agents/{name}.toml.
Add skills under .codex/skills/{name}/SKILL.md.
Update recommendation scripts and i18n templates when needed.

## Extend as an implementer agent

An agent is an implementer when it creates actual deliverables.

Examples include `mobile`, `crawler`, and `ml`.

```text
$codex-extend check agent --name mobile --purpose "mobile UI implementation"
```

After the duplicate check, add the role to this file.

```text
.codex/state/agent_roles.json
```

Agents that need one lane per feature go here.

```json
"feature_implementation_agents": ["backend", "frontend", "mobile"]
```

Agents that run once per project go here.

```json
"single_implementation_agents": ["devops", "docs"]
```
