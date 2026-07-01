# Module 3: Claude Code Configuration & Workflows (20%)

## Concepts You Must Know

### 3.1 CLAUDE.md Hierarchy
- **User-level**: `~/.claude/CLAUDE.md` - personal settings, not shared via version control
- **Project-level**: `.claude/CLAUDE.md` or root `CLAUDE.md` - shared with all team members
- **Directory-level**: subdirectory `CLAUDE.md` files - scoped to that directory
- `@import` syntax references external files to keep CLAUDE.md modular (e.g., importing standards files per package)
- `.claude/rules/` directory for topic-specific rule files as alternative to monolithic CLAUDE.md

```
HIERARQUIA DE CLAUDE.md (do mais geral para o mais específico):

~/.claude/CLAUDE.md              <- NÍVEL USUÁRIO (pessoal, não compartilhado via git)
    | sempre carregado
    v
projeto/CLAUDE.md  ou            <- NÍVEL PROJETO (compartilhado via git)
projeto/.claude/CLAUDE.md
    | carregado ao abrir o projeto
    v
projeto/frontend/CLAUDE.md       <- NÍVEL DIRETÓRIO (scoped ao subdiretório)
projeto/backend/CLAUDE.md        <- Carregado APENAS quando editando arquivos nesse dir
```

**Exemplo de uso do `@import` para eliminar duplicação:**

```markdown
# backend/CLAUDE.md
@import ../docs/standards.md     <- Importa padrões compartilhados (fonte única)

## Convenções Específicas do Backend
- Use async/await para todas operações de I/O
- Valide inputs com Pydantic antes de processar
- Log com structlog, não print()
```

**Estrutura completa de monorepo com Claude Code:**

```
monorepo/
|-- CLAUDE.md                    <- Contexto geral do projeto
|-- docs/
|   `-- standards.md             <- Padrões compartilhados (importados via @import)
|-- .claude/
|   |-- commands/                <- Comandos slash COMPARTILHADOS (versionados no git)
|   |   |-- review.md            <- /review  - checklist de code review
|   |   |-- migrate.md           <- /migrate - conversão de API
|   |   `-- deploy.md            <- /deploy  - checklist de deploy
|   |-- rules/                   <- Regras por tipo de arquivo (carregadas por glob)
|   |   |-- testing.md           <- paths: ["**/*.test.*", "**/*.spec.*"]
|   |   |-- terraform.md         <- paths: ["terraform/**/*"]
|   |   `-- api-handlers.md      <- paths: ["**/handlers/**/*.ts"]
|   `-- skills/                  <- Skills com frontmatter YAML
|       `-- migrate.md           <- context: fork, allowed-tools: [...]
|-- frontend/
|   `-- CLAUDE.md                <- @import ../docs/standards.md + convenções React
|-- backend/
|   `-- CLAUDE.md                <- @import ../docs/standards.md + convenções async
`-- infra/
    `-- CLAUDE.md                <- @import ../docs/standards.md + convenções Terraform

~/.claude/                       <- Diretório pessoal (fora do repo)
|-- CLAUDE.md                    <- Preferências pessoais do desenvolvedor
`-- commands/                    <- Comandos slash PESSOAIS (não compartilhados)
    `-- meus-atalhos.md
```

---

### 3.2 Custom Slash Commands & Skills
- **Project-scoped commands**: `.claude/commands/` (shared via version control)
- **User-scoped commands**: `~/.claude/commands/` (personal)
- **Skills**: `.claude/skills/` with `SKILL.md` files supporting frontmatter:
  - `context: fork` - run in isolated sub-agent, prevents context pollution
  - `allowed-tools` - restrict tool access during skill execution
  - `argument-hint` - prompt for required parameters when invoked without arguments
- Personal skill customization: create variants in `~/.claude/skills/` with different names

**Exemplo completo de SKILL.md com frontmatter:**

```markdown
---
# .claude/skills/migrate.md
context: fork              <- Roda em sub-agente isolado (output verbose não polui main)
allowed-tools:             <- Acesso mínimo necessário (princípio least privilege)
  - Bash                   <- Para testar endpoints após conversão
  - Read                   <- Para ler arquivos de código
  - Edit                   <- Para fazer as mudanças
argument-hint: "Versão alvo da API (ex: v3)"  <- Pede parâmetro se invocada sem args
---

# Skill: Migrar Endpoints de API

Converta o endpoint legado para o formato da nova API versão $ARGUMENTS.

1. Leia o arquivo do endpoint atual com Read
2. Aplique as transformações de formato com Edit
3. Teste o endpoint convertido com Bash
4. Reporte o resultado ao usuário
```

**Tabela de opções de frontmatter para Skills:**

| Opção | Valores possíveis | Efeito no exame |
|-------|------------------|-----------------|
| `context` | `fork` / `main` | `fork` = sub-agente isolado; output verbose fica isolado e não polui a sessão principal |
| `allowed-tools` | lista de ferramentas | Restringe acesso ao mínimo necessário (least privilege) |
| `argument-hint` | string descritiva | Aparece como prompt se a skill for invocada sem argumentos |

---

### 3.3 Path-Specific Rules
- `.claude/rules/` files with YAML frontmatter `paths` fields for conditional activation
- Rules load **only when editing matching files** - reduces irrelevant context and token usage
- Example: `paths: ["terraform/**/*"]` loads terraform conventions only when editing terraform files
- **Advantage over directory-level CLAUDE.md**: glob patterns can target files by type across ALL directories (e.g., `**/*.test.tsx` for all test files)

**Exemplo de arquivo de regra com glob:**

```markdown
---
# .claude/rules/testing.md
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - "**/*.test.tsx"
  - "**/*.spec.tsx"
---

# Convenções de Teste

- Use describe/it blocks com descrições claras
- Mock apenas serviços externos (HTTP, banco), nunca módulos internos
- Cada arquivo testa exatamente um módulo
- Arrange-Act-Assert pattern obrigatório
```

**Diagrama comparando abordagens para convenções transversais:**

```
PROBLEMA: Convenções de teste em arquivos espalhados por todo o projeto

  frontend/components/Button.test.tsx
  frontend/pages/Home.test.tsx
  backend/services/auth.test.ts
  backend/models/user.test.ts
  infra/scripts/validate.test.ts

OPCAO RUIM: CLAUDE.md por diretório
   frontend/CLAUDE.md  (tem convencoes de teste)
   backend/CLAUDE.md   (tem convencoes de teste - duplicado!)
   infra/CLAUDE.md     (tem convencoes de teste - duplicado!)
   -> Manutencao em 3 lugares. Facil desincronizar.

OPCAO CERTA: .claude/rules/ com glob
   .claude/rules/testing.md
   paths: ["**/*.test.*", "**/*.spec.*"]
   -> Um unico arquivo cobre TODOS os testes, independente do diretório
   -> Carregado automaticamente ao editar qualquer arquivo de teste
   -> NAO carregado ao editar código de producao (contexto limpo)
```

---

### 3.4 Plan Mode vs Direct Execution
- **Plan mode**: complex tasks with large-scale changes, multiple valid approaches, architectural decisions, multi-file modifications
- **Direct execution**: simple, well-scoped changes (single-file bug fix, adding a validation check)
- Plan mode enables safe exploration and design **before committing to changes**, preventing costly rework
- **Explore subagent**: isolates verbose discovery output, returns summaries to preserve main context
- Combine: plan mode for investigation -> direct execution for implementation

**Tabela de decisão: Plan Mode vs Direct Execution**

| Tarefa | Modo correto | Razão |
|--------|-------------|-------|
| Refatorar monolito em microserviços | **Plan Mode** | Multi-arquivo, múltiplas abordagens, decisões arquiteturais |
| Corrigir bug de validação em 1 função | **Direct Execution** | Escopo claro, arquivo único |
| Adicionar campo em formulário React | **Direct Execution** | Mudança pequena e bem definida |
| Migrar ORM de SQLAlchemy para SQLModel | **Plan Mode** | Impacto transversal, múltiplas abordagens válidas |
| Adicionar endpoint REST seguindo padrão existente | **Direct Execution** | Padrão estabelecido, escopo claro |
| Redesenhar arquitetura de autenticação | **Plan Mode** | Decisões críticas, múltiplos arquivos afetados |

---

### 3.5 Iterative Refinement
- **Concrete input/output examples** are the most effective way to communicate expected transformations
- **Test-driven iteration**: write test suites first, then iterate by sharing test failures
- **Interview pattern**: have Claude ask questions to surface considerations the developer may not have anticipated
- When to provide all issues in a single message (interacting problems) vs sequentially (independent problems)

**Ciclo de refinamento iterativo (do mais simples ao mais complexo):**

```
PASSO 1: EXEMPLOS CONCRETOS (tente primeiro - mais eficaz para transformações)

  Input:  { "date": "March 15th 2024", "weight": "about 180 lbs" }
  Output: { "date": "2024-03-15", "weight_kg": 81.6, "approximate": true }

  -> Elimina ambiguidade que prosa não consegue expressar
  -> Se ainda inconsistente, vá para o passo 2

PASSO 2: TESTES PRIMEIRO (para lógica com regressão contínua)

  Escreva os testes -> execute -> compartilhe as falhas -> Claude corrige
  -> Útil quando a transformação é complexa e precisa de proteção contínua

PASSO 3: INTERVIEW PATTERN (para requisitos que você não antecipou)

  Peça ao Claude para fazer perguntas antes de implementar
  -> Superficia casos de borda e considerações que você não pensou
```

---

### 3.6 Claude Code in CI/CD Pipelines
- `-p` (or `--print`) flag for non-interactive mode in automated pipelines
- `--output-format json` and `--json-schema` for structured CI output
- CLAUDE.md provides project context (testing standards, review criteria) to CI-invoked Claude Code
- **Session context isolation**: a different Claude session should review code, not the one that generated it
- Include prior review findings when re-running after new commits to avoid duplicate comments

**Exemplos de comandos para CI/CD:**

```bash
# Modo não-interativo: flag -p é obrigatória em pipelines
claude -p "Analise este PR para problemas de segurança"

# Com output estruturado para o pipeline processar
claude -p "Revise o código e retorne findings em JSON" \
  --output-format json \
  --json-schema '{"findings": [{"file": "string", "issue": "string", "severity": "string"}]}'

# Re-execução após novo commit: passe o histórico de revisões anteriores
claude -p "Revise as mudanças. Revisões anteriores já documentadas: [lista]. Não duplique comentários existentes."
```

**Diagrama do problema de self-review bias:**

```
PROBLEMA: Claude revisando código que ela mesma gerou

Sessão A - Gerou o código          Sessão B - Revisão independente
|                                   |
|-- Raciocinou sobre a abordagem    |-- SEM contexto da geração
|-- Conhece a intenção do código    |-- Vê apenas o código resultante
|-- Menos provável questionar       |-- Mais provável detectar
|   suas próprias decisões          |   issues sutis e falhas de lógica
|                                   |
+-- REVISOR RUIM do próprio código  +-- REVISOR MAIS EFICAZ

REGRA: Use uma sessão diferente (novo processo claude -p) para revisar
       código gerado por outra sessão. Nunca autorrevisão na mesma sessão.
```

---

## Scenario: Code Generation with Claude Code

You're using Claude Code to accelerate software development. Your team uses it for code generation, refactoring, debugging, and documentation. You need to integrate it into your development workflow with custom slash commands, CLAUDE.md configurations, and understand when to use plan mode vs direct execution.

---

## Practice Problem 1

**You want to create a custom `/review` slash command that runs your team's standard code review checklist. This command should be available to every developer when they clone or pull the repository. Where should you create this command file?**

A) In the `.claude/commands/` directory in the project repository.

B) In `~/.claude/commands/` in each developer's home directory.

C) In the `CLAUDE.md` file at the project root.

D) In a `.claude/config.json` file with a `commands` array.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
Project-scoped custom slash commands belong in `.claude/commands/` within the repository. These commands are **version-controlled and automatically available** to all developers when they clone or pull the repo. This is the designed mechanism for shared team commands.

**Why B fails:**
`~/.claude/commands/` is for **personal** commands that aren't shared via version control. Every developer would need to manually create the command, and updates wouldn't propagate.

**Why C fails:**
CLAUDE.md is for project **instructions and context**, not command definitions. It's always loaded as context, which is different from an on-demand slash command.

**Why D fails:**
`.claude/config.json` with a `commands` array doesn't exist as a configuration mechanism in Claude Code.

### Key Decision Framework
**Shared team commands -> `.claude/commands/` (version controlled). Personal commands -> `~/.claude/commands/` (not shared).**
</details>

---

## Practice Problem 2

**You've been assigned to restructure the team's monolithic application into microservices. This will involve changes across dozens of files and requires decisions about service boundaries and module dependencies. Which approach should you take?**

A) Start with direct execution and make changes incrementally, letting the implementation reveal the natural service boundaries.

B) Enter plan mode to explore the codebase, understand dependencies, and design an implementation approach before making changes.

C) Use direct execution with comprehensive upfront instructions detailing exactly how each service should be structured.

D) Begin in direct execution mode and only switch to plan mode if you encounter unexpected complexity during implementation.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
Plan mode is designed for exactly this type of task: **large-scale changes, multiple valid approaches, and architectural decisions**. Monolith-to-microservices restructuring requires understanding the existing dependency graph, identifying natural service boundaries, and designing the migration path before making changes. Plan mode enables safe codebase exploration and design **before committing to changes**, preventing costly rework.

**Why A fails:**
Incremental direct execution risks costly rework when dependencies are discovered late. You might split a module into a service only to discover it has tight coupling to three other modules that also need restructuring.

**Why C fails:**
Assumes you already know the right structure without exploring the code. Service boundaries emerge from understanding the actual codebase, not from upfront prescriptions.

**Why D fails:**
The complexity is already stated in the requirements (dozens of files, service boundaries, module dependencies). Waiting for unexpected complexity to appear ignores the known complexity.

### Key Decision Framework
**Plan mode when: multi-file changes, architectural decisions, multiple valid approaches. Direct execution when: well-understood single-file changes with clear scope.**
</details>

---

## Practice Problem 3

**Your codebase has distinct areas with different coding conventions: React components use functional style with hooks, API handlers use async/await with specific error handling, and database models follow a repository pattern. Test files are spread throughout the codebase alongside the code they test. You want all tests to follow the same conventions regardless of location. What's the most maintainable way to ensure Claude automatically applies the correct conventions?**

A) Place a separate CLAUDE.md file in each subdirectory containing that area's specific conventions.

B) Consolidate all conventions in the root CLAUDE.md file under headers for each area, relying on Claude to infer which section applies.

C) Create skills in `.claude/skills/` for each code type that include the relevant conventions in their SKILL.md files.

D) Create rule files in `.claude/rules/` with YAML frontmatter specifying glob patterns to conditionally apply conventions based on file paths.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: D

**Why D is correct:**
`.claude/rules/` with glob patterns (e.g., `paths: ["**/*.test.tsx"]`) allows conventions to be **automatically applied based on file paths regardless of directory location**. This is essential for test files spread throughout the codebase - a single rule file with `**/*.test.*` matches all test files everywhere.

Example rule file `.claude/rules/testing.md`:
```yaml
---
paths: ["**/*.test.*", "**/*.spec.*"]
---
# Testing Conventions
- Use describe/it blocks with clear descriptions
- Mock external services, not internal modules
- Each test file tests exactly one module
```

**Why B fails:**
Relying on Claude to infer which section of a large CLAUDE.md applies is non-deterministic. It may apply API conventions to test files or vice versa.

**Why C fails:**
Skills require manual invocation. The question asks for "automatic" application of conventions, which skills don't provide.

**Why A fails:**
Directory-level CLAUDE.md files can't handle files spread across many directories. You'd need a CLAUDE.md in every directory that contains test files, creating maintenance burden and duplication.

### Key Decision Framework
**For conventions that apply to file types regardless of location, use `.claude/rules/` with glob patterns. For directory-specific context, use subdirectory CLAUDE.md files.**
</details>

---

## Practice Problem 4

**Your pipeline script runs `claude "Analyze this pull request for security issues"` but the job hangs indefinitely. Logs indicate Claude Code is waiting for interactive input. What's the correct approach to run Claude Code in an automated pipeline?**

A) Set the environment variable `CLAUDE_HEADLESS=true` before running the command.

B) Add the `-p` flag: `claude -p "Analyze this pull request for security issues"`

C) Redirect stdin from /dev/null: `claude "Analyze this pull request..." < /dev/null`

D) Add the `--batch` flag: `claude --batch "Analyze this pull request..."`

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: B

**Why B is correct:**
The `-p` (or `--print`) flag is the **documented way** to run Claude Code in non-interactive mode. It processes the prompt, outputs the result to stdout, and exits without waiting for user input - exactly what CI/CD pipelines require.

**Why A, C, D fail:**
These reference non-existent features (`CLAUDE_HEADLESS`, `--batch`) or Unix workarounds that don't properly address Claude Code's command syntax.

### Key Decision Framework
**For CI/CD: `-p` for non-interactive execution, `--output-format json` + `--json-schema` for machine-parseable structured output.**
</details>

---

## Practice Problem 5

**Your monorepo has shared coding standards in a central `docs/standards.md` file. Three packages (`frontend/`, `backend/`, `infra/`) each need those shared standards plus their own package-specific conventions. Currently, each package's CLAUDE.md duplicates the shared standards, creating a maintenance burden when standards change. How should you eliminate the duplication?**

A) Move all standards to the root CLAUDE.md and remove the package-level files entirely.

B) Create a symbolic link from each package directory to the shared standards file.

C) Create a `.claude/rules/` file with paths matching all three packages to inject shared standards.

D) Use `@import` in each package's CLAUDE.md to reference the shared standards file, while keeping package-specific conventions local in each file.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: D

**Why D is correct:**
`@import` keeps CLAUDE.md modular by referencing external files - each package imports the shared standards and adds its own conventions. When standards change, you update `docs/standards.md` once and all three packages pick up the change automatically. Each package retains its own CLAUDE.md for package-specific context.

**Why A fails:**
Moving everything to the root CLAUDE.md loses package-specific context. Each package has its own conventions that only apply within that directory - flattening into root means all context is loaded everywhere, even when irrelevant.

**Why C fails:**
`.claude/rules/` is designed for conditional loading based on file patterns (e.g., `paths: ["**/*.test.*"]`), not for modularity or sharing standards across packages. Rules files activate when editing matching files, which is a different mechanism than importing shared content.

**Why B fails:**
Symbolic links are not a Claude Code configuration mechanism. Claude Code reads CLAUDE.md files based on its hierarchy system - symlinks would create confusion about which directory's context is active and are not a supported pattern.

### Key Decision Framework
**Use `@import` to share common standards across multiple CLAUDE.md files. Keep package-specific conventions local in each file. Single source of truth for shared content, distributed ownership for local context.**
</details>

---

## Practice Problem 6

**You're creating a `/migrate` skill that converts legacy API endpoints to a new format. The skill needs to run shell commands to test each endpoint after conversion, but it generates extensive verbose intermediate output that would pollute the main conversation context. It also requires the target API version as input. Which SKILL.md frontmatter configuration is correct?**

A) `context: fork`, with no `allowed-tools` restriction

B) `context: main`, `allowed-tools: ["Bash", "Read", "Edit"]`, `argument-hint: "Target API version"`

C) `context: fork`, `allowed-tools: ["Bash", "Read", "Edit"]`, `argument-hint: "Target API version (e.g., v3)"`

D) `context: fork`, `allowed-tools: ["Read"]` only, with `argument-hint: "Target API version"`

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: C

**Why C is correct:**
`context: fork` runs the skill in an isolated sub-agent so verbose output doesn't pollute the main conversation. `allowed-tools` restricts to only necessary tools (Bash for testing endpoints, Read for reading files, Edit for making changes) preventing destructive or unnecessary actions. `argument-hint` prompts the developer for required input when they invoke `/migrate` without arguments, ensuring the target API version is always provided.

**Why B fails:**
`context: main` runs the skill in the main conversation context. The question explicitly states the skill generates extensive verbose intermediate output - running in main would pollute the conversation context with all that noise, making it harder to follow the overall task.

**Why A fails:**
No `allowed-tools` restriction over-provisions the skill with unrestricted tool access. The principle of least privilege applies - a migration skill doesn't need access to every available tool. Unrestricted access increases the risk of unintended side effects.

**Why D fails:**
Restricting to `Read` only is too restrictive. The skill needs Bash to run shell commands testing each endpoint after conversion, and Edit to make the actual code changes converting legacy endpoints. With only Read access, the skill can look at files but can't actually perform the migration or test it.

### Key Decision Framework
**`context: fork` when output is verbose or intermediate. `allowed-tools` scoped to exactly what the skill needs. `argument-hint` for required parameters to prevent invocation without necessary input.**
</details>

---

## Practice Problem 7

**You ask Claude Code to generate a data transformation function that converts raw API responses into your internal format. You've tried describing the expected output format in detailed prose twice with different wording, but the output still has subtle differences from what your downstream system expects - date formats are wrong, nested objects are flattened when they shouldn't be. What's the most effective next step?**

A) Provide 2-3 concrete input/output examples showing the exact transformation you expect, including the tricky date formats and nested objects.

B) Write a comprehensive specification document detailing every field mapping and format requirement.

C) Switch to plan mode so Claude can analyze the downstream system requirements first.

D) Write unit tests for the expected output and share the test failures with Claude.

<details>
<summary>Your Answer? (click to reveal correct answer)</summary>

### Correct Answer: A

**Why A is correct:**
Concrete input/output examples are the most effective way to communicate expected transformations when prose descriptions are interpreted inconsistently. The model can see exactly what input produces what output, resolving ambiguities that words can't capture. Showing a raw API response alongside the exact expected internal format eliminates guesswork about date formats, nesting structure, and field mappings.

**Why B fails:**
More prose will produce the same ambiguity. The problem isn't insufficient detail - you've already tried detailed prose twice with different wording. A specification document is still prose, just longer. The issue is that natural language is inherently ambiguous for describing exact data structures.

**Why C fails:**
Plan mode addresses complexity and architecture, not communication clarity. The problem isn't that Claude doesn't understand the task's complexity - it's that the expected output format hasn't been communicated unambiguously. Plan mode won't resolve the date format or nesting ambiguity.

**Why D fails:**
Unit tests are effective for iterative refinement but are premature here. Writing tests requires more effort than providing examples. Try the cheaper fix (examples) first - if 2-3 concrete examples resolve the ambiguity, no tests are needed for this step. Tests become valuable when the transformation logic is complex enough to warrant ongoing regression protection.

### Key Decision Framework
**When prose descriptions produce inconsistent results, switch to concrete input/output examples. Examples eliminate ambiguity that words can't resolve. Reserve test-driven iteration for complex logic that needs ongoing regression protection.**
</details>

---

## Key Takeaways for Domain 3

1. **CLAUDE.md hierarchy**: user (`~/.claude/`) -> project (`.claude/` or root) -> directory (subdirs)
2. **Shared commands** -> `.claude/commands/`; **personal commands** -> `~/.claude/commands/`
3. **Path-specific rules** in `.claude/rules/` with glob patterns beat directory-level CLAUDE.md for cross-cutting concerns
4. **Plan mode** for complex, multi-file, architectural tasks; **direct execution** for well-scoped changes
5. **`-p` flag** runs Claude Code non-interactively for CI/CD pipelines
6. **`context: fork`** in skill frontmatter isolates verbose output from the main session
7. **Independent review sessions** catch issues that the generating session misses (self-review bias)
8. **@import** for modular CLAUDE.md - reference shared standards from multiple packages
9. **Skill frontmatter**: `context: fork` isolates output, `allowed-tools` restricts access, `argument-hint` prompts for input
10. **Concrete input/output examples** beat prose descriptions for communicating exact transformations
