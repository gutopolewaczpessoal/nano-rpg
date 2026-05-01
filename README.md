# nano-rpg

RPG engine powered by NanoClaw agents and Temporal orchestration.

Three AI agents — **Mestre** (narrator), **Zoe**, and **Rafael** (player characters) — run in isolated NanoClaw containers and communicate through durable Temporal workflows. Game state (conditions, character sheets, session snapshots) is persisted in PostgreSQL.

## Architecture

- **NanoClaw** — lightweight agent runtime (~3900 lines), one container per agent
- **Temporal** — durable workflow orchestration for turn sequencing and retry logic
- **Postgres** — game state: character conditions, sheets, campaign snapshots
- **OpenRouter** — LLM provider for all agents via `/add-opencode` skill

## Stack

| Service   | Port(s)       | Purpose                        |
|-----------|---------------|--------------------------------|
| NanoClaw  | 18789         | Web UI + agent host process    |
| Temporal  | 7233 / 8080   | Workflow server / UI           |
| Postgres  | 5432          | Game state persistence         |

## Getting Started

```bash
docker compose up -d
```

See `openspec/changes/rpg-v2/` for the full design and implementation plan.
