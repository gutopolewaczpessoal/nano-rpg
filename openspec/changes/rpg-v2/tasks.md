## 1. Repositório, Projeto e Infraestrutura Base

- [x] 1.1 Criar diretório `/home/augus/projects/nano-rpg/` como raiz do projeto
- [x] 1.2 Executar `git init` e criar `.gitignore` (node_modules, .env, data/, *.db, binários Go)
- [x] 1.3 Criar repositório no GitHub e adicionar como remote `origin`
- [x] 1.4 Criar `README.md` inicial com nome e descrição do projeto
- [x] 1.5 Criar `docker-compose.yml` com os três serviços: `nanoclaw`, `temporal` e `postgres` na rede `nano-rpg-net`
- [x] 1.6 Configurar volumes no compose: `./nanoclaw/data/` para o NanoClaw, porta 18789 (web UI), porta 7233+8080 (Temporal), porta 5432 (Postgres)
- [x] 1.7 Confirmar que `docker compose up` sobe os três serviços sem erros e a rede `nano-rpg-net` está criada
- [x] 1.8 Fazer primeiro commit e push para `main`

## 2. NanoClaw — Instalação e Configuração Base

- [x] 2.1 Clonar NanoClaw dentro de `/home/augus/projects/nano-rpg/` e rodar `bash nanoclaw.sh`
- [x] 2.2 Confirmar que a web UI sobe na porta padrão e o processo host está rodando sem erros
- [x] 2.3 Criar grupo de agente `mestre` via NanoClaw
- [x] 2.4 Criar grupo de agente `zoe` via NanoClaw
- [x] 2.5 Criar grupo de agente `rafael` via NanoClaw
- [x] 2.6 Confirmar que os três diretórios de grupo existem com `container.json` e `CLAUDE.local.md`

## 3. OpenRouter — Configuração e Validação

- [x] 3.1 Registrar chave de API do OpenRouter no Agent Vault do NanoClaw
- [x] 3.2 Instalar skill `/add-opencode` no grupo `mestre`
- [x] 3.3 Instalar skill `/add-opencode` no grupo `zoe`
- [x] 3.4 Instalar skill `/add-opencode` no grupo `rafael`
- [x] 3.5 Configurar `OPENCODE_PROVIDER=openrouter` e `OPENCODE_MODEL` em cada `container.json`
- [x] 3.6 Enviar mensagem de teste para o Mestre e confirmar resposta via OpenRouter nos logs
- [x] 3.7 Enviar mensagem de teste para Zoe e confirmar resposta via OpenRouter
- [x] 3.8 Enviar mensagem de teste para Rafael e confirmar resposta via OpenRouter
- [x] 3.9 Reiniciar container de um agente e confirmar que contexto anterior é preservado
- [x] 3.10 Commit e push — sessão 3 completa e validada ✓

## 4. Temporal — Worker Go

- [ ] 4.1 Confirmar que Temporal UI (porta 8080) está acessível e o server responde na porta 7233
- [ ] 4.2 Instalar Go no ambiente de desenvolvimento
- [ ] 4.3 Criar módulo Go em `worker/` com dependências `go.temporal.io/sdk` e `lib/pq`

## 5. cli.sock — Investigação e Validação (crítico)

- [ ] 5.1 Localizar o `cli.sock` do NanoClaw após a instalação
- [ ] 5.2 Conectar ao socket com `socat` ou script Python e enviar mensagem JSON básica
- [ ] 5.3 Mapear o `platformId` correto para rotear mensagem ao grupo `zoe`
- [ ] 5.4 Confirmar que a resposta de Zoe volta pelo mesmo socket
- [ ] 5.5 Documentar o formato exato de roteamento (input/output) para usar no worker Go

## 6. Temporal Worker — Implementação

- [ ] 6.1 Implementar `RPGTurnWorkflow` em Go (recebe `character` + `context`, executa 3 activities em sequência)
- [ ] 6.2 Implementar `EnrichContextActivity` — stub que retorna o contexto sem modificar (Postgres vem depois)
- [ ] 6.3 Implementar `InvokeCharacterActivity` — conecta ao `cli.sock`, envia mensagem para o personagem correto, aguarda resposta
- [ ] 6.4 Implementar `UpdateStateActivity` — stub que loga o evento sem gravar (Postgres vem depois)
- [ ] 6.5 Compilar o worker Go como binário
- [ ] 6.6 Montar o binário do worker no container do Mestre via `container.json`
- [ ] 6.7 Montar o binário `temporal` CLI no container do Mestre via `container.json`
- [ ] 6.8 Configurar entrypoint do container do Mestre para subir o worker em background antes do Claude Code
- [ ] 6.9 Confirmar que o worker aparece como ativo na Temporal UI (task queue `rpg-tasks`)
- [ ] 6.10 Validar acesso ao `cli.sock` de dentro do container do Mestre: exec no container + script de teste que envia mensagem para Zoe e confirma resposta pelo socket (mesmo teste do grupo 5, mas agora de dentro do container)
- [ ] 6.11 Validar que o Temporal server é alcançável de dentro do container do Mestre: `temporal workflow list --address temporal:7233`

## 7. Integração Mestre → Temporal → Personagem (fim a fim)

- [ ] 7.1 No `CLAUDE.local.md` do Mestre, instruir o agente a usar `temporal workflow execute` para invocar personagens
- [ ] 7.2 Testar manualmente: Mestre executa `temporal workflow execute` para Zoe via Bash tool
- [ ] 7.3 Confirmar que o workflow aparece na Temporal UI, executa as 3 activities, e retorna a resposta de Zoe
- [ ] 7.4 Testar o mesmo fluxo para Rafael
- [ ] 7.5 Confirmar que se o container de Zoe reiniciar durante o workflow, o Temporal retenta e completa
- [ ] 7.6 Commit e push — sessão 2 completa e validada ✓

## 8. Postgres — Schema e Migrations

- [ ] 8.1 Escrever migration `001_init.sql` — tabelas `characters`, `campaigns`
- [ ] 8.3 Escrever migration `002_conditions.sql` — tabelas `character_conditions`, função `advance_campaign_day`
- [ ] 8.4 Escrever migration `003_scenes.sql` — tabelas `scenes`, `campaign_snapshots`
- [ ] 8.5 Executar migrations e confirmar que todas as tabelas existem com `\dt`
- [ ] 8.6 Escrever seed com a campanha inicial e fichas de Zoe e Rafael (`sheet` JSONB com hp, attributes, inventory)

## 9. Estado do Jogo — Wiring no Worker

- [ ] 9.1 Conectar `EnrichContextActivity` ao Postgres: buscar `sheet` e condições ativas do personagem
- [ ] 9.2 Formatar o payload enriquecido com seção "SEU ESTADO ATUAL" quando houver condições ativas
- [ ] 9.3 Conectar `UpdateStateActivity` ao Postgres: inserir registro em `scenes`
- [ ] 9.4 Implementar `add_condition` no worker (inserir em `character_conditions`)
- [ ] 9.5 Testar: adicionar condição "envenenado" para Zoe → confirmar que aparece no próximo contexto enviado a ela
- [ ] 9.6 Testar: `advance_campaign_day` → confirmar que condição com `heals_on_day` atingido expira
- [ ] 9.7 Implementar `save_snapshot` no worker (inserir em `campaign_snapshots`)
- [ ] 9.8 Testar: gravar snapshot → recuperar na próxima sessão
- [ ] 9.9 Commit e push — sessão 3 completa e validada ✓

## 10. Identidades dos Agentes

- [ ] 10.1 Escrever `SOUL.md` do Mestre (narrador, tom, regras de narrativa, quando invocar personagens)
- [ ] 10.2 Escrever `SOUL.md` de Zoe (personalidade, histórico, tom de fala)
- [ ] 10.3 Escrever `SOUL.md` de Rafael (personalidade, histórico, tom de fala — distinto de Zoe)
- [ ] 10.4 Criar skill `rpg-response` para Zoe e Rafael (responder em primeira pessoa, não quebrar personagem)
- [ ] 10.5 Criar skill `rpg-session` para o Mestre (fluxo de turno: invocar → aguardar → compor narração)
- [ ] 10.6 Testar Zoe com 5 mensagens variadas — confirmar voz consistente
- [ ] 10.7 Testar Rafael com 5 mensagens variadas — confirmar voz consistente e distinta de Zoe
- [ ] 10.8 Testar Zoe com condição ativa — confirmar que o comportamento muda
- [ ] 10.9 Executar turno completo fim a fim: jogador → Mestre → Zoe → Rafael → narração composta → jogador
- [ ] 10.10 Commit e push — sessão 4 completa e validada ✓
