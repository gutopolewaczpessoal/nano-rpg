## Why

O v1 do rpg-agent nunca saiu do papel por dois motivos: a orquestração entre agentes do OpenClaw não funcionava na prática, e a integração com OpenRouter era instável. O v2 reconstrói o projeto do zero sobre NanoClaw (runtime leve, ~3900 linhas) e Temporal (orquestração durável), com cada camada sendo validada de forma independente antes de avançar.

## What Changes

- **Novo projeto** criado em `/home/augus/projects/rpg-v2/` (não é um refactor do rpg-agent), inicializado como repositório Git e publicado no GitHub desde o primeiro commit
- **NanoClaw** substitui OpenClaw como runtime dos agentes — 3 containers isolados (Mestre, Zoe, Rafael)
- **OpenRouter** como provedor de LLM para todos os agentes via skill `/add-opencode`
- **Temporal** (Go worker) substitui `sessions_spawn` como mecanismo de orquestração entre agentes
- **MCP server removido** do Mestre — Claude Code usa `Bash` tool para disparar `temporal workflow execute`
- **Postgres** mantido para estado do jogo (condições, fichas, snapshots), sem pgvector
- Personagens têm sessões persistentes via SQLite do NanoClaw (histórico de campanha sobrevive restarts)
- Estado de condições (sangrando, envenenado, etc.) é injetado no contexto pelo Temporal worker antes de entregar mensagem ao personagem

## Capabilities

### New Capabilities

- `nanoclaw-setup`: Instalação do NanoClaw, configuração do OpenRouter via `/add-opencode` para os 3 agentes (Mestre, Zoe, Rafael), validação de que todos respondem via OpenRouter antes de qualquer identidade ou lógica de RPG
- `temporal-orchestration`: Worker Go com `RPGTurnWorkflow` e activities (`EnrichContext`, `InvokeCharacter`, `UpdateState`); Mestre dispara workflows via `temporal workflow execute` na Bash tool; worker roda como processo background no container do Mestre
- `agent-identities`: SOUL.md e CLAUDE.md de cada agente com personalidade, tom e regras de comportamento; skill `rpg-response` para Zoe e Rafael; skill `rpg-session` para o Mestre
- `rpg-state`: Schema Postgres (characters, character_conditions, campaigns, scenes, snapshots); Go activities lendo e gravando estado; condições ativas injetadas no contexto de cada personagem pelo worker

### Modified Capabilities

## Impact

- **Novo repositório:** `/home/augus/projects/rpg-v2/`
- **Dependências novas:** NanoClaw, Temporal server (Docker), Go (worker), PostgreSQL 16
- **Removido:** OpenClaw, pgvector, plugin memory-postgres, sessions_spawn
- **NanoClaw container.json:** precisa de skill `/add-opencode` + mount do `temporal` binary para o container do Mestre
- **Temporal worker:** binário Go compilado, task queue `rpg-tasks`, rodando no container do Mestre como sidecar
