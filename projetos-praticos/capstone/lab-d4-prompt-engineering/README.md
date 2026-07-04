# Lab D4 — Critérios explícitos, few-shot de escalação e output estruturado

> **Capstone, etapa 4/5.** O agente funciona, mas: escala tickets demais (falsos positivos), decide de forma inconsistente e devolve texto livre difícil de integrar. Você resolve os três com prompt engineering.

## 📖 O que você já estudou (index.html → Domínio 4)
- **4.1** Critérios explícitos (reduzir falsos positivos)
- **4.2** Few-shot prompting
- **4.3** Output estruturado via `tool_use` & JSON schema
- **4.4** Validação, retry & feedback

## 🎯 O que você vai construir
1. **System prompt com critérios explícitos.** Em vez de "escale se for complexo", você define **o que conta como escalação** (valor > R$500, cliente irritado 2ª vez, suspeita de fraude). Critério explícito **reduz falso positivo** — a correção certa quando o agente "escala demais".
2. **Few-shot para calibrar julgamento.** 2–3 exemplos de ticket → decisão mostram a fronteira. Pegadinha: para calibrar *quando escalar*, a resposta é **few-shot com critérios**, não "score de confiança".
3. **Output estruturado.** A resolução do ticket sai como **JSON válido** via `tool_use` (tool `registrar_resolucao` com `input_schema`), pronta para o sistema de tickets consumir.
4. **Validação + retry.** Se faltar campo, você devolve o erro ao modelo e ele corrige (feedback loop).

## 🧠 Detalhe de schema que cai na prova
Campo que **pode não existir** no dado → **não** o marque `required`; use `"type": ["string", "null"]` (nullable). Marcar como required força o modelo a inventar valor.

## 🧪 Ligações com o exame
- *"Agente escala demais / muitos falsos positivos"* → **critérios explícitos no prompt** (4.1).
- *"Calibrar quando escalar"* → **few-shot com exemplos e critérios** (4.2). Distratora: "score de confiança".
- *"Garantir JSON íntegro para downstream"* → **`tool_use` com JSON schema** (4.3), não pedir "responda em JSON" e torcer.
- *"Campo às vezes ausente"* → **nullable**, não required (4.3).
