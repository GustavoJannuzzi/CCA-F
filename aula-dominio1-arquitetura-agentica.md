# Domínio 1 — Arquitetura Agêntica (27% do exame)

> Você usa Claude Code todo dia para codar. Esse domínio explica o que está acontecendo POR BAIXO quando o Claude decide usar uma ferramenta, chamar outro agente, ou parar de trabalhar. É o domínio mais pesado do exame (27%) porque entender isso muda completamente como você constrói sistemas com Claude.

---

## 1. O que é "agêntico"?

Quando você usa Claude Code normalmente, o Claude:
1. Lê sua pergunta
2. Responde em texto

Isso é **não-agêntico** — o Claude reage uma vez e para.

**Agêntico** é quando o Claude:
1. Recebe uma tarefa
2. Decide **por conta própria** quais ferramentas usar
3. Age (executa a ferramenta)
4. Vê o resultado
5. Decide o próximo passo
6. Repete até terminar

Você já viu isso acontecer: você pede *"refatora esse arquivo"* e o Claude lê o arquivo, edita, roda os testes, vê o erro, corrige — sem você ficar mandando mensagem nova a cada passo. Isso é o loop agêntico.

---

## 2. O Loop Agêntico — Como funciona de verdade

O mecanismo central é o **`stop_reason`** que a API do Claude retorna. Tem dois valores importantes:

| `stop_reason` | Significa | O que fazer |
|---|---|---|
| `"tool_use"` | Claude quer usar uma ferramenta | Execute a ferramenta, devolva o resultado, continue o loop |
| `"end_turn"` | Claude terminou | Mostre a resposta ao usuário, pare |

### Exemplo de código do loop (Python)

```python
import anthropic

client = anthropic.Anthropic()
messages = [{"role": "user", "content": "Analise o arquivo app.py e me diga se há bugs"}]

# O LOOP AGÊNTICO
while True:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        tools=[read_file_tool, run_tests_tool],  # ferramentas disponíveis
        messages=messages
    )

    # ✅ CORRETO: checar stop_reason
    if response.stop_reason == "end_turn":
        print(response.content[-1].text)  # resposta final ao usuário
        break

    elif response.stop_reason == "tool_use":
        # Claude quer usar uma ferramenta
        tool_use = next(b for b in response.content if b.type == "tool_use")

        # Executa a ferramenta de verdade
        result = execute_tool(tool_use.name, tool_use.input)

        # Appenda na conversa — Claude precisa ver o resultado
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": result}]
        })
        # Volta para o início do while — Claude decide o próximo passo

# ❌ ERRADO: checar o texto da resposta
# if "I've completed the analysis" in response.content[-1].text:
#     break   ← NUNCA FAÇA ISSO. O Claude pode dizer "terminei" no meio de uma análise.
```

### Por que é errado checar o texto?

O Claude pode escrever *"I've completed step 1 of the analysis"* enquanto ainda precisa chamar mais 3 ferramentas. Se você para baseado no texto, você interrompe o trabalho na metade. O `stop_reason` é determinístico — é o protocolo oficial de comunicação entre o modelo e o seu código.

### Experimento prático no Claude Code

Abra o Claude Code e peça algo que exige múltiplos passos:

```bash
# No terminal, dentro de um projeto com arquivos Python:
claude "encontre todos os arquivos Python que importam 'requests', leia cada um e me diga qual faz mais chamadas HTTP"
```

Observe o que acontece: o Claude não responde de uma vez. Ele usa `Glob`, depois `Read` em cada arquivo, processa, sintetiza. Cada vez que ele usa uma ferramenta, é um ciclo do loop agêntico. Quando ele para de chamar ferramentas e apresenta a resposta final, o `stop_reason` foi `"end_turn"`.

---

## 3. Arquitetura Coordinator-Subagente (Hub-and-Spoke)

Imagine que você tem uma tarefa grande: *"Pesquise o impacto da IA em música, artes visuais e literatura e escreva um relatório comparativo."*

Um único agente fazer tudo isso em série seria lento e sofreria de "atenção diluída" (o modelo perde qualidade quando o contexto fica gigante). A solução é dividir o trabalho.

```
                    ┌─────────────────────┐
                    │    COORDINATOR      │  ← recebe a tarefa grande
                    │                     │  ← decompõe em subtarefas
                    │                     │  ← agrega os resultados
                    └─────────────────────┘
                     /         |          \
                    /          |           \
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Subagente│   │ Subagente│   │ Subagente│
        │  Música  │   │  Artes   │   │Literatura│
        └──────────┘   └──────────┘   └──────────┘
        [contexto     [contexto       [contexto
         ISOLADO]      ISOLADO]        ISOLADO]
```

### A regra mais importante: contexto NÃO é herdado

Os subagentes **não veem** a conversa do coordinator. Cada subagente começa do zero. Você PRECISA passar o contexto explicitamente no prompt.

```python
# ❌ ERRADO — subagente vai responder: "que cliente? não tenho essa informação"
task_tool.invoke(
    prompt="Investigue o problema de cobrança do cliente"
)

# ✅ CORRETO — tudo que o subagente precisa está no prompt
task_tool.invoke(
    prompt="""
Investigue o problema de cobrança dupla.

Dados do caso:
- Cliente: CUS-4829 (João Silva)
- Pedido: ORD-789
- Problema: cobrado duas vezes em 15/03/2024
- Valor: R$ 249,90

Ferramentas disponíveis: get_order_details, process_refund
Tarefa: verificar histórico de pagamentos e confirmar a duplicidade.
"""
)
```

### Subagentes em paralelo vs sequencial

Se as tarefas são **independentes** (nenhuma precisa do resultado da outra), dispare todas de uma vez:

```python
# ✅ PARALELO — cada Task é emitida na mesma resposta do coordinator
# (o Claude emite múltiplos tool_use blocks em uma única resposta)
# Resultado: tempo total ≈ tempo da tarefa mais longa (não soma de todas)

coordinator_response = client.messages.create(
    tools=[task_tool],
    messages=[{"role": "user", "content": "Pesquise IA em música, artes e literatura"}]
)
# O coordinator retorna 3 tool_use blocks de uma vez:
# tool_use: task("Pesquise IA em música")
# tool_use: task("Pesquise IA em artes visuais")
# tool_use: task("Pesquise IA em literatura")
# Todos executam em paralelo

# ✅ SEQUENCIAL — quando B precisa do resultado de A
# Ex: Passo 1 coleta dados → Passo 2 analisa os dados coletados
```

### Experimento prático

Crie a estrutura abaixo e rode no Claude Code:

```
mkdir meu-agente
cd meu-agente
```

Crie o arquivo `CLAUDE.md`:
```markdown
# Agente de Pesquisa

Você é um coordinator de pesquisa. Quando receber um tópico amplo, decomponha em 3 subtópicos e delegue cada um como uma tarefa separada usando a ferramenta Task. Passe o contexto completo de cada subtópico no prompt da task. Ao final, agregue os resultados em um relatório.
```

Agora peça ao Claude Code:
```
claude "pesquise as tendências de IA em 2024 nas áreas: saúde, educação e finanças"
```

Você vai ver o Claude usar a ferramenta `Task` 3 vezes (em paralelo ou sequencial dependendo de como ele interpreta as dependências), cada subagente faz a pesquisa, e o coordinator monta o relatório final.

---

## 4. Hooks — A diferença entre "quase sempre" e "sempre"

Esse é um dos conceitos mais importantes do exame. Hooks são interceptadores que executam código determinístico (100% garantido) em pontos específicos do fluxo.

### Analogia arquitetural

Pense em hooks como **middleware no Express.js** ou **interceptors no Spring**. Você não confia que o código da rota vai validar o token JWT toda vez — você coloca um middleware que garante isso antes de qualquer rota.

Da mesma forma, você não confia que o Claude vai verificar a identidade do cliente antes de processar um reembolso toda vez (ele falha ~12% das vezes mesmo com instrução no prompt). Você coloca um hook que bloqueia a chamada se a verificação não aconteceu.

### Comparação crítica para o exame

| Mecanismo | Garantia | Quando usar |
|---|---|---|
| Hook `PostToolUse` | **100% determinístico** | Regras críticas: financeiro, segurança, compliance |
| Instrução no system prompt | ~88-95% (probabilístico) | Comportamento preferencial, guia não-crítico |
| Few-shot examples | Melhora a baseline (probabilístico) | Consistência em casos ambíguos |

**Regra de ouro do exame:** Se a consequência de falhar é financeira ou de segurança → use hooks. Nunca confie só no prompt para isso.

### Como hooks funcionam na prática (Agent SDK)

```python
# Hook PostToolUse — executa APÓS o Claude chamar uma ferramenta, ANTES do resultado chegar de volta ao modelo
def meu_hook(tool_name: str, tool_result: dict) -> dict:
    if tool_name == "process_refund":
        amount = tool_result.get("amount", 0)
        if amount > 500:
            # Bloqueia a ação e força escalada humana
            return {
                "blocked": True,
                "reason": "Reembolso acima de R$500 requer aprovação humana",
                "action": "escalate_to_human",
                "dados_escalada": {
                    "cliente_id": tool_result.get("customer_id"),
                    "pedido_id": tool_result.get("order_id"),
                    "valor": amount
                }
            }
    return tool_result  # deixa passar normalmente

# Registrado no AgentDefinition:
agente = AgentDefinition(
    system_prompt="Você é um agente de suporte ao cliente...",
    tools=[get_customer, lookup_order, process_refund, escalate_to_human],
    hooks={"PostToolUse": meu_hook}
)
```

### Experimento prático — hooks no Claude Code (settings.json)

No Claude Code (a CLI que você já usa), hooks são configurados em `.claude/settings.json`. Crie o arquivo:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[HOOK] Arquivo escrito: $CLAUDE_TOOL_INPUT_FILE_PATH\" >> hooks.log"
          }
        ]
      }
    ]
  }
}
```

Agora peça ao Claude Code para criar um arquivo qualquer. Após ele criar, abra `hooks.log` — vai ter o registro do hook executando. Isso é um hook `PostToolUse` para a ferramenta `Write`. Você pode usar isso para auditar, validar, ou bloquear ações.

---

## 5. Decomposição de Tarefas — Escolhendo a estratégia certa

### Prompt Chaining (sequencial fixo)

Bom para workflows **previsíveis com etapas fixas**:

```
Passo 1: Coleta dados  →  Passo 2: Analisa  →  Passo 3: Valida  →  Passo 4: Reporta
```

Exemplo: revisão de código com checklist fixo (segurança, performance, style guide, tests). Você sabe exatamente quais aspectos revisar, sempre os mesmos.

**Como fazer no Claude Code:**

Crie `.claude/commands/review.md`:
```markdown
# /review

Execute uma revisão de código em 4 passos sequenciais:

**Passo 1 — Segurança:** Procure por SQL injection, XSS, secrets hardcoded, dependências vulneráveis.
**Passo 2 — Performance:** Identifique N+1 queries, loops desnecessários, falta de cache.
**Passo 3 — Cobertura de testes:** Verifique se os casos críticos têm testes.
**Passo 4 — Relatório:** Consolide todos os achados com severidade (crítico/médio/baixo).

Para cada passo, complete antes de iniciar o próximo.
```

Agora rode `/review` no Claude Code — ele vai executar exatamente essa sequência.

### Dynamic Decomposition (adaptativo)

Bom para **investigações abertas** onde você não sabe de antemão quais subtarefas serão necessárias:

```
Coordinator analisa a tarefa → decide quais subtasks criar → spawna conforme necessário
```

Exemplo: *"Investigue por que o sistema de pagamentos está lento."* Você não sabe se o problema é no banco, na rede, no código, ou na infraestrutura — o coordinator decide ao longo da investigação.

### Multi-pass para code review (evitando attention dilution)

Quando você tem 30+ arquivos para revisar, não mande tudo para um único contexto. O Claude perde qualidade nos arquivos do final.

```
Passo 1 (PARALELO): cada arquivo → seu próprio subagente → achados locais
Passo 2 (ÚNICO): todos os achados → um agente de síntese → cross-file issues, padrões, contradições
```

**Por que isso funciona:** cada subagente tem contexto pequeno e focado. O agente de síntese recebe apenas os achados condensados (não os 30 arquivos completos).

---

## 6. Gerenciamento de Estado de Sessão

### Quando usar cada abordagem

| Situação | Ação correta | Por quê |
|---|---|---|
| Contexto degradado (Claude diz "padrões típicos" em vez de mencionar classes específicas) | Nova sessão + resumo estruturado dos achados | `--resume` restaura o estado ruim |
| Explorar 2 abordagens diferentes em paralelo | `fork_session` | Cria branches independentes do baseline atual |
| Sessão longa mas contexto ainda válido | `/compact` | Reduz tokens mantendo o essencial |
| Crash após processar 8 de 20 arquivos | Manifesto de estado (JSON) | Estado persiste entre sessões |

### Manifesto de estado — o padrão para crash recovery

```json
{
  "migration_manifest": {
    "total_files": 20,
    "completed": [
      "api/v1.py", "api/v2.py", "api/v3.py",
      "models/user.py", "models/product.py",
      "services/auth.py", "services/email.py", "services/logging.py"
    ],
    "pending": [
      "models/order.py", "services/billing.py", "services/payment.py",
      "handlers/checkout.py", "handlers/refund.py"
    ],
    "last_updated": "2024-03-15T14:23:00Z"
  }
}
```

**Experimento prático:**

Crie `.claude/commands/migrate-with-recovery.md`:
```markdown
# /migrate-with-recovery

Antes de processar qualquer arquivo:
1. Verifique se existe `migration_manifest.json` na raiz do projeto
2. Se existir, carregue-o e PULE os arquivos já em `completed`
3. Para cada arquivo processado com sucesso, adicione ao `completed` no manifesto
4. Salve o manifesto atualizado após cada arquivo

Isso garante que um crash no meio não perde o progresso.
```

---

## 7. Resumo — Framework de decisão para o exame

O exame vai apresentar cenários e perguntar qual é a solução correta. Use esse framework:

### Pergunta 1: "A falha é determinística (financeiro/segurança) ou preferencial?"
- Determinística → **Hook** (não prompt, não few-shot)
- Preferencial → Instrução no system prompt + few-shot examples

### Pergunta 2: "O subagente tem o contexto que precisa?"
- Se o subagente responde "não tenho essa informação" → faltou **passar contexto explicitamente no Task prompt**
- Contexto NUNCA é herdado automaticamente

### Pergunta 3: "As subtarefas têm dependências entre si?"
- Independentes → **paralelo** (múltiplos Task calls na mesma resposta)
- A depende de B → **sequencial**

### Pergunta 4: "O loop está parando cedo demais?"
- Verificar se está checando `stop_reason == "end_turn"` (correto) vs parsing de texto (errado)

### Pergunta 5: "O resultado final tem gaps mesmo com subagentes bem-sucedidos?"
- Problema de **decomposição do coordinator** — ele não criou subtarefas abrangentes o suficiente

### Pergunta 6: "Sessão com contexto degradado — continuo ou recomeço?"
- Contexto ruim → **nova sessão com resumo estruturado** (não `--resume`, não `/compact`)

---

## 8. Questões típicas do exame com raciocínio

### Questão tipo 1
*"Seu agente pula a verificação de identidade em 12% dos casos mesmo com instrução no system prompt. O que fazer?"*

**Resposta: Hook programático** que bloqueia `process_refund` até `get_customer` ter retornado um ID verificado. A instrução no prompt é probabilística — 12% de falha em operações financeiras não é aceitável.

### Questão tipo 2
*"O subagente responde: 'I'd be happy to help, but I don't have any customer information.' O que causou isso?"*

**Resposta: Contexto não foi passado explicitamente no prompt da Task.** Subagentes são isolados — não herdam nada do coordinator.

### Questão tipo 3
*"O relatório final sobre 'IA em indústrias criativas' cobre só artes visuais. Os subagentes executaram com sucesso. Qual o root cause?"*

**Resposta: O coordinator decompos o tópico de forma estreita** — criou subtasks só para artes visuais, sem música, literatura, cinema. O problema é na decomposição, não nos subagentes.

### Questão tipo 4
*"Para pesquisar regulamentação de IA na UE, EUA e China (frameworks independentes), como executar?"*

**Resposta: Paralelo** — emitir 3 Tasks na mesma resposta do coordinator. Não há dependência de dados entre as regiões.

---

## Próximos passos

Agora que você entende o Domínio 1, os próximos domínios fazem mais sentido:
- **Domínio 2 (Tool Design & MCP):** Como projetar as ferramentas que o loop agêntico vai usar
- **Domínio 3 (Claude Code Config):** Como configurar CLAUDE.md, hooks e slash commands no Claude Code
- **Domínio 4 (Prompt Engineering):** Como escrever system prompts que direcionam bem o comportamento do agente
- **Domínio 5 (Context Management):** Como gerenciar o contexto que você passa entre coordinator e subagentes
