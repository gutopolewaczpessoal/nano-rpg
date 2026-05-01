## ADDED Requirements

### Requirement: Repositório Git criado e publicado
O projeto rpg-v2 SHALL existir como repositório Git em `/home/augus/projects/rpg-v2/` com remote no GitHub, contendo pelo menos um commit inicial antes de qualquer instalação de dependência.

#### Scenario: Repositório inicializado e publicado
- **WHEN** a sessão 1 começa
- **THEN** existe um diretório `/home/augus/projects/rpg-v2/` com `.git/` inicializado, remote `origin` apontando para GitHub, e pelo menos um commit visível em `git log`

---

### Requirement: NanoClaw instalado no projeto
O NanoClaw SHALL estar instalado e operacional em `/home/augus/projects/rpg-v2/`, com o processo host rodando e acessível via web UI na porta padrão.

#### Scenario: NanoClaw respondendo
- **WHEN** o NanoClaw é iniciado via `docker compose up` ou equivalente
- **THEN** a web UI está acessível e o processo host está rodando sem erros nos logs

---

### Requirement: Três grupos de agentes criados
O NanoClaw SHALL ter três grupos de agentes configurados: `mestre`, `zoe` e `rafael`, cada um com seu próprio workspace e container isolado.

#### Scenario: Grupos criados e listáveis
- **WHEN** os grupos são criados via NanoClaw
- **THEN** existem três diretórios de grupo distintos (mestre, zoe, rafael) com `container.json` e `CLAUDE.local.md` em cada um

---

### Requirement: OpenRouter configurado em todos os agentes via /add-opencode
Todos os três agentes (mestre, zoe, rafael) SHALL usar OpenRouter como provedor de LLM, configurado via skill `/add-opencode` do NanoClaw.

#### Scenario: Skill opencode instalado
- **WHEN** `/add-opencode` é executado para cada grupo
- **THEN** o `container.json` de cada grupo contém `"provider": "opencode"` com variáveis `OPENCODE_PROVIDER=openrouter` e `OPENCODE_MODEL` definidas

#### Scenario: Chave OpenRouter registrada no Agent Vault
- **WHEN** a chave de API do OpenRouter é registrada
- **THEN** o Agent Vault injeta a credencial em trânsito e os containers não recebem a chave em texto plano

---

### Requirement: Todos os agentes respondem via OpenRouter
Cada um dos três agentes SHALL responder a uma mensagem de teste simples usando o modelo OpenRouter configurado, confirmando que o pipeline completo funciona antes de qualquer lógica de RPG.

#### Scenario: Mestre responde via OpenRouter
- **WHEN** o jogador envia "Olá" para o Mestre via web UI ou terminal
- **THEN** o Mestre retorna uma resposta em texto, e os logs indicam que a chamada foi roteada pelo OpenRouter

#### Scenario: Zoe responde via OpenRouter
- **WHEN** uma mensagem de teste é enviada para Zoe
- **THEN** Zoe retorna uma resposta e os logs confirmam uso do OpenRouter

#### Scenario: Rafael responde via OpenRouter
- **WHEN** uma mensagem de teste é enviada para Rafael
- **THEN** Rafael retorna uma resposta e os logs confirmam uso do OpenRouter

---

### Requirement: Sessões persistem entre reinicializações
O histórico de conversa de cada agente SHALL sobreviver a reinicializações do container NanoClaw, sem perda de contexto.

#### Scenario: Contexto preservado após restart
- **WHEN** o container de um agente é reiniciado
- **THEN** o agente responde considerando o histórico anterior da sessão (ex: lembra de algo dito antes do restart)
