# Module 4: Prompt Engineering & Structured Output (20%)

## Concepts You Must Know

### 4.1 Explicit Criteria to Reduce False Positives
- Explicit criteria outperform vague instructions (e.g., "flag comments only when claimed behavior contradicts actual code behavior" vs "check that comments are accurate")
- General instructions like "be conservative" or "only report high-confidence findings" fail compared to specific categorical criteria
- **High false positive rates destroy developer trust** - even in accurate categories, trust erodes from adjacent false positives
- Write review criteria that define what to report (bugs, security) vs skip (minor style, local patterns)

#### Exemplo Prático: Instrução Vaga vs Critério Explícito

**ANTES (instrução vaga — alta taxa de falso positivo):**
```
"Verifique se os comentários são precisos e esteja
conservador ao reportar problemas."
```

**DEPOIS (critério explícito — falso positivos eliminados):**
```
"Reporte um problema de comentário SOMENTE quando:
  ✅ O comportamento descrito no comentário contradiz o código real
  ✅ Um parâmetro documentado não existe na assinatura da função
  ✅ O valor de retorno descrito difere do que o código retorna

NÃO reporte:
  ❌ Comentários com estilo informal mas semanticamente corretos
  ❌ Nomes de variáveis que não seguem o padrão da equipe
  ❌ Funções sem documentação (ausência ≠ erro)"
```

> **Regra do exame:** Quando a questão apresenta alta taxa de falso positivo, a solução é SEMPRE trocar instruções vagas por critérios categóricos explícitos.

---

### 4.2 Few-Shot Prompting
- **Most effective technique** for achieving consistently formatted, actionable output when descriptions alone produce inconsistent results
- Few-shot examples demonstrate **ambiguous-case handling** (e.g., which tool to select for ambiguous requests)
- Examples enable the model to **generalize judgment** to novel patterns rather than just matching pre-specified cases
- Effective for **reducing hallucination** in extraction tasks (informal measurements, varied document structures)
- Include 2-4 examples that show reasoning for why one action was chosen over plausible alternatives

#### Exemplo Estruturado de Few-Shot para Extração Médica

```
System: "Você é um assistente de extração de dados médicos..."

Exemplos no prompt:

Exemplo 1:
  Input:  "Paciente pesa aproximadamente 180 libras, tem cerca de 5 pés e 10 pol."
  Output: {"weight_lbs": 180, "approximate": true, "height_cm": 177.8}
  Raciocínio: "approximate: true" captura a incerteza sem perder o dado

Exemplo 2:
  Input:  "Peso: 75kg"
  Output: {"weight_lbs": 165.3, "approximate": false, "height_cm": null}
  Raciocínio: null quando informação ausente (não fabricar!)

Exemplo 3:
  Input:  "Ela é bem alta, uns 6 pés"
  Output: {"weight_lbs": null, "approximate": null, "height_cm": 182.9}
  Raciocínio: "bem alta" não tem peso implícito — não fabricar peso

[Agora processe:] "Paciente de uns 90kg, altura não informada"
```

#### Quando Usar Few-Shot

| Problema | Solução |
|----------|---------|
| Output inconsistente após instruções detalhadas | Few-shot com exemplos de input→output exato |
| Seleção errada entre ferramentas similares | Few-shot mostrando qual query → qual tool |
| Formatação que prosa não descreve bem | Few-shot com exemplos do formato desejado |
| Casos ambíguos não cobertos por regras | Few-shot demonstrando o julgamento correto |

---

### 4.3 Structured Output via tool_use and JSON Schemas
- `tool_use` with JSON schemas is the **most reliable approach** for guaranteed schema-compliant output
- `tool_choice: "auto"` - model MAY return text instead of calling a tool
- `tool_choice: "any"` - model MUST call a tool but can choose which
- **Forced tool selection**: `{"type": "tool", "name": "extract_metadata"}` - model must call that specific tool
- Strict JSON schemas eliminate **syntax errors** but NOT **semantic errors** (values in wrong fields, line items that don't sum)
- Schema design: **required vs optional** fields, enum with `"other"` + detail string, **nullable fields** for absent information (prevents fabrication)
- Include format normalization rules in prompts alongside strict output schemas

#### Exemplo Completo: Schema com Campos Nullable

```python
# Definição de ferramenta para extração de nota fiscal
extract_invoice_tool = {
    "name": "extract_invoice",
    "description": "Extrai dados estruturados de uma nota fiscal",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Número da nota fiscal"
            },
            "total_amount": {
                "type": "number",
                "description": "Valor total em reais"
            },
            "purchase_order": {
                "type": ["string", "null"],  # nullable: pode não existir
                "description": "Número do PO, null se ausente no documento"
            },
            "line_items": {
                "type": ["array", "null"],   # nullable: invoices sem itemização
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity":    {"type": "number"},
                        "unit_price":  {"type": "number"}
                    }
                }
            }
        },
        "required": ["invoice_number", "total_amount"]  # apenas os sempre presentes
    }
}

# Chamada com tool_choice forçado (garante output estruturado)
response = client.messages.create(
    model="claude-opus-4-8",
    tools=[extract_invoice_tool],
    tool_choice={"type": "tool", "name": "extract_invoice"},  # DEVE chamar essa tool
    messages=[{"role": "user", "content": invoice_text}]
)
```

#### Os 3 Modos de `tool_choice`

| Modo | Código | Comportamento | Quando usar |
|------|--------|---------------|-------------|
| Auto | `"auto"` | Pode retornar texto OU chamar tool | Conversas gerais com tools opcionais |
| Any | `"any"` | DEVE chamar alguma tool | Output estruturado obrigatório |
| Específico | `{"type": "tool", "name": "X"}` | DEVE chamar exatamente essa tool | Quando você sabe qual tool usar |

> **Armadilha do exame:** `tool_choice: "any"` garante que uma tool seja chamada, mas NÃO garante que seja a correta. Use o modo específico quando precisar de uma tool exata.

> **Sintaxe vs Semântica:** JSON schema elimina erros de sintaxe (formato inválido, tipos errados), mas NÃO garante que os valores estejam nos campos certos ou que os totais batam. Validação semântica ainda é necessária.

---

### 4.4 Validation, Retry, and Feedback Loops
- **Retry-with-error-feedback**: append specific validation errors to the prompt on retry to guide correction
- **Retries are ineffective** when info is simply absent from the source document (vs format/structural errors)
- `detected_pattern` field in findings enables systematic analysis of false positive patterns
- **Semantic vs syntax errors**: tool_use eliminates syntax errors; semantic errors (wrong values, misplaced fields) require validation logic
- Self-correction validation: extract `calculated_total` alongside `stated_total` to flag discrepancies

#### Diagrama: Ciclo de Retry-with-Error-Feedback

```
┌──────────────────────────────────────────────┐
│   Documento de entrada → Extração inicial    │
└─────────────────────┬────────────────────────┘
                      ↓
              Validação do output
                /           \
           VÁLIDO           INVÁLIDO
              ↓                 ↓
         Aceitar         Erro é de ESTRUTURA/FORMATO?
                           /               \
                         SIM               NÃO (info ausente)
                          ↓                     ↓
             Retry com mensagem            Tornar campo
             de erro específica            nullable no schema
             ──────────────────            ──────────────────
             "Os line_items estão          Não adianta tentar
             em ordem errada.              de novo — o dado
             Reordene conforme             não existe no
             aparecem no doc."             documento!
                          ↓
             Nova extração (corrige o erro estrutural)
```

#### Distinção Crítica: Quando Retry Funciona

| Tipo de Erro | Exemplo | Retry funciona? | Solução correta |
|--------------|---------|:---------------:|-----------------|
| Estrutural/formato | Itens na ordem errada | ✅ SIM | Retry com feedback do erro específico |
| Informação ausente | Endereço não está no doc | ❌ NÃO | Campo nullable no schema |
| Semântico | Valor no campo errado | ✅ Às vezes | Retry + validação cruzada |

---

### 4.5 Batch Processing Strategies
- **Message Batches API**: 50% cost savings, up to 24-hour processing window, no guaranteed latency SLA
- **Appropriate for**: non-blocking, latency-tolerant workloads (overnight reports, weekly audits, nightly test generation)
- **Inappropriate for**: blocking workflows (pre-merge checks)
- No multi-turn tool calling within a single batch request
- `custom_id` fields for correlating batch request/response pairs
- Handle failures by resubmitting only failed documents (identified by `custom_id`) with modifications

#### Árvore de Decisão: Síncrono vs Batch

```
DECISÃO: API Síncrona vs Message Batches API

┌──────────────────────────────────────────────────────────┐
│  A tarefa BLOQUEIA o usuário/fluxo enquanto processa?   │
└───────────────────────┬──────────────────────────────────┘
                        │
              SIM ──────┴────── NÃO
               ↓                  ↓
    API SÍNCRONA           Message Batches API
    (chamada normal)       (50% custo, até 24h)

    Exemplos SIM:          Exemplos NÃO:
    ✅ Pre-merge check     ✅ Relatório noturno de dívida técnica
    ✅ Chat interativo     ✅ Auditoria semanal de contratos
    ✅ Resposta ao user    ✅ Geração noturna de testes
    ❌ Relatório diário    ❌ Check pré-merge (bloqueia developer)
```

#### Características da Message Batches API para o Exame

```
Message Batches API — O que saber:
├── 50% de redução de custo vs chamadas síncronas
├── Janela de processamento: ATÉ 24 HORAS (sem SLA de latência)
├── SEM suporte a multi-turn tool calling num único batch request
├── custom_id: correlaciona cada request com seu response
└── Falhas: identifique pelo custom_id, resubmita SOMENTE os falhos
            com modificações (ex: chunking para docs que excederam contexto)
```

---

### 4.6 Multi-Instance and Multi-Pass Review
- **Self-review limitations**: model retains reasoning context from generation, less likely to question its own decisions
- **Independent review instances** (without prior reasoning context) are more effective at catching subtle issues
- **Multi-pass review**: split large reviews into per-file local analysis + cross-file integration passes
- Attention dilution: processing many files at once produces inconsistent, contradictory feedback
- Verification passes where model self-reports confidence alongside each finding enable calibrated review routing

#### Diagrama: Atenção Diluída vs Multi-Pass

```
PROBLEMA: Revisão de PR com 14 arquivos em um único pass

Pass Único (atenção diluída):
┌──────────────────────────────────────────────────────┐
│ Arquivo 1:  ████████ (análise completa)              │
│ Arquivo 2:  █████░░░ (análise parcial)               │
│ Arquivo 3:  ███░░░░░ (atenção caindo...)             │
│ ...                                                  │
│ Arquivo 14: ░░░░░░░░ (quase ignorado)                │
└──────────────────────────────────────────────────────┘
Resultado: Feedback inconsistente, contradições entre arquivos

──────────────────────────────────────────────────────

SOLUÇÃO: Multi-Pass Review

Pass 1 — Análise LOCAL por arquivo (podem rodar em paralelo):
┌────────────┐  ┌────────────┐  ┌────────────┐
│ Arquivo 1  │  │ Arquivo 2  │  │ Arquivo N  │
│ ████████   │  │ ████████   │  │ ████████   │
│ bugs locais│  │ bugs locais│  │ bugs locais│
└─────┬──────┘  └──────┬─────┘  └──────┬─────┘
      └─────────────────┴───────────────┘
                        ↓
Pass 2 — Análise de INTEGRAÇÃO (cross-file):
┌──────────────────────────────────────────────┐
│ Fluxo de dados entre módulos                 │
│ Consistência de interfaces                   │
│ Padrões e anti-padrões transversais          │
└──────────────────────────────────────────────┘
Resultado: Profundidade uniforme + visão de integração
```

#### Self-Review Bias: Por Que Instâncias Independentes São Melhores

| Abordagem de Revisão | Eficácia | Por quê |
|----------------------|:--------:|---------|
| Mesma sessão que gerou o código | Baixa | Contexto de raciocínio ainda ativo — modelo questiona menos suas próprias decisões |
| Sessão independente (sem histórico de geração) | Alta | Vê o código como novo — detecta issues que o autor ignoraria |
| Múltiplas instâncias independentes em consenso | Alta | Filtra ruído, diferentes perspectivas convergem em problemas reais |

---

## Scenario: Structured Data Extraction System

You're building a structured data extraction system using Claude. The system extracts information from unstructured documents, validates output using JSON schemas, and maintains high accuracy. It must handle edge cases gracefully and integrate with downstream systems.

---

## Practice Problem 1

**Your team wants to reduce API costs for automated analysis. Real-time Claude calls power two workflows: (1) a blocking pre-merge check that must complete before developers can merge, and (2) a technical debt report generated overnight for review the next morning. Your manager proposes switching both to the Message Batches API for its 50% cost savings. How should you evaluate this proposal?**

A) Switch both workflows to batch processing with status polling to check for completion.

B) Use batch processing for the technical debt reports only; keep real-time calls for pre-merge checks.

C) Keep real-time calls for both workflows to avoid batch result ordering issues.

D) Switch both to batch processing with a timeout fallback to real-time if batches take too long.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
The Message Batches API offers 50% cost savings but has processing times **up to 24 hours** with no guaranteed latency SLA. This makes it:
- **Perfect for** overnight technical debt reports (non-blocking, latency-tolerant)
- **Unsuitable for** pre-merge checks where developers are waiting to merge (blocking workflow)

Match the API to the workflow's latency requirements.

**Why A fails:**
"Often faster" completion isn't acceptable for blocking workflows. Developers waiting 5 minutes for a merge check is fine; waiting 4 hours is not, and batch processing can't guarantee the former.

**Why C fails:**
This wastes the 50% cost savings on the overnight reports that don't need real-time processing. The batch API was designed for exactly this use case.

**Why D fails:**
Adds unnecessary complexity. The simpler solution is using each API for what it's designed for.

### Key Decision Framework
**Blocking workflows = synchronous API. Non-blocking, latency-tolerant workflows = batch API. Don't compromise either for a uniform approach.**
</details>

---

## Practice Problem 2

**A pull request modifies 14 files across the stock tracking module. Your single-pass review analyzing all files together produces inconsistent results: detailed feedback for some files but superficial comments for others, obvious bugs missed, and contradictory feedback - flagging a pattern as problematic in one file while approving identical code elsewhere. How should you restructure the review?**

A) Run three independent review passes on the full PR and only flag issues that appear in at least two of the three runs.

B) Require developers to split large PRs into smaller submissions of 3-4 files before automated review runs.

C) Switch to a higher-tier model with a larger context window to give all 14 files adequate attention in one pass.

D) Split into focused passes: analyze each file individually for local issues, then run a separate integration-focused pass examining cross-file data flow.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: D

**Why D is correct:**
The root cause is **attention dilution** when processing many files at once. Splitting into focused passes directly addresses this:
1. **Per-file local analysis**: each file gets full attention for bugs, patterns, style
2. **Cross-file integration pass**: examines data flow, interface consistency, and patterns across files

This ensures consistent depth per file while still catching cross-file issues.

**Why B fails:**
Shifts burden to developers without improving the review system. Sometimes 14 files genuinely belong in one PR.

**Why C fails:**
Larger context windows don't solve attention quality issues. The model has enough context to see all 14 files - it just can't maintain consistent attention across all of them simultaneously.

**Why A fails:**
Would suppress detection of real bugs that happen to appear in only one of three runs. Consensus-based filtering reduces both false positives AND true positives.

### Key Decision Framework
**For large multi-file reviews: split into per-file local passes + a cross-file integration pass. This eliminates attention dilution while preserving cross-file analysis.**
</details>

---

## Practice Problem 3

**You're designing a JSON schema for extracting invoice data from diverse document formats. Some invoices include a purchase order number, others don't. Some list individual line items, others only show totals. Your current schema with all required fields causes the model to fabricate purchase order numbers when they don't exist in the source document. How should you redesign the schema?**

A) Add a preprocessing step that classifies document type and selects the appropriate schema variant.

B) Add a `confidence` field next to each extracted value so reviewers can identify likely fabrications.

C) Make fields like `purchase_order` optional (nullable) so the model returns `null` when the information doesn't exist in the source document, preventing fabrication.

D) Add instructions in the prompt telling the model to leave fields blank when information is not found.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: C

**Why C is correct:**
Making fields **optional (nullable)** directly solves the fabrication problem. When the schema allows `null` for fields like `purchase_order`, the model can honestly represent "this information doesn't exist in the source" instead of being forced to fabricate a value to satisfy a required field constraint.

```json
{
  "purchase_order": {
    "type": ["string", "null"],
    "description": "PO number if present on invoice, null if not found"
  }
}
```

**Why B fails:**
Confidence scores don't prevent fabrication - they just flag it after the fact. The model may confidently fabricate a plausible-looking PO number.

**Why A fails:**
Over-engineered for this problem. Document classification adds complexity when the simpler fix is allowing nullable fields in one schema.

**Why D fails:**
Prompt instructions can't override schema constraints. If the schema requires a non-null string, the model will fill it regardless of prompt instructions.

### Key Decision Framework
**Design schemas with nullable/optional fields for information that may not exist in source documents. Required fields should only be used for data that is genuinely always present. This prevents model fabrication.**
</details>

---

## Practice Problem 4

**Your document extraction system processes medical intake forms. Simple forms extract correctly, but forms with informal measurements (e.g., 'about 180 lbs', 'around 5 foot 10') produce inconsistent output - sometimes including the qualifiers, sometimes normalizing to exact numbers, sometimes returning null. Detailed instructions specifying how to handle informal measurements haven't resolved the inconsistency. What's the most effective fix?**

A) Add schema validation rules that reject non-numeric values in measurement fields.

B) Add a preprocessing step that normalizes informal text to standard formats before extraction.

C) Add 2-4 few-shot examples showing how to handle informal measurements, e.g., 'about 180 lbs' -> `{"weight_lbs": 180, "approximate": true}`.

D) Make measurement fields optional so the model can skip ambiguous values.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: C

**Why C is correct:**
Few-shot examples are the most effective technique for achieving consistent output when detailed instructions alone produce inconsistent results. They demonstrate the exact pattern: informal input -> specific structured output, enabling the model to generalize to novel informal patterns it hasn't seen.

**Why A fails:**
Validation rules that reject non-numeric values would reject valid data. The measurements are real - they just need consistent normalization, not rejection.

**Why B fails:**
A preprocessing step is over-engineered when examples solve it directly. Adding a separate normalization pipeline introduces complexity and potential errors when the model can handle this with proper examples.

**Why D fails:**
Making fields optional loses data unnecessarily. The information exists in the source document - the problem is inconsistent extraction, not missing data.

### Key Decision Framework
**When detailed instructions produce inconsistent output, add 2-4 few-shot examples showing the exact input -> output pattern. Examples demonstrate judgment for ambiguous cases better than descriptions.**
</details>

---

## Practice Problem 5

**Your invoice extraction system has two categories of errors: (1) the `line_items` array sometimes lists items in the wrong order compared to the source document, and (2) for invoices that don't include a shipping address, the system fabricates a plausible-looking address. You implement retry-with-error-feedback for both error types, appending the specific validation error to the prompt on retry. Which error type will actually benefit from retries?**

A) Both - retrying with specific error feedback will correct all extraction errors.

B) Only the line item ordering - this is a structural error the model can self-correct when shown the specific mistake. Address fabrication won't improve because the information is simply absent from the source document.

C) Only the address fabrication - the model needs a second chance to recognize the address is missing.

D) Neither - extraction errors require schema changes, not retries.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
Retry-with-error-feedback is effective for format/structural errors (wrong ordering, format mismatches) because the model has the information but made a structural mistake it can correct. It is ineffective when information is absent from the source - no amount of retrying will produce a shipping address that doesn't exist in the document. The model fabricated because it was required to fill a field; the fix for that is making the field nullable, not retrying.

**Why A fails:**
Retries cannot conjure information that doesn't exist in the source document. The address fabrication will persist (or produce a different fabrication) on retry because the underlying problem is a required field for absent data, not a correctable mistake.

**Why C fails:**
The model didn't fail to "recognize" the address is missing - it fabricated one because the schema required a value. A second attempt with the same required field will produce another fabrication, not a null.

**Why D fails:**
Structural errors like incorrect ordering genuinely benefit from retries with specific feedback. The model has the correct data and can reorder it when told what went wrong.

### Key Decision Framework
**Retry-with-error-feedback works for structural/format errors where the model has the information but made a correctable mistake. For fabrication caused by absent data, make the field nullable instead of retrying.**
</details>

---

## Practice Problem 6

**You submit a batch of 500 contract extractions via the Message Batches API. Results arrive: 480 succeed but 20 return errors including timeouts and context length exceeded. You need to process all 500 contracts for a complete report due tomorrow morning. How should you handle the 20 failures?**

A) Resubmit the entire batch of 500 to ensure consistency across all results.

B) Identify the 20 failed items by their `custom_id` values and resubmit only those as a new batch, applying modifications where needed (e.g., chunking documents that exceeded context limits).

C) Log the failures and deliver the report with only 480 contracts, noting the 20 gaps.

D) Switch all 500 to synchronous API calls for more reliable processing.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
`custom_id` fields are specifically designed for correlating batch request/response pairs. When failures occur, identify the failed items by `custom_id` and resubmit only those with appropriate modifications (e.g., chunking oversized documents that exceeded context limits). This is efficient and preserves the 480 successful results.

**Why A fails:**
Resubmitting all 500 wastes the 480 successful results, doubles cost, and doubles processing time unnecessarily. The successful extractions don't need to be reprocessed.

**Why C fails:**
Delivering incomplete results doesn't meet the requirement of processing all 500 contracts for a complete report. The failures are recoverable with targeted resubmission.

**Why D fails:**
Switching everything to synchronous abandons the 50% cost savings for the 480 that already succeeded. It's also unnecessary - only the 20 failures need attention, and they can be resubmitted as a smaller batch with modifications.

### Key Decision Framework
**Use `custom_id` to correlate batch results and identify failures. Resubmit only failed items with appropriate modifications - don't reprocess successes or abandon batch savings.**
</details>

---

## Key Takeaways for Domain 4

1. **Explicit criteria > vague instructions** for review prompts - define what to report vs skip
2. **Few-shot examples** são a técnica #1 para formatação consistente e tratamento de casos ambíguos
3. **tool_use + JSON schema** = output estruturado garantido; `tool_choice: "any"` força chamada de tool
4. **Campos nullable** previnem fabricação quando dados podem estar ausentes na fonte
5. **Retry-with-error-feedback** funciona para erros de formato, NÃO para informação ausente
6. **Batch API**: 50% de economia, janela de até 24h, sem SLA de latência - apenas para workloads não-bloqueantes
7. **Multi-pass review**: análise local por arquivo + pass de integração cross-file para evitar diluição de atenção
8. **Instâncias de revisão independentes** superam auto-revisão para detectar issues sutis
9. **Few-shot examples** corrigem inconsistência que instruções detalhadas não conseguem resolver — mostre o padrão exato
10. **Retry-with-feedback** funciona para erros estruturais/formato, NÃO para informação ausente — torne campos ausentes nullable
11. **custom_id** correlaciona resultados do batch — resubmeta apenas falhas com modificações, não reprocesse sucessos
