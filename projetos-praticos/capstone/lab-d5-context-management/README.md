# Lab D5 — Gestão de contexto: preservar o crítico, handoff e sessão nova

> **Capstone, etapa 5/5.** O agente agora aguenta conversas longas de suporte. Você resolve os problemas que só aparecem com o tempo: informação crítica "escorre" da janela, o contexto degrada, e a passagem para um humano perde o histórico.

## 📖 O que você já estudou (index.html → Domínio 5)
- **5.1** Preservar informação crítica em conversas longas
- **5.2** Escalação & resolução de ambiguidade
- **5.4** Contexto em codebase/conversa grande — sessão nova vs resume
- **5.6** Proveniência & incerteza em síntese multi-fonte

## 🎯 O que você vai construir
1. **Bloco de "fatos fixos".** Dados que **não podem se perder** (id do cliente verificado, order_id, política aplicada) ficam num resumo persistente re-injetado a cada turno — não confie que a mensagem antiga continue na janela.
2. **Handoff estruturado.** Ao escalar para um humano (que **não vê** a conversa), você compila um resumo: id do cliente, causa-raiz, valor, ação recomendada, **e o que ainda é incerto**.
3. **Sessão nova com resumo (não `--resume`).** Quando o contexto **degradou** (muito ruído, o agente começou a se confundir), a resposta certa é **abrir sessão nova com um resumo estruturado** — não `--resume`, que só traz de volta o mesmo contexto degradado.
4. **`PostToolUse` para normalizar.** Suas ferramentas retornam datas em formatos diferentes; um `PostToolUse` normaliza **depois** que a tool responde, antes de o modelo ver — mantém o contexto limpo.

## 🧠 Resume vs sessão nova — o quadro decisivo
| Situação | Errado | Certo |
|----------|--------|-------|
| Continuar de onde parou (contexto bom) | — | `--resume` / `-c` |
| Contexto **degradou/poluiu** | `--resume` (traz o lixo de volta) | **Sessão nova + resumo estruturado** |

## 🧪 Ligações com o exame
- *"Info crítica se perde em conversa longa"* → **resumo persistente / re-injetar fatos fixos** (5.1).
- *"Contexto degradou, o que fazer?"* → **sessão nova com resumo**, não `--resume` (5.4).
- *"Passar para humano no meio"* → **handoff estruturado** com causa-raiz e incertezas (5.2).
- *"Normalizar formato dos resultados de tool"* → **`PostToolUse`** (transforma depois), não `PreToolUse`.
- *Síntese de várias fontes* → **preservar proveniência** (qual fonte disse o quê) e sinalizar incerteza (5.6).
