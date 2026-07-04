# Lab D3 — Empacotar o agente como projeto Claude Code

> **Capstone, etapa 3/5.** Até aqui o agente vivia em Python (API/SDK). Agora você o "veste" como um **projeto Claude Code**: em vez de escrever o loop, você **configura** o Claude Code (que já é um agente pronto) via arquivos. Este é o domínio mais "config", quase sem Python.

## 📖 O que você já estudou (index.html → Domínio 3)
- **3.1** `CLAUDE.md` — hierarquia, escopo, organização modular (import com `@caminho`)
- **3.2** Slash commands & Skills
- **3.3** Regras com escopo de caminho (`.claude/rules/`)
- **3.4** Plan mode vs execução direta
- **3.6** Claude Code em CI/CD (aprofundado no mini-lab)

## 🎯 O que você vai construir
Um esqueleto de projeto (pasta [`claude-code-project/`](claude-code-project/)) com:

| Arquivo | Papel | Subtópico |
|---------|-------|-----------|
| `CLAUDE.md` | Instruções do time (versionadas) + import `@caminho` | 3.1 |
| `.claude/settings.json` | **Hook** `PostToolUse` (lint após editar) + permissões | 1.5 / 3.x |
| `.claude/commands/resolver-ticket.md` | **Slash command** `/resolver-ticket` com `$ARGUMENTS` | 3.2 |
| `.claude/agents/refunds.md` | **Subagente** de reembolsos (frontmatter) | 1.2 / 3.2 |
| `.mcp.json` | **Servidor MCP do time** (na raiz, versionado) | 2.4 |

Abra cada arquivo — os comentários explicam cada campo. Não precisa rodar: o objetivo é entender **onde cada configuração vive e por quê**.

## 🧠 As distinções que a prova adora (memorize)
- **`CLAUDE.md` do time = `.claude/CLAUDE.md` versionado** no repo. `~/.claude/CLAUDE.md` é **pessoal** (só sua máquina). Hierarquia: enterprise → projeto → pessoal.
- **Import no CLAUDE.md = `@caminho`** (ex.: `@./docs/padroes.md`). **Não** existe `@import`.
- **Automatizar algo após uma ação** (ex.: lint após editar arquivo) = **hook `PostToolUse` no `settings.json`**, **não** uma instrução no CLAUDE.md (instrução é probabilística; hook é garantido).
- **MCP do time = `.mcp.json` na raiz** (versionado). MCP pessoal/experimental = `~/.claude.json`.
- **Plan mode (`/plan`)** = só lê, não edita — use antes de tarefas complexas multi-arquivo; execução direta para mudanças pequenas e localizadas.

## 🧪 Ligações com o exame
- *"Automatizar lint depois de editar arquivo"* → hook `PostToolUse` (não CLAUDE.md).
- *"Instruções do time para todos"* → `.claude/CLAUDE.md` versionado (não `~/.claude/`).
- *"Config MCP compartilhada do time"* → `.mcp.json` na raiz (não `~/.claude.json`).
- *"Por que minhas instruções não são aplicadas?"* → `/memory` mostra o que está carregado; cheque a hierarquia.
