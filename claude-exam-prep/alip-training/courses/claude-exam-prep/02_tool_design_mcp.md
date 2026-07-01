# Module 2: Tool Design & MCP Integration (18%)

## Concepts You Must Know

### 2.1 Effective Tool Descriptions
- Tool descriptions are the **primary mechanism** LLMs use for tool selection
- Minimal descriptions lead to unreliable selection among similar tools
- Include: input formats, example queries, edge cases, boundary explanations
- **Ambiguous/overlapping descriptions cause misrouting** (e.g., `analyze_content` vs `analyze_document` with near-identical descriptions)
- System prompt wording can create keyword-sensitive unintended tool associations

#### Exemplo Prático — Antes e Depois

**ANTES (ruim — causa misrouting):**
```
get_customer: "Retrieves customer information"
lookup_order:  "Retrieves order details"
```
O modelo não sabe qual chamar quando o usuário diz *"check my order #12345"* — ambas parecem válidas.

**DEPOIS (bom — seleção confiável):**
```
get_customer:
  "Retrieves customer profile by customer ID (CUS-XXXX format).
   Use for: name, email, phone, account settings, loyalty points balance.
   Do NOT use for: order status, shipping info — use lookup_order instead.
   Example queries: 'update my email', 'check my loyalty points'"

lookup_order:
  "Retrieves order details by order ID (#12345 or ORD-XXXXX).
   Use for: order status, tracking number, items ordered, delivery date, refund eligibility.
   Do NOT use for: customer profile data — use get_customer instead.
   Example queries: 'where is my order', 'check order #12345 status'"
```

> **Regra de ouro**: se dois membros da equipe discordassem sobre qual ferramenta usar para um dado input, a descrição está ruim e precisa de fronteiras explícitas.

---

### 2.2 Structured Error Responses for MCP Tools
- MCP `isError` flag communicates tool failures to the agent
- **Four error categories**: transient (timeouts), validation (invalid input), business (policy violations), permission
- Generic "Operation failed" errors prevent the agent from making appropriate recovery decisions
- **Retryable vs non-retryable**: return `isRetryable` boolean + `errorCategory` + human-readable description
- Distinguish **access failures** (needing retry) from **valid empty results** (successful query, no matches)

#### Exemplos JSON das 4 Categorias de Erro

```json
// Erro TRANSIENTE (timeout) — deve tentar novamente
{
  "status": "error",
  "errorCategory": "transient",
  "isRetryable": true,
  "message": "Search timed out after 30s",
  "attemptedQuery": "AI impact on music industry 2024",
  "partialResults": ["Artigo 1...", "Artigo 2..."],
  "alternatives": ["Tente query mais específica", "Use document analysis"]
}
```

```json
// Erro de VALIDAÇÃO — não tentar novamente (problema no input)
{
  "status": "error",
  "errorCategory": "validation",
  "isRetryable": false,
  "message": "Customer ID format invalid. Expected: CUS-XXXX",
  "receivedValue": "12345"
}
```

```json
// Erro de NEGÓCIO — não tentar novamente (regra de política)
{
  "status": "error",
  "errorCategory": "business",
  "isRetryable": false,
  "message": "Refund denied: order older than 30-day return window",
  "orderDate": "2024-01-15",
  "policyLimit": "2024-02-14"
}
```

```json
// RESULTADO VAZIO VÁLIDO — NÃO é erro, query funcionou mas não achou nada!
{
  "status": "success",
  "results": [],
  "message": "Query executed successfully. No matching orders found."
}
```

#### Tabela de Decisão: O que o Agente Deve Fazer?

| Situação                  | `isRetryable` | Ação do Agente                              |
|---------------------------|---------------|---------------------------------------------|
| Timeout de rede           | `true`        | Retry com backoff exponencial               |
| ID inválido               | `false`       | Pedir ao usuário o formato correto          |
| Política violada          | `false`       | Explicar a limitação / escalar              |
| Query sem resultados      | N/A (success) | Informar que não há resultados (sem retry)  |

> **Armadilha clássica**: retornar `results: []` com `status: "error"` faz o agente tentar recuperação desnecessária. Resultado vazio é **sucesso**, não falha.

---

### 2.3 Tool Distribution & tool_choice
- Too many tools (e.g., 18 instead of 4-5) degrades tool selection reliability
- Agents with tools outside their specialization tend to misuse them
- **Scoped tool access**: give each agent only role-relevant tools + limited cross-role tools for high-frequency needs
- `tool_choice: "auto"` - model may return text instead of calling a tool
- `tool_choice: "any"` - model MUST call a tool (guarantees structured output)
- Forced selection: `{"type": "tool", "name": "..."}` - model must call that specific tool

#### Comparativo Visual: tool_choice

```
tool_choice: "auto"
  ┌─────────────────────────────────────────────────────┐
  │ Modelo PODE retornar texto OU chamar uma ferramenta │
  │ Risco: responde em prosa quando ferramenta é        │
  │        necessária para output estruturado           │
  └─────────────────────────────────────────────────────┘

tool_choice: "any"
  ┌─────────────────────────────────────────────────────┐
  │ Modelo DEVE chamar alguma ferramenta                │
  │ Garante output estruturado (JSON)                   │
  │ Útil: extração de dados, quando JSON é obrigatório  │
  └─────────────────────────────────────────────────────┘

tool_choice: {"type": "tool", "name": "extract_metadata"}
  ┌─────────────────────────────────────────────────────┐
  │ Modelo DEVE chamar ESSA ferramenta específica       │
  │ Útil: quando você sabe exatamente qual usar         │
  │ Garante schema correto sem ambiguidade              │
  └─────────────────────────────────────────────────────┘
```

---

### 2.4 MCP Server Integration
- **Project-level** `.mcp.json` for shared team tooling (version controlled)
- **User-level** `~/.claude.json` for personal/experimental servers
- Environment variable expansion (e.g., `${GITHUB_TOKEN}`) for credential management without committing secrets
- Tools from ALL configured MCP servers are discovered at connection time and available simultaneously
- **MCP resources**: content catalogs (issue summaries, database schemas) to reduce exploratory tool calls

#### Estrutura de Arquivos: Onde Cada Configuração Vai

```
projeto/                          ← repositório git
├── .mcp.json                     ← COMPARTILHADO: versionado, todos os devs recebem
│                                    configuração do servidor GitHub da equipe
├── .claude/
│   └── CLAUDE.md                 ← contexto e instruções do projeto
└── src/
    └── ...

~/ (home do usuário)              ← NÃO versionado, só seu
└── .claude.json                  ← PESSOAL: servidor Jira experimental, só você usa
```

#### Exemplo de `.mcp.json` Correto

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

> `${GITHUB_TOKEN}` é expandido do ambiente de cada desenvolvedor — o token **nunca entra no repositório**.

#### O que NUNCA Fazer

```json
// ERRADO — nunca hardcode credenciais no .mcp.json!
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "ghp_abc123xyz789..."
      }
    }
  }
}
// Qualquer pessoa com acesso ao repo (incluindo repos públicos)
// teria acesso ao seu token. SECURITY ANTI-PATTERN.
```

#### Regra de Localização

| O que é?                        | Onde vai?             | Por quê?                            |
|---------------------------------|-----------------------|-------------------------------------|
| Servidor da equipe (GitHub, Jira) | `.mcp.json` no projeto | Versionado → todos recebem automaticamente |
| Servidor experimental/pessoal   | `~/.claude.json`      | Não versionado → não polui o time   |
| Credenciais/tokens              | Variável de ambiente  | Nunca no repositório                |

---

### 2.5 Built-in Tools (Read, Write, Edit, Bash, Grep, Glob)
- **Grep**: content search (function names, error messages, import statements)
- **Glob**: file path pattern matching (find files by name or extension)
- **Read/Write**: full file operations; **Edit**: targeted modifications using unique text matching
- **Edit fallback**: when Edit fails due to non-unique matches, use Read + Write
- Build understanding incrementally: Grep to find entry points -> Read to follow imports and trace flows

#### Tabela de Seleção: Qual Ferramenta Usar?

| Necessidade                                     | Ferramenta Correta                    | Ferramenta ERRADA (e por quê)              |
|-------------------------------------------------|---------------------------------------|---------------------------------------------|
| Encontrar arquivos que **importam** um módulo   | **Grep** — busca conteúdo do arquivo  | Glob — só encontra pelo nome do arquivo     |
| Encontrar todos os arquivos `.test.ts`          | **Glob** `**/*.test.ts`               | Grep — busca dentro do conteúdo, não nomes |
| Editar uma função específica (texto único)      | **Edit** — modificação pontual        | Write — reescreve o arquivo inteiro         |
| Edit falha (texto não é único no arquivo)       | **Read + Write** — lê tudo, reescreve | Bash com `sed` — não use Bash para isso     |
| Executar testes após mudança                    | **Bash** — único que executa comandos | Read — apenas lê, não executa               |
| Buscar todos os usos de `legacy_auth`           | **Grep** com pattern `legacy_auth`    | Glob `**/*legacy_auth*` — busca nome, não conteúdo |

#### Fluxo de Exploração de Codebase (passo a passo)

```
Objetivo: entender e modificar AuthService

1. GREP "AuthService"
   └─→ encontra entry point em auth/service.py (linha 42)
           │
           ▼
2. READ auth/service.py
   └─→ entende a classe, seus imports e dependências
           │
           ▼
3. GREP "from auth.service import"
   └─→ rastreia todos os módulos que consomem AuthService
           │
           ▼
4. READ arquivos consumidores (ex: api/routes.py, middleware/auth.py)
   └─→ entende o fluxo completo de chamadas
           │
           ▼
5. EDIT auth/service.py (ou arquivo correto)
   └─→ faz a mudança com contexto completo e seguro
```

> **Anti-pattern**: usar `READ` diretamente em arquivos aleatórios sem GREP primeiro desperdiça tokens e perde o contexto do fluxo.

---

## Scenario: Developer Productivity Tools

You're building developer productivity tools using the Claude Agent SDK. The agent helps engineers explore unfamiliar codebases, understand legacy systems, generate boilerplate code, and automate repetitive tasks. It uses built-in tools (Read, Write, Bash, Grep, Glob) and integrates with MCP servers.

---

## Practice Problem 1

**Production logs show the agent frequently calls `get_customer` when users ask about orders (e.g., "check my order #12345"), instead of calling `lookup_order`. Both tools have minimal descriptions ("Retrieves customer information" / "Retrieves order details") and accept similar identifier formats. What's the most effective first step to improve tool selection reliability?**

A) Add few-shot examples to the system prompt demonstrating correct tool selection patterns, with 5-8 examples showing order-related queries routing to `lookup_order`.

B) Consolidate both tools into a single `lookup_entity` tool that accepts any identifier and internally determines which backend to query.

C) Implement a routing layer that parses user input before each turn and pre-selects the appropriate tool based on detected keywords and identifier patterns.

D) Expand each tool's description to include input formats, example queries, edge cases, and boundaries explaining when to use it versus similar alternatives.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: D

**Why D is correct:**
Tool descriptions are the **primary mechanism LLMs use for tool selection**. When descriptions are minimal, models lack the context to differentiate between similar tools. Expanding descriptions is a **low-effort, high-leverage fix** that directly addresses the root cause. For example:

Before: `"Retrieves order details"`
After: `"Retrieves order details by order ID (format: #12345 or 12345). Use this tool when the user asks about order status, shipping, items ordered, or order history. Do NOT use for customer profile information like name, email, or account settings - use get_customer for those."`

**Why A fails:**
Few-shot examples add token overhead without fixing the underlying issue. They're a workaround for bad descriptions, not a fix for them.

**Why C fails:**
A routing layer is over-engineered and bypasses the LLM's natural language understanding - exactly the capability you want to leverage.

**Why B fails:**
Consolidation is a valid architectural choice but requires more effort than simply improving descriptions. It's a "first step" question - fix the low-hanging fruit first.

### Key Decision Framework
**When tools are confused, improve descriptions first. Descriptions are the cheapest, most direct fix for tool selection problems.**
</details>

---

## Practice Problem 2

**The web search subagent times out while researching a complex topic. You need to design how this failure information flows back to the coordinator agent. Which error propagation approach best enables intelligent recovery?**

A) Return structured error context to the coordinator including the failure type, the attempted query, any partial results, and potential alternative approaches.

B) Implement automatic retry logic with exponential backoff within the subagent, returning a generic "search unavailable" status only after all retries are exhausted.

C) Catch the timeout within the subagent and return an empty result set marked as successful.

D) Propagate the timeout exception directly to a top-level handler that terminates the entire research workflow.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
Structured error context gives the coordinator everything it needs to make intelligent recovery decisions:
```json
{
  "status": "error",
  "errorCategory": "transient",
  "isRetryable": true,
  "attemptedQuery": "AI impact on music industry 2024",
  "partialResults": ["Found 3 articles before timeout..."],
  "alternatives": ["Try narrower query", "Use document analysis instead"]
}
```
The coordinator can then decide: retry with a modified query, try an alternative approach, or proceed with partial results.

**Why B fails:**
The generic "search unavailable" status hides valuable context from the coordinator. It can't distinguish between "timed out on a broad query" (try narrower) vs "service is down" (skip this source entirely).

**Why C fails:**
Silently suppressing errors by returning empty results as success is an **anti-pattern**. The coordinator thinks the search succeeded and found nothing, so it won't attempt recovery.

**Why D fails:**
Terminating the entire workflow for a single subagent failure is disproportionate. Other subagents may have succeeded, and the coordinator could produce a useful partial report.

### Key Decision Framework
**Errors should carry structured context (type, what was attempted, partial results, alternatives) so the coordinator can make informed recovery decisions. Never hide failures or terminate entire workflows for single-agent errors.**
</details>

---

## Practice Problem 3

**During testing, you observe that the synthesis agent frequently needs to verify specific claims while combining findings. Currently, it returns control to the coordinator, which invokes the web search agent, then re-invokes synthesis. This adds 2-3 round trips per task and increases latency by 40%. 85% of verifications are simple fact-checks (dates, names, statistics) while 15% require deeper investigation. What's the most effective approach to reduce overhead while maintaining reliability?**

A) Give the synthesis agent a scoped `verify_fact` tool for simple lookups, while complex verifications continue delegating to the web search agent through the coordinator.

B) Have the synthesis agent accumulate all verification needs and return them as a batch to the coordinator, which sends them all to the web search agent at once.

C) Give the synthesis agent access to all web search tools so it can handle any verification need directly without round-trips through the coordinator.

D) Have the web search agent proactively cache extra context around each source during initial research, anticipating what the synthesis agent might need to verify.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
This applies the **principle of least privilege** - give the synthesis agent only what it needs for the 85% common case (simple fact verification) while preserving the existing coordination pattern for the 15% complex cases. A scoped `verify_fact` tool is narrower than full web search, preventing cross-specialization misuse.

**Why B fails:**
Batching creates blocking dependencies - synthesis steps may depend on earlier verified facts. You can't batch when results feed into subsequent synthesis decisions.

**Why C fails:**
Giving the synthesis agent ALL web search tools over-provisions it, violating separation of concerns. It would have tools outside its specialization that it might misuse.

**Why D fails:**
Speculative caching relies on predicting what the synthesis agent will need to verify, which is unreliable. It wastes resources caching context that may never be needed.

### Key Decision Framework
**When a subagent needs limited cross-role capabilities, provide a scoped tool for the common case rather than full access to another agent's toolset. Preserve the coordinator pattern for complex cases.**
</details>

---

## Practice Problem 4

**Your team uses a shared GitHub MCP server for issue tracking and you personally use an experimental Jira MCP server for testing. The GitHub server requires a GITHUB_TOKEN credential that each developer sets in their environment. Where should each server be configured, and how should the credential be handled?**

A) GitHub server in project-scoped `.mcp.json` with `${GITHUB_TOKEN}` environment variable expansion; Jira server in user-scoped `~/.claude.json` since it's personal/experimental.

B) Both in `.mcp.json` in the project root with the token value hardcoded for simplicity.

C) Both in `~/.claude.json` to keep all MCP configuration in one place.

D) GitHub server in CLAUDE.md as a connection instruction; Jira in `.mcp.json`.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
Project-level `.mcp.json` is the right place for shared team tooling because it's version controlled and available to all developers who clone the repo. Using `${GITHUB_TOKEN}` environment variable expansion keeps the credential out of the repository while letting each developer supply their own token. The Jira server belongs in user-scoped `~/.claude.json` because it's a personal/experimental tool that other team members don't need or use.

**Why B fails:**
Hardcoding token values in `.mcp.json` commits secrets to version control. This is a security anti-pattern - anyone with repo access (including public repos) would have your credentials.

**Why C fails:**
Putting the shared GitHub server in `~/.claude.json` means it won't be available to other team members. Each developer would need to manually configure it, defeating the purpose of project-level shared configuration.

**Why D fails:**
CLAUDE.md provides instructions and guidance to the agent but cannot configure MCP server connections. MCP servers must be configured in `.mcp.json` (project-level) or `~/.claude.json` (user-level). Putting the personal Jira server in `.mcp.json` would expose an experimental tool to the entire team.

### Key Decision Framework
**Shared team servers go in project-scoped `.mcp.json` (version controlled); personal/experimental servers go in user-scoped `~/.claude.json`. Always use environment variable expansion for credentials - never hardcode secrets.**
</details>

---

## Practice Problem 5

**You're designing an MCP server for a project management system. The agent needs to (a) browse available project templates and their descriptions before making decisions, and (b) create new projects from selected templates. How should you expose these two capabilities?**

A) Two tools: `list_templates` (returns template list) and `create_project` (creates from template).

B) An MCP resource for the template catalog (browsable content the agent can read) and an MCP tool for `create_project` (an action that modifies state).

C) A single `manage_projects` tool that accepts a mode parameter: "list" or "create".

D) Resources for both capabilities, since the agent only needs to read information.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
MCP resources are designed for content catalogs - static or read-only data like issue summaries, documentation hierarchies, and database schemas. They give agents visibility into available data without requiring exploratory tool calls. Template browsing is exactly this kind of catalog: the agent reads through available templates and their descriptions to inform its decisions. MCP tools are for actions that modify state. Creating a project from a template changes the system, so it belongs as a tool with explicit parameters and confirmation.

**Why A fails:**
Using a tool for `list_templates` works functionally but misses the semantic distinction MCP provides. A tool implies an action; browsing a catalog is passive content consumption. Using a resource for the template catalog gives the agent a more natural way to explore available options and reduces unnecessary tool calls.

**Why C fails:**
Combining read and write operations into a single tool with a mode parameter conflates two fundamentally different operations. It makes the tool description harder to write clearly, increases the risk of accidental project creation when the agent only intended to browse, and violates the principle of giving tools a single clear purpose.

**Why D fails:**
Resources are read-only content - you cannot create a project through a resource. Project creation modifies state and requires explicit parameters (template ID, project name, configuration), which is exactly what MCP tools are designed for.

### Key Decision Framework
**MCP resources are for content catalogs (read-only browsing of available data); MCP tools are for actions that modify state. Match the MCP primitive to the operation type: reading/browsing = resource, creating/updating/deleting = tool.**
</details>

---

## Practice Problem 6

**You need to find all files in a large Python codebase that import a deprecated authentication module called `legacy_auth`. There could be various import patterns: `import legacy_auth`, `from legacy_auth import ...`, or even dynamic imports. Which of Claude Code's built-in tools is the most appropriate choice?**

A) The Glob tool with the pattern `**/*legacy_auth*` to find files with that name.

B) The Grep tool to search for the pattern `legacy_auth` across the codebase, which will find it in import statements regardless of import style.

C) The Bash tool to run `find . -name '*.py' -exec grep -l legacy_auth {} \;`.

D) Use Read on each Python source file in sequence and scan for the import statement.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
Grep is the built-in tool designed for searching file contents. It will find `legacy_auth` wherever it appears - in `import legacy_auth`, `from legacy_auth import authenticate`, `importlib.import_module('legacy_auth')`, or even in comments referencing the module. It searches across the entire codebase efficiently and returns matching files regardless of the specific import pattern used.

**Why A fails:**
Glob matches file path patterns, not file contents. The pattern `**/*legacy_auth*` would find files *named* `legacy_auth.py` or `legacy_auth_utils.py`, but it would completely miss the hundreds of files that *import* the module. This is a fundamental confusion between file name matching (Glob) and content searching (Grep).

**Why C fails:**
While `find` + `grep` via Bash would produce correct results, you should not use Bash to run grep commands when the dedicated Grep tool exists. The built-in Grep tool is optimized for correct permissions and access, provides structured output, and integrates properly with the agent's workflow.

**Why D fails:**
Reading each Python file individually is impractical at scale. In a large codebase with thousands of files, you'd need to know which files to read first - which is the exact problem you're trying to solve. This approach would consume enormous context and time compared to a single Grep call.

### Key Decision Framework
**Grep for content search (what's inside files), Glob for file name patterns (finding files by name or extension). Don't confuse them - they solve fundamentally different problems. Always prefer built-in tools over equivalent Bash commands.**
</details>

---

## Key Takeaways for Domain 2

1. **Tool descriptions are the #1 lever** for fixing tool selection - improve them before adding infrastructure
2. **Structured error responses** with `errorCategory`, `isRetryable`, and partial results enable intelligent recovery
3. **Scope tool access** - give agents only role-relevant tools + limited cross-role tools for high-frequency needs
4. **MCP servers**: project-level `.mcp.json` (shared) vs user-level `~/.claude.json` (personal)
5. **Environment variables** in `.mcp.json` for credentials - never commit secrets
6. **Access failures != empty results** - always distinguish between errors and legitimate "no matches" responses
7. **Built-in tool selection**: Grep for content search, Glob for file patterns, Edit for targeted changes, Read+Write as Edit fallback
8. **MCP resources** for content catalogs (read-only browsing); **MCP tools** for actions that modify state
9. **Project .mcp.json** for shared team servers (version controlled); **~/.claude.json** for personal servers
10. **Grep** for content search, **Glob** for file name patterns - don't confuse them
