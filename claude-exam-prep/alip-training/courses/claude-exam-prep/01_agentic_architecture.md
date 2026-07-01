# Module 1: Agentic Architecture & Orchestration (27%)

## Concepts You Must Know

### 1.1 Agentic Loop Lifecycle
- The loop: send request -> inspect `stop_reason` -> if `"tool_use"`, execute tool and loop; if `"end_turn"`, present response
- Tool results are **appended to conversation history** so the model reasons over them
- **Anti-patterns**: parsing natural language for termination signals, arbitrary iteration caps as primary stop mechanism, checking assistant text for completion indicators

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AGENTIC LOOP - FLUXO CORRETO                   │
└─────────────────────────────────────────────────────────────────────┘

  USUÁRIO
    │
    │  mensagem / request
    ▼
┌───────────┐
│  MODELO   │ ◄──────────────────────────────────────────────┐
│  (Claude) │                                                │
└───────────┘                                                │
      │                                                      │
      │  inspeciona stop_reason                              │
      │                                                      │
      ├──── "tool_use" ────► ┌─────────────────────┐        │
      │                      │  EXECUTAR FERRAMENTA │        │
      │                      │  (get_customer,      │        │
      │                      │   process_refund...) │        │
      │                      └─────────────────────┘        │
      │                                │                     │
      │                                │ resultado           │
      │                                ▼                     │
      │                      ┌─────────────────────┐        │
      │                      │  APPEND na história  │ ───────┘
      │                      │  de conversa        │  (loop continua)
      │                      └─────────────────────┘
      │
      └──── "end_turn" ────► APRESENTAR RESPOSTA AO USUÁRIO ✓

⚠️  ANTI-PADRÃO: Verificar texto do assistente para decidir parar
    if "I've completed the task" in assistant_text:  ← ERRADO!
        break

✅  PADRÃO CORRETO: Verificar stop_reason
    if response.stop_reason == "end_turn":           ← CORRETO!
        break
```

---

### 1.2 Coordinator-Subagent Patterns
- **Hub-and-spoke**: coordinator manages ALL inter-subagent communication
- Subagents have **isolated context** - they do NOT inherit the coordinator's conversation history
- Coordinator responsibilities: task decomposition, delegation, result aggregation, deciding which subagents to invoke
- **Risk**: overly narrow task decomposition leads to incomplete coverage (e.g., "creative industries" decomposed only into visual arts subtopics)

```
┌─────────────────────────────────────────────────────────────────────┐
│              PADRÃO HUB-AND-SPOKE (Coordinator-Subagent)            │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │    COORDINATOR      │
                    │  (hub / orquestrador)│
                    │  - decompõe tarefas  │
                    │  - delega trabalho   │
                    │  - agrega resultados │
                    └─────────────────────┘
                     /         |          \
                    /          |           \
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Subagent │   │ Subagent │   │ Subagent │
        │   (A)    │   │   (B)    │   │   (C)    │
        │Web Search│   │Doc Analys│   │Synthesis │
        └──────────┘   └──────────┘   └──────────┘
        [contexto     [contexto       [contexto
         ISOLADO]      ISOLADO]        ISOLADO]

  ✅ Coordinator → Subagent A  (passa contexto explicitamente)
  ✅ Coordinator → Subagent B  (passa contexto explicitamente)
  ✅ Subagent A  → Coordinator (retorna resultado)
  ❌ Subagent A  → Subagent B  (NÃO se comunicam diretamente!)
  ❌ Subagent herda contexto do Coordinator automaticamente (FALSO!)
```

---

### 1.3 Subagent Invocation & Context Passing
- `Task` tool spawns subagents; `allowedTools` must include `"Task"` for coordinator to spawn them
- Context must be **explicitly provided** in the subagent prompt - no automatic inheritance
- `AgentDefinition` configures descriptions, system prompts, and tool restrictions per subagent type
- `fork_session` creates independent exploration branches from a shared baseline

```python
# ❌ ERRADO — subagente não herda contexto automaticamente
task_tool.invoke(
    prompt="Investigue o problema de cobrança"
    # Subagente vai responder: "Que problema? Não tenho informações!"
)

# ✅ CORRETO — contexto passado explicitamente no prompt
task_tool.invoke(
    prompt=f"""
Investigue o problema de cobrança dupla.

Contexto do caso:
- Cliente: CUS-4829 (João Silva)
- Pedido: ORD-789
- Problema: Cobrado duas vezes em 15/03/2024
- Valor cobrado incorretamente: R$ 249,90

Ferramentas disponíveis: get_order_details, process_refund
Ação esperada: verificar histórico de pagamentos e confirmar duplicidade.
"""
)
```

---

### 1.4 Multi-Step Workflows with Enforcement
- **Programmatic enforcement** (hooks, prerequisite gates) vs **prompt-based guidance** for ordering
- When deterministic compliance is required (e.g., identity verification before financial operations), **prompt instructions alone have a non-zero failure rate** - use hooks
- Structured handoff protocols for escalation: customer ID, root cause, refund amount, recommended action

```
┌──────────────────────────────────────────────────────────────────────┐
│          COMPARAÇÃO: MECANISMOS DE ENFORCEMENT                       │
├─────────────────────┬─────────────────┬──────────────────────────────┤
│ Mecanismo           │ Garantia        │ Quando usar                  │
├─────────────────────┼─────────────────┼──────────────────────────────┤
│ Hooks (PostToolUse) │ DETERMINÍSTICA  │ Regras críticas: financeiro, │
│                     │ 100% garantido  │ segurança, compliance        │
├─────────────────────┼─────────────────┼──────────────────────────────┤
│ Instruções no       │ PROBABILÍSTICA  │ Comportamento preferencial,  │
│ system prompt       │ ~88-95% típico  │ guia não-crítico             │
├─────────────────────┼─────────────────┼──────────────────────────────┤
│ Few-shot examples   │ PROBABILÍSTICA  │ Melhorar consistência em     │
│                     │ melhora baseline│ casos ambíguos               │
└─────────────────────┴─────────────────┴──────────────────────────────┘

Regra de ouro: se a consequência de falha é financeira ou de segurança,
use hooks (programático). Nunca confie só no prompt para isso.
```

---

### 1.5 Agent SDK Hooks
- `PostToolUse` hooks intercept tool results for transformation before the model processes them
- Hooks can **block policy-violating actions** (e.g., refunds > $500) and redirect to escalation
- Hooks = **deterministic guarantees**; prompt instructions = **probabilistic compliance**

```python
# Exemplo: Hook PostToolUse que bloqueia reembolsos acima de $500
def post_tool_use_hook(tool_name: str, tool_result: dict) -> dict:
    if tool_name == "process_refund":
        amount = tool_result.get("amount", 0)
        if amount > 500:
            # Bloqueia e redireciona para escalada humana
            return {
                "blocked": True,
                "reason": "Reembolso > $500 requer aprovação humana",
                "action": "escalate_to_human",
                "escalation_data": {
                    "customer_id": tool_result.get("customer_id"),
                    "order_id": tool_result.get("order_id"),
                    "amount": amount,
                    "requested_by": "agent"
                }
            }
    return tool_result  # deixa passar normalmente se dentro da política

# O hook é registrado no AgentDefinition:
# agent = AgentDefinition(
#     hooks={"PostToolUse": post_tool_use_hook},
#     ...
# )
```

---

### 1.6 Task Decomposition Strategies
- **Prompt chaining** (fixed sequential): good for predictable multi-aspect reviews
- **Dynamic adaptive decomposition**: good for open-ended investigation tasks
- Split large code reviews into per-file local passes + a separate cross-file integration pass to avoid attention dilution

```
┌─────────────────────────────────────────────────────────────────────┐
│                   ESTRATÉGIAS DE DECOMPOSIÇÃO                       │
└─────────────────────────────────────────────────────────────────────┘

PROMPT CHAINING (sequencial fixo) — previsível, multi-aspecto:
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│Passo 1 │───►│Passo 2 │───►│Passo 3 │───►│Passo 4 │
│Coleta  │    │Analisa │    │Valida  │    │Relata  │
└────────┘    └────────┘    └────────┘    └────────┘
Bom para: reviews com checklist fixo, workflows ETL, documentação

DYNAMIC DECOMPOSITION (adaptativo) — open-ended, investigação:
              ┌────────────┐
              │ Coordinator│
              └────────────┘
             /      |       \
    ┌───────┐  ┌───────┐  ┌───────┐
    │ Task A│  │ Task B│  │ Task C│  ← spawned conforme necessário
    └───────┘  └───────┘  └───────┘
         \         |         /
          └────────┴─────────┘
                   │
              ┌────────┐
              │Síntese │
              └────────┘
Bom para: pesquisa, investigação de bugs, análise exploratória

CODE REVIEW MULTI-PASS (evita attention dilution):
┌───────────────────────────────────────────────────────────┐
│  PASSO 1: Análise local por arquivo (paralelo)            │
│  arquivo1.py ──► [review] ──► findings locais             │
│  arquivo2.py ──► [review] ──► findings locais             │
│  arquivo3.py ──► [review] ──► findings locais             │
└───────────────────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│  PASSO 2: Integração cross-file (sessão separada)         │
│  [todos findings] ──► data flow, interfaces, padrões      │
│                   ──► contradições entre arquivos         │
└───────────────────────────────────────────────────────────┘
```

---

### 1.7 Session State Management
- `--resume <session-name>` continues a named session
- `fork_session` creates parallel exploration branches
- Starting fresh with a structured summary is more reliable than resuming with stale tool results
- When resuming, inform about specific file changes for targeted re-analysis

```
┌─────────────────────────────────────────────────────────────────────────┐
│              GERENCIAMENTO DE ESTADO DE SESSÃO                          │
├──────────────────────────────┬──────────────────────────┬───────────────┤
│ Situação                     │ Ação Correta             │ Por quê       │
├──────────────────────────────┼──────────────────────────┼───────────────┤
│ Contexto degradado           │ Sessão nova com resumo   │ --resume       │
│ (respostas genéricas,        │ estruturado das achados  │ restaura o    │
│ "padrões típicos" em vez     │ chave                    │ estado ruim   │
│ de classes específicas)      │                          │               │
├──────────────────────────────┼──────────────────────────┼───────────────┤
│ Precisa explorar 2           │ fork_session             │ Cria branches │
│ abordagens diferentes        │                          │ independentes │
│ em paralelo                  │                          │ do baseline   │
├──────────────────────────────┼──────────────────────────┼───────────────┤
│ Sessão longa mas contexto    │ /compact                 │ Reduz tokens  │
│ ainda válido                 │                          │ mantendo o    │
│                              │                          │ essencial     │
├──────────────────────────────┼──────────────────────────┼───────────────┤
│ Crash durante processamento  │ Manifesto de estado      │ Estado persiste│
│ (ex: 8 de 20 arquivos feitos)│ (JSON) + coordinator     │ entre sessões;│
│                              │ carrega manifesto no     │ evita retrabalho│
│                              │ restart                  │               │
└──────────────────────────────┴──────────────────────────┴───────────────┘

Exemplo de manifesto para crash recovery:
{
  "migration_manifest": {
    "total_files": 20,
    "completed": ["api/v1.py", "api/v2.py", ..., "models/user.py"],  // 8 feitos
    "pending": ["models/order.py", "services/billing.py", ...],       // 12 restantes
    "last_updated": "2024-03-15T14:23:00Z"
  }
}
```

---

## Scenario: Customer Support Resolution Agent

You're building a customer support agent using the Claude Agent SDK. The agent handles returns, billing disputes, and account issues through MCP tools: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`. Target: 80%+ first-contact resolution with appropriate escalation.

---

## Practice Problem 1

**Production data shows that in 12% of cases, your agent skips `get_customer` entirely and calls `lookup_order` using only the customer's stated name, occasionally leading to misidentified accounts and incorrect refunds. What change would most effectively address this reliability issue?**

A) Add a programmatic prerequisite that blocks `lookup_order` and `process_refund` calls until `get_customer` has returned a verified customer ID.

B) Enhance the system prompt to state that customer verification via `get_customer` is mandatory before any order operations.

C) Add few-shot examples showing the agent always calling `get_customer` first, even when customers volunteer order details.

D) Implement a routing classifier that analyzes each request and enables only the subset of tools appropriate for that request type.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
When a specific tool sequence is required for critical business logic (identity verification before processing refunds), **programmatic enforcement provides deterministic guarantees** that prompt-based approaches cannot. A `PostToolUse` hook or prerequisite gate can block `lookup_order` and `process_refund` until `get_customer` has returned a verified customer ID. This eliminates the 12% failure rate entirely.

**Why B fails:**
Enhancing the system prompt relies on probabilistic LLM compliance. The agent is already skipping verification 12% of the time despite presumably knowing it should verify first. Making the instruction more emphatic reduces the rate but doesn't eliminate it. For financial operations, "usually works" isn't acceptable.

**Why C fails:**
Few-shot examples improve consistency but are still probabilistic. They add token overhead without providing a hard guarantee. The model might still skip verification in novel situations not covered by examples.

**Why D fails:**
A routing classifier addresses tool availability rather than tool ordering, which is not the actual problem. The agent has access to the right tools - it's just calling them in the wrong order.

### Key Decision Framework
**When the consequence of non-compliance is financial or safety-critical, choose programmatic enforcement (hooks/gates) over prompt-based guidance.**
</details>

---

## Practice Problem 2

**Your agent achieves 55% first-contact resolution, well below the 80% target. Logs show it escalates straightforward cases (standard damage replacements with photo evidence) while attempting to autonomously handle complex situations requiring policy exceptions. What's the most effective way to improve escalation calibration?**

A) Add explicit escalation criteria to your system prompt with few-shot examples demonstrating when to escalate versus resolve autonomously.

B) Have the agent self-report a confidence score (1-10) before each response and automatically route to humans when confidence falls below a threshold.

C) Deploy a separate classifier model trained on historical tickets to predict which requests need escalation before the main agent begins processing.

D) Implement sentiment analysis to detect customer frustration levels and automatically escalate when negative sentiment exceeds a threshold.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
The root cause is unclear decision boundaries - the agent doesn't know which cases are simple vs complex. Adding **explicit escalation criteria** with few-shot examples directly addresses this. Examples should demonstrate:
- Simple case: "Customer has photo of damaged item, standard replacement policy applies" -> resolve autonomously
- Complex case: "Customer wants price match to competitor, policy only covers own-site adjustments" -> escalate

This is the **proportionate first response** before adding infrastructure.

**Why B fails:**
LLM self-reported confidence is poorly calibrated. The agent is already **incorrectly confident** on hard cases (attempting to resolve policy exceptions) and **incorrectly uncertain** on easy cases (escalating standard replacements). A confidence score would just formalize the same bad calibration.

**Why C fails:**
Over-engineered solution requiring labeled data and ML infrastructure when prompt optimization hasn't been tried yet. Always try the simpler, lower-cost fix first.

**Why D fails:**
Sentiment doesn't correlate with case complexity. A customer might be calm about a complex policy exception or frustrated about a simple replacement delay. This solves a different problem entirely.

### Key Decision Framework
**When the agent makes wrong decisions, first fix the decision criteria (explicit instructions + examples). Only add infrastructure (classifiers, scoring) after prompt-based approaches prove insufficient.**
</details>

---

## Practice Problem 3

**You're designing a coordinator agent for a multi-agent research system. After running the system on "impact of AI on creative industries," each subagent completes successfully, but the final report covers only visual arts (digital art, graphic design, photography), completely missing music, writing, and film. The coordinator's logs show it decomposed the topic into three visual-arts-only subtasks. What is the most likely root cause?**

A) The synthesis agent lacks instructions for identifying coverage gaps in findings from other agents.

B) The web search agent's queries are not comprehensive enough and need to be expanded.

C) The coordinator agent's task decomposition is too narrow, resulting in subagent assignments that don't cover all relevant domains of the topic.

D) The document analysis agent is filtering out sources related to non-visual creative industries due to overly restrictive relevance criteria.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: C

**Why C is correct:**
The coordinator's logs directly reveal the root cause: it decomposed "creative industries" into only visual arts subtopics. **The subagents executed their assigned tasks correctly** - they just weren't assigned the right tasks. This is a coordinator decomposition failure.

**Why A, B, D fail:**
All three options blame downstream agents that are working correctly within their assigned scope. The web search agent found relevant articles for its assigned topics. The document analysis agent summarized correctly. The synthesis agent combined what it received. The problem is upstream - the coordinator didn't give them the right scope.

### Key Decision Framework
**When all subagents succeed individually but the combined output has gaps, look at the coordinator's task decomposition first.** The coordinator is responsible for ensuring complete topic coverage when breaking tasks into subtasks.
</details>

---

## Practice Problem 4

**Your agentic loop processes customer requests. During testing, the agent occasionally stops mid-task, presenting an incomplete response to the user even though more tools should be called. Your loop code checks if the assistant's text contains phrases like "I've completed the task" to decide whether to stop. What's the most likely cause of the premature termination?**

A) The agent's system prompt doesn't instruct it to complete all steps before responding.

B) The loop is using natural language parsing for termination instead of checking `stop_reason` for `"tool_use"` vs `"end_turn"`.

C) The context window is full, forcing the model to stop generating mid-task.

D) The agent needs an explicit "continue" tool to signal it has more work to do.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
Parsing assistant text for completion signals is an anti-pattern. The agentic loop should check `stop_reason`: continue when `"tool_use"`, terminate when `"end_turn"`. Natural language is unreliable because the model may include phrases like "I've completed X" while still intending to call more tools.

**Why A fails:**
The system prompt may help shape behavior, but the root cause is the loop's termination logic. Even with perfect prompting, checking natural language for stop signals will produce false positives.

**Why C fails:**
A full context window would produce a different failure mode (truncation or API error), not a clean-looking incomplete response with completion-sounding language.

**Why D fails:**
The model already signals continuation intent via `stop_reason: "tool_use"`. Adding a custom "continue" tool is unnecessary complexity when the built-in mechanism exists.

### Key Decision Framework
**The agentic loop must use `stop_reason` for termination decisions. Parsing natural language from the assistant's response is unreliable and produces false positives.**
</details>

---

## Practice Problem 5

**Your coordinator agent delegates a billing investigation to a subagent. The coordinator's conversation includes the customer ID (CUS-4829), order history, and a complaint about being double-charged. The subagent responds: "I'd be happy to help, but I don't have any customer or order information to investigate. Could you provide the details?" What's the root cause?**

A) The subagent's system prompt doesn't include billing investigation instructions.

B) The subagent was spawned without including the relevant customer context in its prompt, since subagents don't automatically inherit the coordinator's conversation history.

C) The subagent lacks the billing tools needed for the investigation.

D) The coordinator should use `fork_session` instead of `Task` to maintain shared context.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
Subagents operate with isolated context. They do NOT inherit the coordinator's conversation history automatically. All relevant context must be explicitly included in the subagent's prompt when spawning via the `Task` tool. The subagent's response directly confirms it has no customer or order information, pointing to a context passing failure.

**Why A fails:**
The subagent isn't confused about what to do (billing investigation) - it's missing the data to do it. Instructions vs. context are different problems, and the subagent's response specifically says it lacks information, not that it doesn't know its role.

**Why C fails:**
The subagent isn't reporting missing tools. It's reporting missing context data. Tool availability and context are separate concerns.

**Why D fails:**
`fork_session` creates branches from a shared baseline for divergent exploration, not for passing context to subagents. The correct pattern is to include relevant context in the `Task` prompt.

### Key Decision Framework
**Subagents are context-isolated. When a subagent reports missing information that exists in the coordinator's conversation, the fix is always to pass that context explicitly in the Task prompt.**
</details>

---

## Practice Problem 6

**You spent 2 hours exploring a large codebase with Claude Code, identifying architectural patterns across 30+ files. Claude's responses are now inconsistent - referencing "typical patterns" instead of the specific classes it found earlier. You need to continue the investigation tomorrow. What's the best approach?**

A) Use `--resume` with the session name to continue exactly where you left off.

B) Start a new session with a structured summary of key findings from the previous session, then continue investigation from there.

C) Use `/compact` to reduce context and continue in the current session.

D) Use `fork_session` to create a fresh branch from the current degraded state.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
When prior tool results are stale and context has degraded, starting fresh with a structured summary is more reliable than resuming. The model is already showing signs of context degradation (generic references instead of specifics). A new session with injected key findings gives the model accurate, condensed context to work from.

**Why A fails:**
`--resume` would restore the degraded state. The model's inconsistent responses indicate context quality has already deteriorated. Resuming puts you right back into the degraded session.

**Why C fails:**
`/compact` reduces token count but loses specifics that are already inconsistent. Compacting a degraded session preserves the degradation in a smaller form - it doesn't restore accuracy.

**Why D fails:**
`fork_session` preserves the degraded state in a new branch. Branching from a bad state gives you a new branch with the same problems.

### Key Decision Framework
**When context has degraded (vague references replacing specifics), start fresh with a structured summary rather than resuming or compacting the degraded session.**
</details>

---

## Practice Problem 7

**Your multi-agent research system needs to investigate "AI regulation across the EU, US, and China." The coordinator can either assign all three regions to separate subagents simultaneously, or investigate them sequentially so each subagent can build on prior findings. The regions have independent regulatory frameworks with minimal cross-references. How should the coordinator execute?**

A) In parallel by emitting multiple `Task` tool calls in a single coordinator response, since the regions have independent regulatory frameworks and no subagent needs another's output.

B) Sequentially, so each subagent can reference findings from earlier regions for comparative analysis.

C) Parallel for EU and US, then sequential for China using combined EU/US findings as context.

D) Assign all three regions to a single subagent to ensure consistent analysis methodology.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
When subtasks are independent (no subagent needs another's output), spawn them in parallel by emitting multiple `Task` tool calls in a single coordinator response. This reduces total latency from 3x sequential time to ~1x. The problem statement explicitly says the regions have independent regulatory frameworks with minimal cross-references, confirming independence.

**Why B fails:**
Sequential execution creates artificial dependencies where none exist. Each region's regulatory framework is independent, so earlier findings don't meaningfully inform later research. Sequential execution wastes time for no benefit.

**Why C fails:**
This is a compromise that still introduces unnecessary sequential dependency for China. If frameworks are independent, there's no reason to wait for EU/US results before investigating China.

**Why D fails:**
A single subagent loses the parallelism benefit entirely and risks attention dilution across three complex, independent regulatory domains. The model may under-research later regions as context fills up.

### Key Decision Framework
**When subtasks have no data dependencies between them, execute in parallel via multiple Task calls in one coordinator response. Sequential execution should only be used when a later subtask requires output from an earlier one.**
</details>

---

## Practice Problem 8

**Your multi-agent code migration system crashes after completing 8 of 20 file conversions. When you restart the coordinator, it has no memory of which files were already converted and begins processing from the start, creating duplicate conversions and wasted work. How should you prevent this?**

A) Have each agent write completed file paths to a structured manifest file after each conversion, and have the coordinator load the manifest on startup to skip already-converted files.

B) Add idempotent conversion logic so reprocessing already-converted files is harmless.

C) Checkpoint the full conversation history to disk after each file so the session can be restored exactly.

D) Wrap all 20 conversions in a database transaction so they either all succeed or all roll back.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
Structured state persistence via manifests is the correct pattern for crash recovery. Each agent exports its state to a known location (e.g., a JSON manifest of completed files), and the coordinator loads the manifest on resume to understand what's already done. This is lightweight, inspectable, and reliable.

**Why B fails:**
Idempotent logic is a fallback, not a primary strategy. It wastes compute by reprocessing 8 already-converted files. In large migrations, this "harmless" reprocessing can add significant time and cost. Idempotency is a safety net, not a recovery plan.

**Why C fails:**
Full conversation checkpointing is too large and brittle. Conversation histories can be enormous, and restoring an exact conversational state doesn't guarantee the model will behave identically. Manifests capture the essential state (what's done) without the bloat.

**Why D fails:**
Database transactions are impractical for long-running multi-agent workflows. You don't want 8 successful conversions rolled back because the 9th failed. The goal is graceful partial recovery, not all-or-nothing semantics.

### Key Decision Framework
**For crash recovery in multi-agent systems, use structured manifests to persist progress. Agents write state to known locations, and coordinators load manifests on restart to resume from where work left off.**
</details>

---

## Key Takeaways for Domain 1

1. **Hooks > prompts** for deterministic business rule enforcement
2. **Coordinator owns decomposition** - downstream agent success doesn't mean the system works
3. **Explicit criteria + examples** are the first fix for bad agent decisions
4. **Subagents are isolated** - always pass context explicitly in the prompt, don't assume inheritance
5. **stop_reason** drives the agentic loop - never parse natural language for termination: `"tool_use"` = continue, `"end_turn"` = done
6. **Avoid anti-patterns**: NL parsing for termination, arbitrary iteration caps, self-review within the same session
7. **Fresh start with summary > resume** when prior context is degraded
8. **Parallel execution** for independent subtasks via multiple Task calls in one response
9. **Manifests for crash recovery** - structured state persistence enables graceful restart
