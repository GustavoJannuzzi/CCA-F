# Lab D2 — Tools bem desenhadas, erros estruturados e `tool_choice`

> **Capstone, etapa 2/5.** No D1 as tools eram mock com descrições fracas. Agora você as desenha como um bom engenheiro de tools faria — porque **a qualidade da descrição decide se o modelo escolhe a tool certa**.

## 📖 O que você já estudou (index.html → Domínio 2)
- **2.1** Descrições de ferramentas claras
- **2.2** Respostas de erro estruturadas (MCP) — o que é protocolo (`isError`) vs convenção da app
- **2.3** Distribuição de ferramentas & `tool_choice`

## 🎯 O que você vai construir
Refatorar as 3 tools do agente de suporte para:

1. **Descrições que desambiguam.** `lookup_order` vs `get_order_status` são fáceis de confundir. Você escreve descrições que dizem **quando usar cada uma** e o que retornam — a correção certa para "o modelo escolhe a tool errada" é **expandir a descrição**, não adicionar few-shot.
2. **Erros estruturados.** Quando `process_refund` falha (pedido já reembolsado, valor acima do limite), você retorna um **payload estruturado** dentro do `content`. Aqui mora a pegadinha do exame: no protocolo MCP **só `isError` é campo oficial**; `errorCategory`, `isRetryable`, `alternatives` são **convenção da sua aplicação** dentro do conteúdo do resultado.
3. **`tool_choice`.** Você vê os 3 modos e quando usar cada um.

## 🧠 `tool_choice` — o quadro que cai na prova
| Valor | Comportamento | Use quando |
|-------|---------------|------------|
| `{"type":"auto"}` | Pode chamar tool **ou** responder em texto | Conversa geral (default) |
| `{"type":"any"}` | **Deve** chamar alguma tool (qualquer uma) | Você sempre quer uma ação estruturada |
| `{"type":"tool","name":"X"}` | **Deve** chamar a tool X | Forçar extração/roteamento específico |

## 🧪 Ligações com o exame
- *"O agente escolhe a ferramenta errada entre duas parecidas"* → **expandir/clarificar as descrições** (2.1). Distratora: "adicionar few-shot".
- *"Qual campo é do protocolo MCP?"* → **`isError`**. `errorCategory`/`isRetryable`/`alternatives` são convenção sua no `content` (2.2).
- *"Sempre force uma resposta estruturada"* → `tool_choice: any` ou tool específica (2.3).

## 🔌 Nota sobre MCP
Estas tools poderiam viver num **servidor MCP** (um processo separado que expõe ferramentas via protocolo). O formato do resultado — `content` + `isError` — é o mesmo. No D3 você conecta um MCP ao Claude Code via `.mcp.json`. Deploy/hospedagem de MCP está **fora do escopo** do exame.
