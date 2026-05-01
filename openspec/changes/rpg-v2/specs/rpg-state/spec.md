## ADDED Requirements

### Requirement: Schema Postgres com tabelas de estado do jogo
O Postgres SHALL ter as tabelas `characters`, `character_conditions`, `campaigns`, `scenes` e `campaign_snapshots` criadas via migration versionada antes de qualquer gravação de dados.

#### Scenario: Migrations executadas com sucesso
- **WHEN** o docker compose sobe pela primeira vez
- **THEN** todas as tabelas existem no banco e `\dt` lista pelo menos: characters, character_conditions, campaigns, scenes, campaign_snapshots

---

### Requirement: Fichas dos personagens armazenadas como JSONB
Cada personagem SHALL ter uma ficha completa armazenada na coluna `sheet` (JSONB) da tabela `characters`, contendo atributos, HP, inventário e quaisquer outros campos do sistema de jogo.

#### Scenario: Ficha recuperada com todos os campos
- **WHEN** `EnrichContextActivity` busca a ficha de um personagem
- **THEN** o JSONB retornado contém pelo menos: `hp`, `max_hp`, `attributes` e `inventory`

---

### Requirement: Condições físicas e emocionais registradas por personagem
O sistema SHALL permitir registrar condições ativas (ex: sangrando, envenenado, exausto, cego, braço fraturado) para qualquer personagem, com tipo, descrição, severidade e dia de início.

#### Scenario: Condição adicionada e recuperada
- **WHEN** uma condição é inserida para um personagem via `UpdateStateActivity`
- **THEN** a condição aparece em `character_conditions` com `is_active = true` e é retornada pela próxima `EnrichContextActivity` para esse personagem

#### Scenario: Condição com cura automática expira
- **WHEN** `advance_campaign_day` é chamada e o `heals_on_day` de uma condição foi atingido
- **THEN** a condição tem `is_active` atualizado para `false` automaticamente

---

### Requirement: Condições ativas são injetadas no contexto antes de cada resposta
A `EnrichContextActivity` SHALL incluir todas as condições ativas do personagem no payload enviado ao agente NanoClaw, de forma estruturada e legível pelo LLM.

#### Scenario: Payload com condições formatado corretamente
- **WHEN** Zoe tem duas condições ativas (ex: envenenada + exausta)
- **THEN** o payload entregue ao container de Zoe contém uma seção "SEU ESTADO ATUAL" listando ambas as condições com descrição e severidade

---

### Requirement: Log narrativo de cenas gravado
Cada turno completo SHALL gerar um registro na tabela `scenes` com o personagem, o contexto enviado e a resposta recebida, formando o log narrativo da campanha.

#### Scenario: Cena gravada após turno completo
- **WHEN** `UpdateStateActivity` é chamada com os dados do turno
- **THEN** um registro é inserido em `scenes` com `campaign_id`, `character_name`, `context` e `response`

---

### Requirement: Snapshots de campanha como save points
O Mestre SHALL poder gravar um snapshot da campanha (save do jogo) com um resumo narrativo do estado atual, recuperável na próxima sessão.

#### Scenario: Snapshot gravado pelo Mestre
- **WHEN** o Mestre chama a tool de save com um resumo
- **THEN** um registro é inserido em `campaign_snapshots` com `game_day` e `summary`

#### Scenario: Último snapshot recuperado no início da sessão
- **WHEN** o Mestre inicia uma nova sessão e consulta o último save
- **THEN** recebe o snapshot mais recente com `game_day` e `summary` para retomar a narrativa
