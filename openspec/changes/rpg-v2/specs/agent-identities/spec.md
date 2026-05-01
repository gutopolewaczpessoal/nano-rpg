## ADDED Requirements

### Requirement: Mestre tem identidade de narrador
O Mestre SHALL ter um `SOUL.md` que define seu papel como narrador da história: descreve o ambiente, propõe situações, decide quais personagens reagem e os invoca via Temporal, e compõe a narração final com as respostas dos personagens.

#### Scenario: Mestre narra sem controlar personagens
- **WHEN** o jogador descreve uma ação
- **THEN** o Mestre descreve o cenário e as consequências, mas não fala em nome de Zoe ou Rafael diretamente — invoca-os via Temporal para que respondam com sua própria voz

#### Scenario: Mestre decide quem reage
- **WHEN** uma ação do jogador é relevante para um ou mais personagens
- **THEN** o Mestre decide (com base no contexto) quais personagens invocar, e executa `temporal workflow execute` para cada um antes de compor a narração final

---

### Requirement: Zoe tem personalidade distinta e consistente
Zoe SHALL ter um `SOUL.md` com personalidade, histórico e tom de fala definidos, mantendo voz consistente em todas as respostas durante a campanha.

#### Scenario: Zoe mantém tom em 5 mensagens consecutivas
- **WHEN** Zoe recebe 5 mensagens de teste variadas
- **THEN** todas as respostas mantêm o mesmo tom, vocabulário e traços de personalidade definidos no SOUL.md

---

### Requirement: Rafael tem personalidade distinta e consistente
Rafael SHALL ter um `SOUL.md` com personalidade, histórico e tom de fala definidos, distintos dos de Zoe e do Mestre.

#### Scenario: Rafael mantém tom em 5 mensagens consecutivas
- **WHEN** Rafael recebe 5 mensagens de teste variadas
- **THEN** todas as respostas mantêm o mesmo tom e personalidade definidos no SOUL.md, distinguíveis das respostas de Zoe

---

### Requirement: Personagens consideram seu estado atual ao responder
Zoe e Rafael SHALL adaptar seu comportamento e tom de fala com base nas condições ativas recebidas no contexto da mensagem (ex: envenenado, exausto, cego).

#### Scenario: Personagem com condição física responde diferente
- **WHEN** Zoe recebe uma mensagem com contexto indicando que está envenenada
- **THEN** a resposta de Zoe reflete o estado (ex: fala mais devagar, menciona desconforto, age com limitação)

#### Scenario: Personagem sem condição responde normalmente
- **WHEN** Rafael recebe uma mensagem sem condições ativas no contexto
- **THEN** Rafael responde com seu tom normal, sem mencionar limitações

---

### Requirement: Skill `rpg-response` em Zoe e Rafael
Zoe e Rafael SHALL ter a skill `rpg-response` instalada, que instrui o agente a responder apenas em primeira pessoa como o personagem, sem quebrar o personagem ou comentar sobre o sistema.

#### Scenario: Personagem não quebra o personagem
- **WHEN** o jogador faz uma pergunta fora da narrativa (ex: "você é uma IA?")
- **THEN** Zoe ou Rafael respondem dentro do universo do jogo, sem reconhecer serem agentes de IA

---

### Requirement: Skill `rpg-session` no Mestre
O Mestre SHALL ter a skill `rpg-session` instalada, que instrui o agente sobre o fluxo de um turno: ler o contexto, decidir personagens, invocar via Temporal, aguardar, e compor narração final.

#### Scenario: Mestre segue o fluxo de turno completo
- **WHEN** o jogador descreve uma ação que afeta dois personagens
- **THEN** o Mestre invoca os dois via Temporal (em sequência), aguarda ambas as respostas, e entrega uma narração composta ao jogador
