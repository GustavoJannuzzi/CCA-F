# Lab D1 — O loop agêntico, orquestração e o gate `PreToolUse`

> **Capstone, etapa 1/5.** Aqui nasce o *Customer Support Resolution Agent*. Nas próximas etapas ele ganha tools bem desenhadas (D2), vira projeto Claude Code (D3), prompts calibrados (D4) e gestão de contexto (D5).

## 📖 O que você já estudou (index.html → Domínio 1)
- **1.1** O loop agêntico (`stop_reason`)
- **1.2** Orquestração coordenador-subagente
- **1.3** Invocação de subagentes, passagem de contexto & paralelismo
- **1.4 / 1.5** Workflows com enforcement e hooks `PreToolUse`/`PostToolUse`

## 🎯 O que você vai construir
Um agente de suporte que, dado um pedido do cliente, decide sozinho quais ferramentas chamar até resolver. Duas partes:

1. **O loop cru (Claude API):** você escreve o `while` que inspeciona `stop_reason`, executa as tools e devolve os `tool_result`. Ferramentas *mockadas* (`get_customer`, `lookup_order`, `process_refund`) — no D2 a gente desenha elas direito.
2. **O gate de segurança (`PreToolUse`):** a política diz *"nunca reembolsar sem verificar o cliente antes"*. Você não confia no prompt para isso — você intercepta `process_refund` **antes** de executar e bloqueia se o cliente ainda não foi verificado. Isso é enforcement **determinístico**.

## 🧩 Passo a passo (starter.py → solucao.py)
1. Defina o array `tools` (3 tools mock) e a implementação de cada uma (`executar`).
2. Escreva o loop: `messages.create` → se `stop_reason == "tool_use"`, execute e anexe `tool_result`; se `"end_turn"`, pare.
3. Antes de executar cada tool, chame `pre_tool_use(tool, state)`. Se ela retornar um bloqueio, **não execute** — devolva um `tool_result` com `is_error=True` explicando o pré-requisito. O modelo lê isso e se corrige (chama `get_customer` primeiro).
4. Rode com um pedido que tenta pular a verificação e observe o agente ser forçado a verificar antes.

## 🧠 Conceitos que o código materializa
- **Quem controla a parada é `stop_reason`**, não parsear o texto ("terminei").
- **API é stateless:** você reenvia `messages` inteiro a cada volta; cada `tool_result` casa com o `tool_use` pelo `tool_use_id`.
- **Gate programático ≠ instrução de prompt:** o hook é uma garantia; o prompt é probabilístico.

## 🧪 Ligações com o exame
- *"Em X% dos casos o agente pula a verificação apesar do system prompt"* → **hook `PreToolUse`**, não "reforçar o prompt" nem "adicionar few-shot" (distratoras clássicas do 1.4).
- *"O loop para cedo / resposta incompleta"* → confiar em `stop_reason`, não no texto.
- *Bloquear = `PreToolUse`* (roda **antes**); transformar resultado = `PostToolUse` (roda **depois**).

## 🚀 Extensão opcional (coordenador → subagente)
No `solucao.py` há um bloco comentado mostrando o mesmo agente reescrito no **Agent SDK** como coordenador que delega a um subagente `refunds`. Note o `allowedTools=["Task", ...]` e o **contexto isolado**: o subagente só sabe o que vai explícito no prompt da `Task`.
