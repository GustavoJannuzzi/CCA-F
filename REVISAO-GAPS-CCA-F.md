# Revisão de Gaps — Material CCA-F (perspectiva: usuário de Claude Code que nunca desenvolveu agente)

> **Como ler este documento.** Para cada tópico dou um **veredito** e, quando há gap,
> aponto **o que falta** (ONDE vive / QUANDO é usado / COMO parece na prática) e **como melhorar**.
> Vereditos: ✅ suficiente · ⚠️ gap (falta contexto de "onde/quando/como") · ❌ gap crítico (imprecisão factual ou conceito assumido).
>
> Verificado contra a documentação oficial da Anthropic (Claude Code, Agent SDK, Messages API) em 2026-07-02.

---

## 0. O gap transversal (vale para os 5 domínios)

O material ensina muito bem **O QUÊ** e o **julgamento de prova** (qual alternativa marcar e por quê as outras falham). O que ele quase nunca faz é dizer **em qual "plano" cada coisa vive**. Para quem só usou Claude Code como usuário, esse é o buraco que faz conceitos parecerem abstratos.

Existem **três planos**, e o exame mistura os três sem avisar:

| Plano | O que é | Quem escreve o quê | Conceitos que vivem aqui |
|---|---|---|---|
| **Claude API crua** (Messages API) | Endpoint HTTP **stateless**. Você escreve o loop na mão. | Dev escreve o loop, define tools (schema), reenvia histórico | `messages`, `stop_reason`, `tool_use`/`tool_result`, `tool_choice`, `is_error`, `input_schema`, **Batches API**, `custom_id` |
| **Claude Agent SDK** (ex-"Claude Code SDK") | Framework que **roda o loop por você**. Python `claude-agent-sdk`, TS `@anthropic-ai/claude-agent-sdk`. | Dev define agentes, tools, hooks; o SDK executa | Coordinator/subagents, `Task`/`Agent` tool, `allowedTools`, **hooks** (`PreToolUse`/`PostToolUse`…), orquestração multi-agente |
| **Claude Code CLI** | O terminal que você já usa. **Construído em cima do mesmo motor do Agent SDK.** | Dev escreve arquivos de config; o modelo age | `CLAUDE.md`, `@import`, `.claude/commands`, `.claude/skills`, `.claude/rules`, `.claude/agents`, `.mcp.json`, plan mode, `/compact`, `-p`, `--resume`, hooks em `settings.json` |

**O "aha" que o material nunca diz explicitamente:**

1. **Claude Code É um agente construído sobre o Agent SDK.** Por isso hooks, subagents, MCP, skills e CLAUDE.md existem **nos dois mundos** — num como *arquivo de configuração* (Code), no outro como *código/opção* (SDK). O que você já faz no terminal é a versão "config" do que um dev de agente faz em código.
2. **O "loop agêntico" (Domínio 1) você só escreve na mão na API crua.** No Agent SDK e no Claude Code o loop já está pronto — você nunca vê `stop_reason`. Os "anti-padrões de terminação" só acontecem quando alguém constrói na API crua.
3. **Quem decide o quê:** o **desenvolvedor** define tools, prompts, hooks e config; o **modelo** decide qual tool chamar e emite `tool_use`; o **runtime** (SDK/Code) — ou o **seu código** (API crua) — executa a tool e devolve o resultado ao loop.

> **Sugestão de melhoria global:** abrir a apostila (e cada módulo) com esse quadro dos três planos e, em cada tópico, marcar com um selo **[API]**, **[SDK]** ou **[Code]** onde aquilo vive. Resolve ~70% dos gaps de uma vez.

---

## Domínio 1 — Agentic Architecture & Orchestration (27%)

### 1.1 Agentic Loop Lifecycle — ⚠️ gap (ONDE / QUEM / COMO)
**O material tem:** o loop `stop_reason` → `tool_use`/`end_turn`, tool results anexados à história, anti-padrões (parsear texto natural). Diagrama ASCII bom.

**O que falta:**
- **ONDE:** não diz que esse loop é **código que o dev escreve na API crua**. Para você (usuário de Claude Code), o loop é *invisível* — o Claude Code já o roda. O anti-padrão "if 'I've completed' in text" só existe quando alguém constrói o loop na mão.
- **COMO:** o diagrama é conceitual; falta ver o payload real do round-trip (assistant `tool_use` → user `tool_result`).
- **QUEM:** a API é **stateless** — é por isso que você reenvia o histórico inteiro a cada chamada. Isso não está dito aqui (aparece solto no Domínio 5).

**Como melhorar — adicionar caixa "Onde isso vive" + JSON real:**
```python
# [API crua] O loop é SEU código. A API não tem memória: você reenvia messages a cada volta.
resp = client.messages.create(model="claude-opus-4-8", max_tokens=1024,
                              tools=[get_customer_tool], messages=messages)

if resp.stop_reason == "tool_use":
    tool_call = resp.content[-1]          # {type:"tool_use", id:"toolu_..", name:"get_customer", input:{...}}
    result = run_get_customer(tool_call.input)          # VOCÊ executa a tool
    messages.append({"role": "assistant", "content": resp.content})
    messages.append({"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tool_call.id,
         "content": result, "is_error": False}
    ]})
    # ...e chama create() de novo (o loop continua)
elif resp.stop_reason == "end_turn":
    done(resp)
```
> Frase-âncora: *"No Claude Code e no Agent SDK esse loop já está implementado — você nunca escreve `stop_reason`. Ele importa quando você constrói na Messages API ou desenha um agente no SDK."*

---

### 1.2 Coordinator-Subagent (hub-and-spoke) — ⚠️ gap (ONDE / COMO)
**O material tem:** hub-and-spoke, contexto isolado dos subagents, responsabilidades do coordinator. Bom conceitualmente.

**O que falta:** "coordinator", "subagent", "hub-and-spoke" são vocabulário de dev de agente sem aterrissagem. Onde um coordinator "roda"? É **um agente** (SDK) cujas tools incluem `Task`; cada subagent é **outra config de agente**. No Claude Code isso vive em `.claude/agents/*.md`.

**Como melhorar:** mapear o abstrato para o concreto:
- **[SDK]** coordinator = agente com `allowedTools` incluindo `"Task"`; subagents = entradas na opção `agents={...}`.
- **[Code]** subagents = arquivos `.claude/agents/coordinator.md`, `.claude/agents/web-search.md`… "coordinator gerencia toda comunicação" significa, na prática, *só ele chama `Task` e lê os resultados*.

---

### 1.3 Subagent Invocation & Context Passing — ⚠️ gap + ❌ correção factual
**O material tem:** `Task` tool; `allowedTools` deve incluir `"Task"`; `AgentDefinition`; contexto passado explicitamente. **O ponto do `allowedTools` incluir `"Task"` está CORRETO** (é assim no SDK — bom!).

**Correção factual:** ❌ **`fork_session` não é o nome real.** O que existe:
- **`--fork-session`** (flag de CLI do Claude Code): ao usar `--resume`/`--continue`, cria um *novo* session id em vez de reusar o original.
- **`/fork`** (comando): cria um subagente que herda a conversa inteira.

**O que falta (COMO):** o snippet `task_tool.invoke(prompt=...)` é **pseudocódigo**. No SDK real você *define* os agentes e o **modelo** chama a `Task`; você raramente "invoca" a tool imperativamente. E "contexto passado explicitamente" precisa de dono: **o modelo-coordinator compõe o prompt da `Task`**, mas é o **dev** que instrui o coordinator a incluir os fatos do caso.

**Como melhorar:** trocar `fork_session` por `--fork-session`/`/fork`; mostrar um `.claude/agents/billing-investigator.md` real e deixar claro que "isolamento de contexto" = o subagent começa do zero, então os fatos (CUS-4829, ORD-789…) têm que estar no prompt da Task.

---

### 1.4 Multi-Step Workflows with Enforcement — ⚠️ gap + ❌ correção
**O material tem:** hooks (determinístico) vs prompt (probabilístico); tabela com "~88-95%".

**O que falta / corrigir:**
- Os números **88-95%** são **ilustrativos**, não oficiais — vale marcar como "ordem de grandeza".
- **ONDE:** "hook" aqui = hook do Agent SDK / Claude Code (evento + callback). No Code vive em `settings.json`; no SDK, nas options.
- ❌ Ver 1.5: o exemplo de *bloqueio* deveria ser **`PreToolUse`**, não `PostToolUse`.

---

### 1.5 Agent SDK Hooks — ❌ GAP CRÍTICO (factual)
**O material tem:** "`PostToolUse` hooks... podem bloquear reembolsos > $500 e redirecionar para escalada". Código `post_tool_use_hook(...)` retornando `{"blocked": True}`.

**Problema factual (confirmado na doc oficial):**
- **`PostToolUse` roda DEPOIS que a tool executou** — se `process_refund` já rodou, o dinheiro já saiu. Bloquear aí é tarde demais.
- Para **bloquear ANTES da execução** use **`PreToolUse`**, que pode **negar** a ação. O retorno real não é `{"blocked": True}`; é:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Reembolso > $500 requer aprovação humana"
  }
}
```
`permissionDecision` aceita `"allow"`, `"deny"`, `"ask"`, `"defer"`.

**Regra de ouro (a que o exame quer):**
- **`PreToolUse`** = *portão* — decide se a tool pode rodar (bloquear/gatekeeping). ← reembolso > $500, gate de verificação antes de operações financeiras.
- **`PostToolUse`** = *inspecionar/transformar o resultado* depois que a tool rodou. ← **é exatamente o uso CORRETO no Domínio 5** (aparar campos do `get_order_details`).

**Como melhorar:** reescrever o exemplo do reembolso como `PreToolUse` + retorno real; e deixar explícito o *timeline* (Pre = antes, Post = depois). Bônus: a mesma correção afeta o gabarito da **Prática 1** deste módulo (o "prerequisite gate" que bloqueia `lookup_order`/`process_refund` é conceitualmente `PreToolUse`).

---

### 1.6 Task Decomposition Strategies — ✅ suficiente (leve nota)
Conteúdo de julgamento (prompt chaining vs dinâmico; multi-pass review) está bom. **Leve gap:** clarificar *quem* orquestra — chaining pode ser **você codando a sequência** (fixa) vs decomposição dinâmica **decidida pelo coordinator/modelo**.

---

### 1.7 Session State Management — ⚠️ gap + ❌ correção
**O material tem:** `--resume`, `fork_session`, fresh start > resume, manifesto JSON para crash recovery.

**Corrigir / faltando:**
- ❌ `fork_session` → `--fork-session` / `/fork` (ver 1.3).
- **ONDE:** `--resume`/`--continue`/`--fork-session` são flags do **Claude Code CLI** (não da API). `--resume` e `--continue` (`-c`) são reais.
- **COMO/QUEM:** o **manifesto** (JSON de progresso) é um **padrão que VOCÊ inventa** (seu código escreve e lê), não uma feature embutida. Vale dizer isso — senão parece que existe um "manifest" nativo.

---

### Cenário & Práticas do Domínio 1
O cenário diz "Claude Agent SDK" — ótimo. Falta a ponte de que `get_customer`, `process_refund` etc. são **tools que o dev define e o modelo chama**; não são mágicas do SDK. E o gabarito da Prática 1 ("PostToolUse hook") herda a imprecisão de 1.5 → é `PreToolUse`.

---

## Domínio 2 — Tool Design & MCP Integration (18%)

### 2.1 Effective Tool Descriptions — ✅ suficiente (leve gap COMO)
Antes/depois e a "regra de ouro" (se dois colegas discordariam, a descrição está ruim) são excelentes. **Leve gap:** *onde* vive a "descrição"? É o campo `description` da definição da tool:
```python
get_customer_tool = {
    "name": "get_customer",
    "description": "Retrieves customer profile by ID (CUS-XXXX)... Use for... Do NOT use for...",
    "input_schema": {"type": "object", "properties": {...}, "required": [...]}
}
```
O **modelo lê esse campo no momento da seleção**. Mostrar isso conecta "descrição" a "onde ela mora".

---

### 2.2 Structured Error Responses — ⚠️ gap (❌ clarificação factual)
**O material tem:** flag `isError`; 4 categorias; `isRetryable`; empty result válido ≠ erro. Ótimo conteúdo de julgamento.

**Corrigir:** ❌ **só `isError` (booleano) é campo do protocolo MCP.** `errorCategory`, `isRetryable`, `alternatives`, `partialResults` **não são do protocolo** — são **convenção da sua aplicação** que o autor da tool coloca **dentro do `content`** do resultado. O material apresenta como se fossem padrão.

**O que falta (QUEM/ONDE):** quem *produz* esse JSON é a **implementação da tool / servidor MCP**; quem *consome* é o **modelo**, que lê o `content` e decide (retry vs escalar vs seguir). Mostrar que o JSON rico vai *dentro* do `tool_result.content`, com `is_error: true` sinalizando a falha.

---

### 2.3 Tool Distribution & tool_choice — ⚠️ gap (ONDE / QUEM)
**O material tem:** muitos tools degradam seleção; acesso escopado; os 3 modos de `tool_choice`. Os shapes estão **corretos**.

**O que falta:**
- **`tool_choice` é parâmetro da requisição da Messages API**, setado pelo **dev por chamada** — **não** é config de Claude Code. Mostrar:
```python
client.messages.create(..., tools=[...], tool_choice={"type": "tool", "name": "extract_invoice"})
```
- "Acesso escopado a tools" ↔ campo `tools` do agente (**[Code]** `.claude/agents/*.md` frontmatter `tools:`; **[SDK]** `allowedTools`). São coisas diferentes de `tool_choice` — vale separar as duas ideias.

---

### 2.4 MCP Server Integration — ⚠️ gap (falta o modelo mental do "o que é um MCP server")
**O material tem:** `.mcp.json` (projeto, versionado) vs `~/.claude.json` (pessoal); expansão de env var; resources. Tudo correto e bem ilustrado.

**O que falta (o maior gap para quem nunca fez):** **o que é um MCP server, mecanicamente.** Falta dizer que:
- Um MCP server é um **processo separado** (local via **stdio** ou remoto via **HTTP/SSE**) que **expõe tools, resources e prompts**.
- O `.mcp.json` é o arquivo que diz ao Claude Code **como iniciar e conectar** nesse processo (`command`/`args`) — por isso `npx ... server-github`: ele *sobe* o servidor.
- As tools de **todos** os servidores conectados são descobertas na conexão e ficam disponíveis juntas.

**Como melhorar:** 3–4 frases de "o que é um MCP server na prática" + transporte (stdio local vs HTTP remoto) + citar o comando `claude mcp add` como alternativa ao arquivo.

---

### 2.5 Built-in Tools (Read/Write/Edit/Bash/Grep/Glob) — ✅ suficiente
Esse é o seu dia a dia no Claude Code — a tabela de seleção e o fluxo Grep→Read→Edit estão ótimos. **Única ponte útil:** dizer que **são as mesmas built-in tools que o Agent SDK expõe** (mesmo motor). Assim você percebe que já "conhece as ferramentas de um agente".

---

## Domínio 3 — Claude Code Configuration & Workflows (20%)
*(Seu território como usuário — mas o exame testa **autoria de config**, que talvez você nunca tenha feito.)*

### 3.1 CLAUDE.md Hierarchy — ❌ correção factual (senão ✅)
**O material tem:** níveis usuário/projeto/diretório; `.claude/rules/`. A hierarquia está correta.

**Corrigir:** ❌ **`@import` não existe como palavra-chave.** A sintaxe real de import é **`@caminho/do/arquivo`** (o `@` seguido do caminho, sem "import"):
```markdown
<!-- backend/CLAUDE.md -->
@../docs/standards.md          <!-- CORRETO -->
<!-- NÃO: @import ../docs/standards.md -->
```
Isso aparece errado em vários pontos do módulo (conceito 3.1 e Prática 5) — vale corrigir em todos.

---

### 3.2 Custom Slash Commands & Skills — ✅ suficiente + ⚠️ gap de *desambiguação*
**Confirmado:** `context: fork`, `allowed-tools` e `argument-hint` **são campos reais** de SKILL.md. O material está correto.

**Gap real (e cobrado no exame):** três coisas parecidas que você (como usuário) tende a confundir. Sugiro adicionar esta tabela:

| Coisa | Onde | O que é | Contexto | Como dispara |
|---|---|---|---|---|
| **Slash command** | `.claude/commands/*.md` | "macro" de prompt reutilizável (`$ARGUMENTS`) | roda no **contexto principal** | você digita `/nome` |
| **Skill** | `.claude/skills/*/SKILL.md` | capacidade que o **modelo pode invocar sozinho**; pode isolar via `context: fork` | main **ou** fork | modelo decide (ou você invoca) |
| **Subagent** | `.claude/agents/*.md` | **agente separado** com contexto próprio, tools próprias | **sempre isolado** | via tool `Task`/`Agent` |

> Campos de frontmatter de subagent (Code): `name`, `description`, `tools`, `model`, `permissionMode`, etc. Para restringir *quais* subagents um coordinator pode chamar: `tools: Agent(web-search, doc-analysis)`.

---

### 3.3 Path-Specific Rules — ✅ suficiente (confirmado nativo)
`.claude/rules/` com frontmatter `paths:` **é feature nativa do Claude Code** e funciona como descrito (regras sem `paths` carregam sempre; com `paths` carregam só ao mexer em arquivos que casam o glob; `~/.claude/rules/` = nível usuário). Nada a corrigir.

---

### 3.4 Plan Mode vs Direct Execution — ✅ suficiente
A tabela de decisão está boa e é o seu uso diário. Única adição opcional: dizer que plan mode é um **modo de UX do Claude Code** (shift+tab) e citar o **Explore subagent** que isola descoberta verbosa.

---

### 3.5 Iterative Refinement — ✅ suficiente
Exemplos concretos > prosa, TDD, interview pattern — conteúdo de julgamento sólido (overlap com Domínio 4).

---

### 3.6 Claude Code in CI/CD — ✅ suficiente (leve gap COMO)
**Confirmado:** `-p`/`--print`, `--output-format json` (`text`/`json`/`stream-json`) e **`--json-schema` são reais** — este último é a feature de *structured outputs* (valida o resultado final contra o schema, só em print mode). O material acertou.

**Leve gap (COMO):** mostrar um trecho de pipeline mais completo (como o JSON é consumido no passo seguinte) e mencionar **autenticação headless** em CI (`ANTHROPIC_API_KEY` no ambiente) — detalhe prático que você vai bater de frente ao automatizar. E reforçar que "sessão diferente para revisar" = **um novo processo `claude -p`**.

---

## Domínio 4 — Prompt Engineering & Structured Output (20%)

### 4.1 Explicit Criteria — ✅ suficiente
Vago vs categórico, e "falso positivo destrói confiança" — ótimo, é julgamento puro.

### 4.2 Few-Shot Prompting — ✅ suficiente (nota COMO)
**Leve nota:** *onde* os exemplos entram? No **system prompt** ou como **mensagens de exemplo no array `messages`**. Para você, vale citar as duas colocações.

### 4.3 Structured Output via tool_use & JSON Schemas — ⚠️ gap (ONDE / COMO para não-dev de API)
**O material tem:** tool_use + JSON schema = output confiável; os 3 modos de `tool_choice`; nullable; sintaxe ≠ semântica. O snippet Python está **correto**.

**O que falta — o "truque" nunca é nomeado:** você **não** está chamando uma função de verdade. Você **define uma tool cujo `input_schema` É o formato de saída desejado**, força `tool_choice` para ela, e **lê o JSON de volta em `response.content[0].input`** (o que o modelo "passaria como argumento" É a sua saída estruturada). Isso é o pulo do gato que um usuário de Claude Code nunca viu.

**Ponte útil:** no **Claude Code/CI** o equivalente é `--json-schema`; na **API** é o padrão tool_use. Dizer isso conecta os dois planos.

**Como melhorar:** adicionar 2 linhas — "o que você lê de volta é `content[0].input`" — e a ponte com `--json-schema`.

### 4.4 Validation, Retry & Feedback — ✅ suficiente (nota COMO)
Julgamento bom (retry funciona p/ erro estrutural, não p/ info ausente). **Nota:** "retry" = **seu código** re-chama a API anexando o erro como nova mensagem `user`. É loop orquestrado pelo dev, não uma feature.

### 4.5 Batch Processing — ⚠️ gap (ONDE / COMO)
**O material tem:** 50% de custo, até 24h, sem SLA, `custom_id`, sem multi-turn tool calling num request, resubmeter só falhas. Conteúdo correto.

**O que falta:** **é uma API distinta** (`/v1/messages/batches`), separada do Claude Code — não é algo que você faz no terminal. Falta a forma:
```python
# [API] cada entrada é UMA chamada Messages independente (por isso "sem multi-turn tool loop")
client.messages.batches.create(requests=[
  {"custom_id": "inv-001", "params": {"model": "claude-opus-4-8", "max_tokens": 1024, "messages": [...]}},
  {"custom_id": "inv-002", "params": {...}},
])
# depois: poll do status → retrieve results → correlaciona por custom_id
```
> "Sem multi-turn tool calling num único batch request" = cada item é **uma** volta da Messages API; você não roda o loop agêntico *dentro* de um item do batch.

### 4.6 Multi-Instance & Multi-Pass Review — ✅ suficiente
Overlap com 1.6/3.6; self-review bias e diluição de atenção bem explicados.

---

## Domínio 5 — Context Management & Reliability (15%)

### 5.1 Preserving Critical Info — ⚠️ gap (POR QUE / ONDE)
**O material tem:** riscos de summarization; lost-in-the-middle; acúmulo de tool results; "case facts" block; hook `PostToolUse` para aparar `get_order_details` (**uso CORRETO de PostToolUse — contraste bom com o erro do Domínio 1**).

**O que falta:** "sempre passe o histórico completo" é uma **verdade da API crua (stateless)** — é *por isso* que você reenvia tudo. **No Claude Code isso é automático** (o app gerencia o histórico e faz auto-compaction). As técnicas manuais (case-facts block, trim) são para **quando VOCÊ gerencia o contexto** (API/SDK). Dizer isso evita a impressão de que você precisa fazer "case facts" manualmente no terminal.

### 5.2 Escalation & Ambiguity — ✅ suficiente
Gatilhos de escalação, múltiplos matches (pedir identificador, não escolher por heurística, não expor perfis) — julgamento excelente.

### 5.3 Error Propagation — ✅ suficiente
Duplica 2.2 (estruturado, access failure vs empty result). Mesma clarificação do 2.2 se aplica (campos ricos = convenção de app).

### 5.4 Context in Large Codebase — ⚠️ gap + ❌ correção
**O material tem:** degradação de contexto; scratchpad; subagent delegation; manifesto; `/compact`.

**Corrigir/faltando:**
- ❌ `fork_session` (se aparecer) → `--fork-session`/`/fork`.
- **Ponte:** `/compact` você já conhece; "subagent delegation" é a tool `Task`/`.claude/agents` (o que o Claude Code faz quando dispara um **Explore subagent**). **Scratchpad** e **manifesto** são **convenções DIY** (arquivos que você mantém), não features nativas.

### 5.5 Human Review & Confidence Calibration — ✅ suficiente
Aggregate accuracy engana; stratified sampling; confiança por campo — sólido (MLOps). **Nota:** "confidence score" aqui é valor que **você calcula/armazena**, não um campo da API.

### 5.6 Information Provenance — ✅ suficiente
Claim-source mapping, conflitos anotados (não escolher), metadados temporais — ótimo. **Nota leve:** o claim-source mapping é um **schema que você desenha** (via tool_use/output estruturado) — mesma ideia do 4.3.

---

## Resumo — correções factuais a propagar (prioridade para o exame)

| # | Onde no material | Erro | Correto |
|---|---|---|---|
| 1 | D1 §1.5 e Prática 1; D5 §5.4 | Bloquear ação com **`PostToolUse`** | **`PreToolUse`** (nega antes de executar; `permissionDecision: "deny"`). `PostToolUse` = inspecionar/transformar *depois* (uso certo em D5 §5.1) |
| 2 | D3 §3.1 e Prática 5 | **`@import ../docs/standards.md`** | **`@../docs/standards.md`** (não existe palavra-chave `import`) |
| 3 | D1 §1.3, §1.7; D5 §5.4 | **`fork_session`** como opção | **`--fork-session`** (flag CLI) ou **`/fork`** (comando); não existe `fork_session` |
| 4 | D2 §2.2; D5 §5.3 | `errorCategory`/`isRetryable` como campos MCP | Só **`isError`** é do protocolo; o resto é **convenção da app** dentro do `content` |

## Resumo — gaps de "onde/quando/como" (não são erros, são contexto faltando)

- **[API crua]** o loop `stop_reason`, statelessness, `tool_use`→`tool_result`, `tool_choice`, Batches API, tool_use-como-output-estruturado → falta dizer que **é código do dev na Messages API**.
- **[SDK]** coordinator/subagents, `Task`/`allowedTools`, hooks → falta aterrissar em **config de agente** e no *timeline* dos hooks.
- **[Code]** o que é um **MCP server** (processo separado, stdio/HTTP), desambiguação **command × skill × subagent**, `--json-schema`/headless em CI → falta o modelo mental mecânico.
- **Ponte-mãe:** Claude Code = agente sobre o Agent SDK ⇒ o que você já usa (config) é a mesma coisa que o dev de agente faz (código).
