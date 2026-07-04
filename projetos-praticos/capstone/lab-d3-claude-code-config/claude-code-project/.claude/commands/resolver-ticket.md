---
description: Resolve um ticket de suporte de ponta a ponta
argument-hint: <email-do-cliente> <order-id>
allowed-tools: Read, Grep, Bash
---

<!--
Slash command customizado: vira /resolver-ticket no Claude Code.
$ARGUMENTS injeta o que o usuário digitar depois do comando.
Frontmatter: description (ajuda), argument-hint (dica de uso),
allowed-tools (restringe as ferramentas deste comando).
-->

Você é o agente de suporte. Resolva o ticket para: **$ARGUMENTS**

Siga a ordem OBRIGATÓRIA:
1. Verifique o cliente (get_customer) — nunca pule este passo.
2. Consulte o pedido (lookup_order).
3. Se couber reembolso e valor <= R$500, processe. Se > R$500, escale para humano
   com um resumo estruturado (id do cliente, causa-raiz, valor, ação recomendada).
