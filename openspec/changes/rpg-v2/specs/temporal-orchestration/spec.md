## ADDED Requirements

### Requirement: Temporal server acessível
Um servidor Temporal SHALL estar rodando como container Docker, acessível pelo worker Go e pelo container do Mestre.

#### Scenario: Temporal server operacional
- **WHEN** o docker compose sobe
- **THEN** o Temporal server responde na porta 7233 e a Temporal UI está acessível na porta 8080

---

### Requirement: Worker Go compilado e rodando no container do Mestre
Um worker Temporal em Go SHALL rodar como processo background no container do Mestre, registrado na task queue `rpg-tasks`, pronto para executar workflows antes do Mestre ser iniciado.

#### Scenario: Worker registrado e aguardando tasks
- **WHEN** o container do Mestre sobe
- **THEN** o worker Go está rodando em background e aparece como worker ativo na Temporal UI, registrado em `rpg-tasks`

---

### Requirement: Mestre invoca personagem via `temporal workflow execute`
O Mestre SHALL poder invocar um personagem usando a Bash tool para rodar `temporal workflow execute`, bloqueando até receber a resposta do personagem.

#### Scenario: Invocação síncrona de personagem
- **WHEN** o Mestre executa `temporal workflow execute --workflow-type RPGTurnWorkflow --task-queue rpg-tasks --input '{"character":"zoe","context":"..."}'`
- **THEN** o comando bloqueia, o workflow executa, e o resultado (resposta de Zoe) é retornado na stdout

---

### Requirement: RPGTurnWorkflow orquestra a resposta do personagem
O `RPGTurnWorkflow` SHALL executar três activities em sequência: enriquecer contexto com estado do Postgres, invocar o personagem via NanoClaw, e gravar o evento no Postgres.

#### Scenario: Workflow completo end-to-end
- **WHEN** `RPGTurnWorkflow` é iniciado com `character` e `context`
- **THEN** o workflow executa `EnrichContextActivity`, depois `InvokeCharacterActivity`, depois `UpdateStateActivity`, e retorna a resposta do personagem ao chamador

---

### Requirement: EnrichContextActivity injeta estado do personagem
A `EnrichContextActivity` SHALL buscar no Postgres as condições ativas e a ficha do personagem, e retornar um contexto enriquecido para ser entregue junto com a mensagem.

#### Scenario: Contexto enriquecido com condições ativas
- **WHEN** `EnrichContextActivity` é executada para um personagem com condições ativas
- **THEN** o contexto retornado inclui as condições (ex: "envenenado", "braço fraturado") e a ficha atual do personagem

#### Scenario: Contexto sem condições
- **WHEN** `EnrichContextActivity` é executada para um personagem sem condições ativas
- **THEN** o contexto retornado inclui apenas a ficha do personagem, sem seção de condições

---

### Requirement: InvokeCharacterActivity entrega mensagem ao agente NanoClaw e aguarda resposta
A `InvokeCharacterActivity` SHALL conectar ao `cli.sock` do NanoClaw, enviar a mensagem enriquecida para o container do personagem correto, e aguardar a resposta pelo mesmo socket.

#### Scenario: Mensagem entregue e resposta recebida
- **WHEN** `InvokeCharacterActivity` é executada para "zoe" com um contexto
- **THEN** a mensagem aparece no container de Zoe, Zoe processa e responde, e a activity retorna o texto da resposta

#### Scenario: Timeout se personagem não responde
- **WHEN** o container do personagem não responde dentro do timeout configurado
- **THEN** a activity falha com erro de timeout e o Temporal aplica a política de retry

---

### Requirement: UpdateStateActivity grava evento no Postgres
A `UpdateStateActivity` SHALL gravar no Postgres um registro do evento ocorrido (personagem, contexto, resposta) para manter o log narrativo da campanha.

#### Scenario: Evento gravado após resposta
- **WHEN** `UpdateStateActivity` é executada com a resposta do personagem
- **THEN** um registro é inserido na tabela `scenes` do Postgres com personagem, contexto e resposta

---

### Requirement: Workflow retoma após falha de container
Se um container NanoClaw reiniciar durante a execução de um workflow, o Temporal SHALL retentar a activity após a recuperação do container, sem perder o turno.

#### Scenario: Retry automático após restart de container
- **WHEN** o container de Zoe reinicia durante `InvokeCharacterActivity`
- **THEN** o Temporal retenta a activity após o container voltar, e o workflow completa normalmente
