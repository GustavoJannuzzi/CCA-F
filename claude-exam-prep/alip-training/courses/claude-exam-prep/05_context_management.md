# Module 5: Context Management & Reliability (15%)

## Concepts You Must Know

### 5.1 Preserving Critical Information Across Long Interactions
- **Progressive summarization risks**: condensing numerical values, percentages, dates, and customer expectations into vague summaries that lose precision
- **Lost-in-the-middle effect**: models reliably process information at the beginning and end of long inputs but may omit findings from middle sections
- **Tool result accumulation**: verbose tool outputs consume tokens disproportionately to their relevance (e.g., 40+ fields per order lookup when only 5 are relevant)
- Always pass **complete conversation history** in subsequent API requests to maintain coherence

**Skills:**
- Extract transactional facts (amounts, dates, order numbers) into a persistent "case facts" block included in each prompt
- Trim verbose tool outputs to only relevant fields before they accumulate in context
- Place key findings summaries at the **beginning** of aggregated inputs with explicit section headers to mitigate position effects

---

#### Exemplo Prático: Progressive Summarization — RUIM vs BOM

```
RUIM - Resumo vago perde precisão:
"O cliente teve problemas com pedidos recentes e espera resolução"
  └── Perdemos: valores exatos, datas, status de reembolso, número do caso

BOM - "Case Facts" block preserva dados transacionais:
---CASE FACTS (atualizado a cada tool call)---
Cliente: CUS-4829 (João Silva)
Pedido #1: ORD-789  | Status: devolvido    | Reembolso: R$234,50
Pedido #2: ORD-1203 | Status: em trânsito  | Entrega: 20/03/2024
Pontos Fidelidade: 450 pts | Último post: 15/02/2024 (PENDENTE)
Reclamação: Cobrança dupla em 15/03/2024
---FIM CASE FACTS---
  └── Preservamos: tudo que importa, compactado, sem ambiguidade
```

---

#### Diagrama: Lost-in-the-Middle Effect

```
LOST-IN-THE-MIDDLE EFFECT:

Posição no contexto:    Início       Meio         Fim
Atenção do modelo:      ████████     ████         ████████
                        (alta)       (baixa)      (alta)

Implicação prática:
┌─────────────────────────────────────────────────────────┐
│ [INÍCIO] Resumo de achados  ← COLOQUE AQUI!             │
│          System prompt / instruções críticas             │
│                                                         │
│ [MEIO]   Tool result 1...  Tool result 2...             │
│          Tool result 3...  Tool result 4...  ← PERIGO!  │
│          (achados do meio podem ser ignorados/perdidos)  │
│                                                         │
│ [FIM]    Pergunta atual do usuário ← processada bem     │
└─────────────────────────────────────────────────────────┘

Solução: mova resumos de achados para o INÍCIO do contexto
         com cabeçalhos de seção explícitos (## Achados Principais)
```

---

#### Exemplo: PostToolUse Hook para Aparar Tool Results

```python
# Hook que filtra tool results ANTES de entrarem no contexto do modelo
def post_tool_use_hook(tool_name: str, result: dict) -> dict:
    if tool_name == "get_order_details":
        # get_order_details retorna 45 campos — mantemos só 5 relevantes
        return {
            "status":            result.get("status"),
            "tracking_number":   result.get("tracking_number"),
            "estimated_delivery":result.get("estimated_delivery"),
            "items":             result.get("items"),
            "refund_eligible":   result.get("refund_eligible")
            # 40 campos descartados: warehouse_code, internal_sku,
            # audit_trail, carrier_hub, etc.
        }
    return result  # outros tools passam sem modificação

# Resultado: cada get_order_details usa ~100 tokens em vez de ~900
# Após 6 chamadas: 600 tokens vs 5.400 tokens — diferença decisiva
```

---

### 5.2 Escalation and Ambiguity Resolution
- **Appropriate escalation triggers**: customer explicitly requests human, policy exceptions/gaps, inability to make meaningful progress
- **NOT just complex cases** - a straightforward case should be resolved even if complex-sounding
- **Sentiment-based escalation and self-reported confidence scores are unreliable** proxies for actual case complexity
- **Multiple customer matches** require clarification (request additional identifiers) NOT heuristic selection
- Honor explicit customer requests for human agents **immediately** without first attempting investigation

**Skills:**
- Add explicit escalation criteria with **few-shot examples** demonstrating when to escalate vs resolve
- Escalate when policy is **ambiguous or silent** on the customer's specific request
- Ask for additional identifiers when tool results return multiple matches

---

#### Tabela de Gatilhos de Escalação

| Situação | Escalar? | Por quê |
|----------|----------|---------|
| Cliente pede explicitamente por humano | ✅ IMEDIATAMENTE | Respeitar preferência sem tentar resolver antes |
| Caso complexo mas dentro da política | ❌ Resolver | Complexidade ≠ necessidade de escalação |
| Política não cobre o caso (gap) | ✅ Escalar | Agente não deve criar políticas on-the-fly |
| Cliente frustrado (sentimento negativo) | ❌ Por si só | Sentimento é proxy não confiável de complexidade |
| Agente incapaz de avançar após tentativas | ✅ Escalar | Incapacidade de progredir = gatilho válido |
| Confiança auto-reportada do LLM < 0.7 | ❌ Por si só | Scores de confiança do LLM são mal calibrados |

---

#### Diagrama: Múltiplos Matches — Padrão Correto

```
Tool call: get_customer("Sarah Johnson")

Retorno do tool:
├── Match 1: Sarah Johnson | CUS-1234 | última atividade: ontem
├── Match 2: Sarah Johnson | CUS-5678 | última atividade: 3 meses atrás
└── Match 3: Sarah Johnson | CUS-9012 | última atividade: 1 ano atrás

❌ ERRADO: Selecionar heuristicamente (mais recente = CUS-1234)
   └── Risco: processar reembolso na conta errada

❌ ERRADO: Mostrar todos os 3 perfis ao cliente
   └── Risco: exposição de dados de outros clientes (privacidade!)

❌ ERRADO: Escalar para humano imediatamente
   └── Risco: escalação desnecessária de problema solucionável

✅ CORRETO: Pedir identificador adicional
   Agente: "Para garantir que estou acessando a conta certa, pode
            me confirmar seu e-mail ou os últimos 4 dígitos do
            cartão cadastrado?"
   └── Resolve com clarificação, sem violar privacidade, sem escalar
```

---

### 5.3 Error Propagation Across Multi-Agent Systems
- **Structured error context**: failure type, attempted query, partial results, alternative approaches
- Distinguish **access failures** (timeouts needing retry) from **valid empty results** (successful query with no matches)
- Generic error statuses ("search unavailable") hide valuable context from the coordinator
- **Anti-patterns**: silently suppressing errors (returning empty as success) OR terminating entire workflows on single failures

**Skills:**
- Return structured error context including failure type, what was attempted, partial results, and potential alternatives
- Subagents implement local recovery for transient failures, only propagate errors they cannot resolve
- Structure synthesis output with **coverage annotations** indicating which topics are well-supported vs have gaps

---

#### Diagrama: Fluxo de Propagação de Erro em Multi-Agent

```
Cenário: Subagente (Web Search) → Timeout após 30s

┌────────────────────────────────────────────────────────────────┐
│ ❌ ANTI-PATTERN 1: Suprimir silenciosamente                    │
│                                                                │
│  Subagente retorna: {"results": [], "status": "success"}       │
│  Coordinator interpreta: "Busca ok, zero resultados"           │
│  Consequência: não tenta alternativas → relatório incompleto   │
│  (access failure disfarçada de valid empty result!)            │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ❌ ANTI-PATTERN 2: Terminar todo o workflow                    │
│                                                                │
│  Subagente lança exceção → Coordinator encerra tudo            │
│  Consequência: perdemos os outros 3 subagentes que já          │
│  completaram com sucesso → desperdício total                   │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ✅ CORRETO: Erro estruturado com contexto                      │
│                                                                │
│  Subagente retorna:                                            │
│  {                                                             │
│    "status": "error",                                          │
│    "errorCategory": "transient",                               │
│    "isRetryable": true,                                        │
│    "attemptedQuery": "AI impact on music industry 2024",       │
│    "partialResults": ["3 artigos encontrados antes do timeout"],│
│    "alternatives": ["query mais específica", "doc analysis"]   │
│  }                                                             │
│                                                                │
│  Coordinator decide de forma informada:                        │
│  → Retentar com query mais específica?                         │
│  → Usar partial results na síntese?                            │
│  → Marcar gap de cobertura nessa área do relatório?            │
└────────────────────────────────────────────────────────────────┘
```

---

### 5.4 Managing Context in Large Codebase Exploration
- **Context degradation**: in extended sessions, models start giving inconsistent answers and referencing "typical patterns" rather than specific classes discovered earlier
- **Scratchpad files** for persisting key findings across context boundaries
- **Subagent delegation**: subagents investigate specific questions while the main agent preserves high-level understanding
- **Crash recovery**: structured agent state exports (manifests) that the coordinator loads on resume
- `/compact` to reduce context usage during extended exploration sessions

**Skills:**
- Spawn subagents for specific investigations ("find all test files," "trace refund flow dependencies")
- Maintain scratchpad files recording key findings, referencing them for subsequent questions
- Summarize findings from one exploration phase before spawning sub-agents for the next phase

---

#### Estratégias para Exploração Extensa de Codebase

```
ESTRATÉGIAS PARA CODEBASE EXPLORATION EXTENSA:

┌─────────────────────────────────────────────────────────────┐
│ 1. SCRATCHPAD FILE — persiste achados entre sessões          │
│                                                             │
│    exploration_notes.md                                     │
│    ┌─────────────────────────────────────────────┐          │
│    │ ## Padrões Identificados                    │          │
│    │ - AuthService usa JWT com 24h expiry        │          │
│    │ - Todos handlers herdam de BaseHandler      │          │
│    │ - Config via env vars (não config files)    │          │
│    │                                             │          │
│    │ ## Arquivos Chave                           │          │
│    │ - src/auth/service.py  (linha 45: token)   │          │
│    │ - src/core/base_handler.py (middleware)     │          │
│    └─────────────────────────────────────────────┘          │
│    → Referenciado em perguntas subsequentes                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. SUBAGENT DELEGATION — investiga sem poluir contexto      │
│                                                             │
│    Coordinator (mantém visão de alto nível)                 │
│         ├── Subagente A: "Liste todos os arquivos de teste" │
│         ├── Subagente B: "Trace o fluxo de autenticação"    │
│         └── Subagente C: "Onde o refund é processado?"      │
│    → Cada subagente retorna RESUMO — não output completo    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. /compact — reduz tokens durante exploração extensa       │
│                                                             │
│    Quando usar: contexto > 70-80% cheio, sessão ainda útil  │
│    Efeito: comprime histórico mantendo pontos essenciais    │
│    Limitação: NÃO corrige contexto já degradado             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 4. SINAIS DE DEGRADAÇÃO DE CONTEXTO — quando agir           │
│                                                             │
│    ⚠️  "padrões típicos" em vez de classes específicas      │
│    ⚠️  Respostas inconsistentes entre perguntas similares   │
│    ⚠️  Perde referência a achados do início da sessão       │
│                                                             │
│    → Ação: iniciar nova sessão com resumo estruturado       │
│      (fresh start > resume de sessão degradada)             │
└─────────────────────────────────────────────────────────────┘
```

#### Exemplo: Manifest para Crash Recovery

```json
// state_manifest.json — escrito por cada agente após completar sua tarefa
{
  "completed_files": [
    "src/auth/service.py",
    "src/auth/models.py",
    "src/orders/handler.py"
  ],
  "in_progress": null,
  "pending_files": [
    "src/orders/models.py",
    "src/billing/service.py"
  ],
  "last_updated": "2024-03-15T14:32:00Z",
  "checkpoint_version": 8
}

// No restart após crash:
// Coordinator carrega manifest → pula completed_files → retoma de pending_files
// 8 arquivos já convertidos NÃO são reprocessados
```

---

### 5.5 Human Review Workflows and Confidence Calibration
- **Aggregate accuracy metrics** (e.g., 97% overall) may mask poor performance on specific document types or fields
- **Stratified random sampling** for measuring error rates in high-confidence extractions and detecting novel error patterns
- **Field-level confidence scores** calibrated using labeled validation sets for routing review attention
- Validate accuracy **by document type and field** before automating high-confidence extractions

---

#### Diagrama: Por Que Aggregate Accuracy Engana

```
PROBLEMA: 97% accuracy global esconde 78% em handwritten

Volume total: 10.000 invoices
├── Typed invoices:       73.6% do volume | 99.5% accuracy ← quase perfeito
├── Scanned invoices:     18.4% do volume | 94.0% accuracy ← aceitável
└── Handwritten invoices:  8.0% do volume | 78.0% accuracy ← RISCO!

SAMPLING INGÊNUO (5% aleatório → ~500 invoices):
├── ~368 typed     revisadas (99.5% → quase sem erros encontrados)
├── ~92  scanned   revisadas (94% → poucos erros)
└── ~40  handwritten revisadas (78% → ~9 erros, mas sub-representado!)
   → Taxa de erro 22% pode PIORAR sem ser detectada!

SAMPLING ESTRATIFICADO correto:
├── Typed:       Revisar  1% → ~74  amostras  (baixo risco)
├── Scanned:     Revisar  5% → ~92  amostras  (risco médio)
└── Handwritten: Revisar 30% → ~240 amostras  ← foco onde há risco!

→ Effort proporcional ao risco por categoria
→ Regressões detectadas por categoria (não escondidas no agregado)
→ Validar por tipo de documento E por campo antes de reduzir revisão
```

---

### 5.6 Information Provenance in Multi-Source Synthesis
- **Source attribution is lost** during summarization when findings are compressed without preserving claim-source mappings
- Synthesis agent must **preserve and merge** structured claim-source mappings
- **Conflicting statistics from credible sources**: annotate conflicts with source attribution rather than arbitrarily selecting one value
- **Temporal data**: require publication/collection dates to prevent temporal differences from being misinterpreted as contradictions

**Skills:**
- Require subagents to output structured claim-source mappings (source URLs, document names, relevant excerpts)
- Structure reports with explicit sections distinguishing **well-established findings** from **contested ones**
- Include publication/data collection dates in structured outputs to enable correct temporal interpretation

---

#### Exemplo: Structured Claim-Source Mapping

```json
// Saída RUIM do subagente (perde proveniência na prose):
"Solar adoption grew significantly in 2024, with major markets
 seeing double-digit growth rates."
// → Synthesis não sabe de onde veio, não pode comparar com outras fontes

// Saída BOA do subagente (claim-source mapping estruturado):
{
  "claims": [
    {
      "claim": "Solar adoption grew 34% in 2024",
      "source_name": "DOE Annual Energy Outlook 2024",
      "source_url": "https://eia.gov/...",
      "publication_date": "2024-03-01",
      "excerpt": "Utility-scale solar capacity additions reached..."
    },
    {
      "claim": "Solar adoption grew 28% in 2024",
      "source_name": "IEA Renewables Report 2024",
      "source_url": "https://iea.org/...",
      "publication_date": "2024-04-15",
      "excerpt": "Global solar PV installations grew by..."
    }
  ]
}

// Synthesis agent com CONFLITO — NÃO escolhe um valor, ANOTA o conflito:
"Taxas de crescimento solar variam por fonte: DOE reporta 34%
 (DOE Annual Energy Outlook, mar/2024), IEA reporta 28%
 (IEA Renewables Report, abr/2024). As diferenças podem refletir
 metodologias distintas (utility-scale vs. total instalado)."
```

#### Diagrama: Metadados Temporais Previnem Falsos Conflitos

```
FALSO CONFLITO (mesmo fato, épocas diferentes):

  Dado A: "População: 2,1 milhões"  ← fonte: Censo 2018
  Dado B: "População: 2,4 milhões"  ← fonte: Estimativa 2023

  SEM metadata temporal:
    Synthesis vê: "2,1M vs 2,4M = CONFLITO!" ← errado!

  COM metadata temporal:
    Synthesis vê: "2,1M em 2018 → 2,4M em 2023 = crescimento ✓"

────────────────────────────────────────────────────────────────

CONFLITO REAL (mesma época, fontes diferentes):

  Dado A: "PIB cresceu 3.2%" — Banco Central, Q3/2024
  Dado B: "PIB cresceu 2.8%" — FMI, Q3/2024

  → Anotar AMBOS com atribuição e data
  → Não selecionar arbitrariamente
  → Deixar o leitor avaliar diferença metodológica
```

---

## Scenario: Multi-Agent Research System

You're building a multi-agent research system using the Claude Agent SDK. A coordinator agent delegates to specialized subagents: one searches the web, one analyzes documents, and one synthesizes findings. The system researches topics and produces comprehensive, cited reports.

---

## Practice Problem 1

**Your customer support agent handles multi-issue requests. A customer writes: "I need to return order #5521, and also my account email needs updating, and can you check why my loyalty points didn't post?" The agent successfully processes the return but then gives inconsistent information about the loyalty points, referencing "standard processing times" instead of the specific lookup it performed earlier in the conversation. What's the most likely cause?**

A) The loyalty points system returned an error that the agent is masking with generic language to avoid confusing the customer.

B) The agent is designed to handle only one issue per conversation and can't maintain state across multiple sequential operations.

C) The agent's conversation context has degraded - earlier tool results and findings are being lost or deprioritized as the conversation grows, causing it to fall back on general knowledge.

D) The agent's system prompt instructs it to provide general guidance for issues it's unsure about, and the loyalty points query returned ambiguous results.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: C

**Why C is correct:**
This is a classic **context degradation** problem. In extended conversations with multiple tool calls, earlier tool results accumulate in context but get deprioritized. The agent performed a specific loyalty points lookup but, by the time it processes this third issue, the specific findings from that lookup are buried deep in the conversation history. It falls back on general knowledge ("standard processing times") instead of referencing the specific data it retrieved.

The fix: extract key facts from each tool call into a persistent "case facts" block that stays at the top of the working context, ensuring specific findings aren't lost to context degradation.

**Why B fails:**
The agent successfully handled the first issue (return), showing it can process sequential operations.

**Why A fails:**
The scenario says the agent gives inconsistent information referencing "standard processing times" - this is context degradation behavior, not error masking.

**Why D fails:**
The question states the agent performed a lookup, not that results were ambiguous. The inconsistency is between what the agent found and what it reports.

### Key Decision Framework
**When an agent starts referencing general knowledge instead of specific tool results obtained earlier in the conversation, the root cause is context degradation. Fix with persistent fact extraction and explicit section headers.**
</details>

---

## Practice Problem 2

**Your research system produces a report on renewable energy adoption rates. The synthesis agent's report states "Solar adoption grew 34% in 2024" without attribution. One subagent found a DOE report saying 34% growth, another found an IEA report saying 28% growth. The synthesis agent apparently chose the DOE figure without noting the discrepancy. How should you fix this?**

A) Require subagents to output structured claim-source mappings that the synthesis agent must preserve, and instruct the synthesis agent to annotate conflicting statistics with source attribution rather than selecting one value.

B) Have the synthesis agent always prefer the most recent source when statistics conflict.

C) Add a verification subagent that checks all statistics against a primary authoritative source before synthesis.

D) Instruct the synthesis agent to average conflicting statistics and report the mean value.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
The fix has two parts:
1. **Upstream**: Require subagents to output **structured claim-source mappings** (claim, source URL, document name, publication date, relevant excerpt) rather than just prose summaries
2. **Downstream**: Instruct the synthesis agent to **annotate conflicts with source attribution** rather than arbitrarily selecting one value

The report should read: "Solar adoption growth rates vary by source: the DOE reports 34% growth (DOE Annual Energy Outlook, 2024), while the IEA reports 28% growth (IEA Renewables Report, 2024)."

**Why B fails:**
Recency doesn't determine accuracy. Both sources may be current but use different methodologies or scopes.

**Why C fails:**
No single "primary authoritative source" exists for most research topics. This just moves the selection problem upstream.

**Why D fails:**
Averaging statistics with different methodologies produces a meaningless number. The DOE and IEA may be measuring different things (e.g., residential vs total adoption).

### Key Decision Framework
**Never arbitrarily select between conflicting statistics. Require structured claim-source mappings from subagents and instruct synthesis to preserve both values with attribution, letting the reader evaluate.**
</details>

---

## Practice Problem 3

**Your support agent needs to look up a customer, but the `get_customer` tool returns three matches for "Sarah Johnson." The agent picks the one with the most recent activity and proceeds with a refund. This turns out to be the wrong customer. How should the agent handle multiple matches?**

A) Ask the customer for additional identifying information (email, phone, last 4 of card) to disambiguate, rather than selecting based on heuristics.

B) Return all three profiles to the customer and ask them to confirm which one is theirs.

C) Use the customer's IP address or session data to automatically select the most likely match.

D) Escalate to a human agent whenever multiple matches are found since the AI can't reliably disambiguate.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
When tool results return multiple matches, the agent should **request additional identifiers** from the customer to disambiguate rather than selecting based on heuristics (like most recent activity). Asking for email, phone, or last 4 digits of a card number narrows the match to the correct customer.

**Why B fails:**
Exposing all three customer profiles raises privacy concerns - showing other customers' information to someone who may not be any of them.

**Why C fails:**
IP/session data may not be available to the agent's tools, and IP addresses don't reliably identify customers (shared networks, VPNs).

**Why D fails:**
Over-escalation for a solvable problem. The agent can resolve this by asking a simple clarifying question - no human needed.

### Key Decision Framework
**Multiple matches = ask for additional identifiers. Never select heuristically, never expose other customers' data, and don't escalate when clarification can resolve it.**
</details>

---

## Practice Problem 4

**Your customer support agent calls `get_order_details` which returns 45 fields per order (shipping history, warehouse codes, internal SKUs, audit trails, etc.). After 5-6 tool calls in a conversation, the agent starts missing key details from earlier lookups and gives vague answers. Only 5 fields per order are typically relevant to customer inquiries (status, tracking number, delivery date, item names, refund eligibility). Context window usage is at 80%. What's the most effective fix?**

A) Increase max_tokens to accommodate more tool results in the conversation.

B) Instruct the agent in the system prompt to only reference the most recent tool result.

C) Summarize the entire conversation every 3 tool calls to free up context space.

D) Implement a PostToolUse hook that trims `get_order_details` results to only the 5 relevant fields before they enter the conversation context.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: D

**Why D is correct:**
Tool results accumulate in context and consume tokens disproportionately to their relevance. A **PostToolUse hook** that trims the 45 fields down to 5 relevant ones before the model processes them prevents context bloat at the source. Each `get_order_details` call now contributes only the essential information (status, tracking number, delivery date, item names, refund eligibility), keeping context lean even after many tool calls.

**Why A fails:**
`max_tokens` controls **output length** (how many tokens the model can generate in a response), not context capacity. Increasing it doesn't give the model more room to process earlier tool results.

**Why C fails:**
Periodic summarization **loses precision** in recent results. Summarizing every 3 calls means specific values from the most recent lookups get compressed into vague summaries - exactly the problem we're trying to solve.

**Why B fails:**
Ignoring earlier results **breaks multi-issue conversations**. If a customer asks about three different orders, the agent needs to reference findings from all lookups, not just the last one.

### Key Decision Framework
**When tool outputs are verbose and context is filling up, trim at the source with PostToolUse hooks. Don't confuse max_tokens (output length) with context capacity, and don't sacrifice earlier results to save space.**
</details>

---

## Practice Problem 5

**Your invoice extraction system reports 97% overall accuracy across 10,000 test invoices. Your team proposes reducing human review to a 5% random sample. However, when you break down accuracy by document type, you find: typed invoices 99.5% accurate, scanned invoices 94% accurate, handwritten invoices 78% accurate. Handwritten invoices represent 8% of total volume. What review strategy should you implement?**

A) Stratified sampling that maintains higher review rates for handwritten invoices while reducing review for typed invoices, with accuracy tracked separately by document type.

B) The 5% random sample is sufficient since 97% overall accuracy meets the production threshold.

C) 100% human review on all invoice types until handwritten accuracy improves to match typed invoices.

D) Exclude handwritten invoices from automated extraction entirely and process them manually.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
Aggregate accuracy metrics can mask poor performance on specific document types or fields. 97% overall hides the 78% handwritten accuracy. **Stratified sampling** ensures the review effort matches the risk: high review rate for handwritten (78% accuracy), moderate for scanned (94%), minimal for typed (99.5%). Tracking accuracy separately by document type lets you detect regressions in any category and adjust review rates accordingly.

**Why B fails:**
A 5% random sample would **under-sample the high-error category**. With handwritten invoices at only 8% of volume, a random 5% sample would include very few handwritten invoices - not enough to catch the 22% error rate or detect if it worsens.

**Why C fails:**
100% review **wastes effort on the 99.5% category**. Typed invoices are nearly perfect - reviewing all of them consumes resources that should be directed toward the handwritten invoices where errors actually occur.

**Why D fails:**
Excluding handwritten invoices **gives up on improvement** instead of targeting review where it matters. The system can still extract handwritten invoices with human review as a safety net, and the accuracy data from reviews can be used to improve the model over time.

### Key Decision Framework
**Never rely on aggregate accuracy metrics alone. Break down performance by document type, field, and other relevant dimensions. Use stratified sampling to match review effort to risk level, and track accuracy separately for each category.**
</details>

---

## Practice Problem 6

**Your research system produces a report on urban population trends. The synthesis agent flags a 'significant discrepancy' between two credible sources: Source A reports a city's population as 2.1 million, Source B reports 2.4 million. Upon investigation, Source A is a 2018 census and Source B is a 2023 estimate. The synthesis agent treated these as contradictory claims about the same fact. How should you prevent this class of false contradictions?**

A) Instruct the synthesis agent to always prefer the most recent source for numerical data.

B) Add a tolerance threshold (e.g., 20%) so small numerical differences are not flagged as contradictions.

C) Require subagents to include publication or data collection dates in their structured outputs, and instruct the synthesis agent to consider temporal context before flagging contradictions.

D) Have a verification subagent cross-reference all statistics against a single authoritative database.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: C

**Why C is correct:**
Temporal differences between data sources are a common source of false contradictions. Requiring **publication/collection dates** in structured outputs lets the synthesis agent distinguish "different measurements at different times" from "contradictory claims about the same time period." In this case, a 2018 census of 2.1M and a 2023 estimate of 2.4M aren't contradictory - they represent population growth over 5 years.

**Why A fails:**
Preferring recency **silences legitimate conflicts** between contemporary sources. If two 2023 reports disagree, you'd arbitrarily pick one instead of noting the discrepancy. Recency is relevant metadata, but it shouldn't be an automatic selection rule.

**Why B fails:**
Tolerance thresholds are **arbitrary and would hide real contradictions**. A 20% threshold would also suppress a genuine conflict between two 2023 sources reporting 2.1M vs 2.4M (14% difference). The issue isn't the magnitude of the difference but the temporal context.

**Why D fails:**
A **single authoritative source rarely exists** for most research topics. Population data comes from censuses, estimates, and projections from multiple organizations, each with different methodologies and collection dates.

### Key Decision Framework
**Require temporal metadata (publication dates, data collection dates) in all structured outputs from subagents. Instruct synthesis agents to evaluate whether discrepancies reflect temporal differences before flagging them as contradictions.**
</details>

---

## Practice Problem 7

**Your research system investigates 'renewable energy storage technologies.' The web search subagent finds extensive data on lithium-ion batteries and pumped hydro storage. The document analysis subagent finds only brief mentions of hydrogen storage and nothing on compressed air energy storage. The synthesis agent produces a confident-sounding, well-structured report that covers lithium-ion and pumped hydro thoroughly but doesn't mention the gaps in hydrogen and compressed air coverage. How should you fix this?**

A) Add more specialized subagents to ensure complete research coverage of all subtopics.

B) Have the coordinator verify that each subtopic has at least 3 independent sources before allowing synthesis to proceed.

C) Require the synthesis agent to include explicit coverage annotations distinguishing well-supported topics from those with limited or no source material, and to report gaps rather than omitting them silently.

D) Instruct subagents to perform additional searches when they find limited results on a subtopic.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: C

**Why C is correct:**
The synthesis agent should structure its output with **coverage annotations** indicating which findings are well-supported (lithium-ion: 12 sources) vs which have gaps (hydrogen: 2 brief mentions, compressed air: no data found). Silent omission of poorly-covered topics creates a **false sense of comprehensiveness**. The reader needs to know what the report covers well and where it falls short.

**Why A fails:**
More subagents may help gather additional data but **doesn't fix the reporting problem**. Even with more subagents, if the synthesis agent still silently omits gaps, the report will appear comprehensive when it isn't.

**Why B fails:**
Source minimums **block partial results unnecessarily**. Requiring 3 sources per subtopic would prevent the report from including the limited but still valuable hydrogen storage information. Partial coverage with transparency is better than no coverage.

**Why D fails:**
Instructing subagents to "search harder" **can't find information that doesn't exist** in the available sources. If compressed air energy storage data isn't available in the sources the subagents can access, additional searches won't produce it. The gap should be reported, not hidden.

### Key Decision Framework
**Synthesis agents must include coverage annotations - never silently omit topics with limited data. Distinguish well-supported findings from gaps, and report what you didn't find as explicitly as what you did find.**
</details>

---

## Key Takeaways for Domain 5

1. **Context degradation** is real - extract key facts into persistent structured blocks, don't rely on conversation history alone
2. **Lost-in-the-middle**: place summaries at the beginning of aggregated inputs with explicit section headers
3. **Trim verbose tool outputs** to only relevant fields before they consume context budget
4. **Escalation triggers**: customer requests human, policy gaps, inability to progress - NOT sentiment or self-reported confidence
5. **Multiple matches**: ask for additional identifiers, never select heuristically
6. **Conflicting sources**: annotate with attribution, never arbitrarily select one value
7. **Structured claim-source mappings**: required from subagents to preserve provenance through synthesis
8. **Scratchpad files** + `/compact` + subagent delegation manage extended session context
9. **Stratified sampling** by document type and field to validate accuracy before reducing human review
10. **Trim verbose tool outputs** via PostToolUse hooks before they consume context budget
11. **Stratified sampling** by document type/field - aggregate accuracy masks category-level problems
12. **Temporal metadata** (publication dates) prevents false contradictions between different time periods
13. **Coverage gap annotations** in synthesis reports - never silently omit poorly-covered topics
