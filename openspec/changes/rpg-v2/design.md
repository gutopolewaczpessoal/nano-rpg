## Context

O v1 (rpg-agent) foi construído sobre OpenClaw e nunca chegou à Fase 4 (orquestração entre agentes). Dois bloqueadores concretos: o mecanismo `sessions_spawn` do OpenClaw não funcionou na prática, e a integração com OpenRouter era instável. O v2 é um projeto novo em `/home/augus/projects/nano-rpg/`, construído sobre NanoClaw (runtime leve, ~3900 linhas, baseado em Claude Code SDK) e Temporal (orquestração durável em Go).

O jogador interage com o Mestre via interface web do NanoClaw ou terminal. O Mestre narra, decide quais personagens reagem, e os invoca via Temporal. Os personagens (Zoe, Rafael) processam em seus próprios containers e retornam respostas ao workflow, que as entrega de volta ao Mestre.

## Infraestrutura — Docker Compose

Toda a infraestrutura é gerenciada por um único `docker-compose.yml` na raiz do projeto. O NanoClaw precisa do Docker socket montado para spawnar containers de agentes dinamicamente.

```
docker-compose.yml
├── nanoclaw        Node.js host process, porta 18789 (web UI)
│                   monta /var/run/docker.sock para spawnar agentes
│                   monta ./nanoclaw/data/ para persistência (SQLite, cli.sock)
├── temporal        Temporal server, porta 7233 (gRPC) + 8080 (UI)
└── postgres        Postgres 16, porta 5432
```

Os containers de agentes (mestre, zoe, rafael) são spawnados dinamicamente pelo NanoClaw host via Docker daemon — não aparecem no compose, mas precisam estar na mesma rede Docker para alcançar `temporal:7233` e `postgres:5432`.

**Rede:** todos os serviços do compose e os containers spawnados pelo NanoClaw usam a rede `nano-rpg-net` (bridge). O NanoClaw configura a rede dos containers de agentes via `container.json` de cada grupo.

```
nano-rpg-net (bridge)
├── nanoclaw        → expõe cli.sock via volume compartilhado
├── temporal        → acessível em temporal:7233
├── postgres        → acessível em postgres:5432
├── container-mestre  (spawnado pelo NanoClaw)
│     worker Go em background
│     cli.sock montado de ./nanoclaw/data/cli.sock
│     temporal CLI apontando para temporal:7233
├── container-zoe     (spawnado pelo NanoClaw)
└── container-rafael  (spawnado pelo NanoClaw)
```

**Volumes relevantes:**
- `./nanoclaw/data/` → montado no NanoClaw host e também no container do Mestre (para acesso ao `cli.sock`)
- `./worker/rpg-worker` → binário Go montado no container do Mestre
- `./temporal-cli` → binário `temporal` montado no container do Mestre

## Goals / Non-Goals

**Goals:**
- 3 agentes NanoClaw (Mestre, Zoe, Rafael) rodando via OpenRouter desde o primeiro dia
- Orquestração durável via Temporal: o Mestre invoca personagens, aguarda respostas, compõe narração
- Estado do jogo persistido em Postgres: condições físicas/emocionais, fichas, snapshots
- Contexto de estado injetado pelo worker antes de cada entrega ao personagem
- Sessões persistentes: histórico de campanha sobrevive reinicializações de container
- Repositório Git publicado no GitHub desde o primeiro commit

**Non-Goals:**
- Interface web própria (usa a do NanoClaw)
- Memória semântica / busca vetorial (pgvector removido)
- Agentes autônomos que iniciam ações sem input do jogador
- Multi-campanha (uma campanha por vez)
- Deploy em cloud

## Decisions

### 1. NanoClaw como runtime dos agentes
**Escolha:** NanoClaw sobre OpenClaw.
**Razão:** ~3900 linhas vs 434k — modificável quando necessário. Suporta Claude Code SDK em containers Docker isolados com estado persistido em SQLite. Filosofia "modifique direto" alinha com o projeto.
**Alternativa descartada:** OpenClaw — complexidade de configuração impraticável, OpenRouter instável.

### 2. OpenRouter para todos os agentes via `/add-opencode`
**Escolha:** Skill `/add-opencode` do NanoClaw em todos os 3 containers.
**Razão:** Único caminho suportado para OpenRouter no NanoClaw. Provider configurado por `container.json` de cada grupo — cada agente pode usar um modelo diferente.
**Alternativa descartada:** `ANTHROPIC_BASE_URL` — menos testado, Agent Vault pode interceptar de forma incompatível.

### 3. Temporal para orquestração entre agentes
**Escolha:** Temporal (Go SDK) com `RPGTurnWorkflow` e activities.
**Razão:** Execução durável — se o container reiniciar no meio de um turno, o workflow retoma. Visibilidade no Temporal UI. Retry automático em caso de falha de container.
**Alternativa descartada:** `sessions_spawn` nativo do OpenClaw — era o bloqueador do v1. CLI direto sem Temporal — sem durabilidade nem visibilidade.

### 4. Worker Temporal no container do Mestre
**Escolha:** Go worker roda como processo background no mesmo container do Mestre.
**Razão:** O Mestre usa a Bash tool do Claude Code para rodar `temporal workflow execute` (bloqueante). O worker no mesmo container pega o task localmente. Não precisa de HTTP endpoint ou MCP server adicional.
**Alternativa descartada:** Worker no host — acoplamento com o ambiente local, mais difícil de dockerizar. Worker por agente (Zoe, Rafael) — complexidade desnecessária: personagens só reagem, nunca iniciam.

### 5. `temporal workflow execute` como bridge Mestre → Temporal
**Escolha:** Mestre roda `temporal workflow execute --workflow-type RPGTurnWorkflow --input '...'` via Bash tool.
**Razão:** Nativo no CLI do Temporal. Bloqueante: inicia o workflow e aguarda o resultado na stdout. Não precisa de MCP server, SDK, ou endpoint HTTP.
**Alternativa descartada:** MCP server que chama Temporal SDK — peça adicional desnecessária.

### 6. Comunicação worker → agentes de personagem via `cli.sock`
**Escolha:** Worker conecta em `data/cli.sock` do NanoClaw (socket Unix bidirecional, protocolo JSON).
**Razão:** API pública do NanoClaw para injeção de mensagens. Resposta volta pelo mesmo socket quando o container processa.
**Risco:** Formato exato de `platformId` para roteamento precisa ser validado na sessão 1.
**Alternativa de fallback:** Escrita direta em `inbound.db` / leitura de `outbound.db` — funciona mas acopla com internals.

### 7. Enriquecimento de contexto antes da entrega
**Escolha:** `EnrichContextActivity` no worker busca condições + ficha no Postgres e injeta no payload antes de enviar para o personagem.
**Razão:** Elimina dependência de o agente lembrar de chamar uma tool para saber seu próprio estado. O personagem sempre recebe seu estado atual no contexto da mensagem.

### 8. Postgres sem pgvector
**Escolha:** Postgres 16, sem extensão vetorial.
**Razão:** Estado do jogo não precisa de busca semântica — condições e fichas são consultadas por ID. Remove dependência e complexidade de embeddings.
**Futuro:** pgvector pode entrar como migration se memória semântica for necessária.

## Risks / Trade-offs

- **`cli.sock` platformId desconhecido** → Testar na sessão 1 antes de qualquer código Temporal. Fallback: escrita direta no inbound.db.
- **OpenCode provider no container** → Comportamento com Claude Code SDK pode diferir do esperado. Validar na sessão 1 com mensagem simples antes de avançar.
- **`temporal` binary no container do Mestre** → Precisa de mount via `container.json`. Se o NanoClaw não suportar mount de binários arbitrários, alternativa é instalar via packages do container.
- **Worker como sidecar no container** → NanoClaw não tem suporte nativo a processos background no container. Solução: script de entrypoint customizado que sobe o worker antes do Claude Code. Requer fork leve ou `container.json` com setup hook.
- **Latência de turno** → 3 LLMs em sequência pode levar 30-60s. Mitigação futura: paralelizar Zoe e Rafael quando o Mestre os invocar independentemente.

## Open Questions

- Qual é o `platformId` exato para rotear mensagem para um agente específico via `cli.sock`? (validar na sessão 1)
- O NanoClaw suporta processo background (worker Go) no mesmo container sem modificação? Ou precisa de entrypoint customizado?
- O `/add-opencode` skill funciona corretamente com o Agent Vault para todos os modelos do OpenRouter?
