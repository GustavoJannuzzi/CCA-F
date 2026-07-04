# 🛠️ Projetos Práticos — Trilha CCA-F

Esta pasta é o **laboratório hands-on** da apostila. A ideia é simples: você estuda um domínio no `index.html` e, ao terminar, **constrói** a funcionalidade que acabou de aprender. Julgamento prático se fixa fazendo, não lendo.

> **Stack:** Python 3.10+ · Claude Agent SDK (`claude-agent-sdk`) + Claude API (`anthropic`).
> **Formato:** *read-along*. Cada lab tem enunciado, esqueleto (`starter.py` com `TODO`) e solução comentada (`solucao.py`). Você **não precisa necessariamente rodar** tudo — o objetivo é entender e comparar. Se quiser rodar, veja [`00-setup.md`](00-setup.md).

---

## 🧭 Como a trilha está organizada

Escolhemos uma abordagem **híbrida**:

### 1. Capstone evolutivo — *Customer Support Resolution Agent* (Cenário 1)
Um único agente que **cresce a cada domínio**. É o cenário mais clássico do exame e o único que naturalmente toca os 5 domínios. Você começa com um loop cru e termina com um agente de produção com hooks, tools bem desenhadas, config de Claude Code, prompts calibrados e gestão de contexto.

| Ordem | Estude no index | Lab | O que você constrói |
|-------|-----------------|-----|---------------------|
| 1º | Domínio 1 (`d1`) | [`capstone/lab-d1-loop-e-orquestracao/`](capstone/lab-d1-loop-e-orquestracao/) | O loop agêntico, coordenador→subagente e um gate `PreToolUse` (verificar cliente antes de reembolsar) |
| 2º | Domínio 2 (`d2`) | [`capstone/lab-d2-tools-e-mcp/`](capstone/lab-d2-tools-e-mcp/) | Tools com descrições claras, erros estruturados estilo MCP e `tool_choice` |
| 3º | Domínio 3 (`d3`) | [`capstone/lab-d3-claude-code-config/`](capstone/lab-d3-claude-code-config/) | Empacotar como projeto Claude Code: `CLAUDE.md`, slash command, hook em `settings.json`, `.mcp.json` |
| 4º | Domínio 4 (`d4`) | [`capstone/lab-d4-prompt-engineering/`](capstone/lab-d4-prompt-engineering/) | System prompt com critérios explícitos, few-shot de escalação e output estruturado (JSON schema) |
| 5º | Domínio 5 (`d5`) | [`capstone/lab-d5-context-management/`](capstone/lab-d5-context-management/) | Preservar info crítica em conversa longa, handoff estruturado e sessão nova com resumo |

### 2. Mini-labs — cenários que o capstone não cobre bem
Dois cenários oficiais que merecem um lab próprio:

| Estude no index | Mini-lab | Cenário |
|-----------------|----------|---------|
| Domínios 3 + 5 | [`minilabs/cicd-code-review/`](minilabs/cicd-code-review/) | **Claude Code em CI/CD** — review de PR headless com `claude -p` |
| Domínios 1 + 5 | [`minilabs/multiagent-research/`](minilabs/multiagent-research/) | **Multi-Agent Research System** — coordenador + subagentes em paralelo, com proveniência |

---

## 📌 Sequência recomendada

```
Domínio 1 (index)  →  lab-d1  ─┐
Domínio 2 (index)  →  lab-d2   │  capstone crescendo
Domínio 3 (index)  →  lab-d3   │  (o mesmo agente)
Domínio 4 (index)  →  lab-d4   │
Domínio 5 (index)  →  lab-d5  ─┘
                   →  minilab CI/CD          (fecha Claude Code)
                   →  minilab Multi-Agent    (fecha orquestração)
```

Faça **um lab por sessão de estudo**, logo depois de ler o domínio correspondente. Cada README começa com "📖 O que você já estudou" ligando de volta aos subtópicos do `index.html`.

## 🎯 Como cada lab se conecta ao exame

Todo lab termina com uma seção **"🧪 Ligações com o exame"**: as pegadinhas clássicas daquele domínio reaparecem como decisões concretas de código (ex.: *"por que um hook `PreToolUse` e não reforçar o system prompt?"*). Se você entende **por que o código é assim**, acerta a questão de múltipla escolha.

## ⚠️ Aviso

Este material é de **estudo**. O código prioriza clareza didática sobre robustez de produção (sem tratamento exaustivo de erros, sem retries de rede, secrets simplificados). Nunca comite API keys reais.
