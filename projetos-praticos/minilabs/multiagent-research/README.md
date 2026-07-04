# Mini-lab — Multi-Agent Research System

> **Cenário oficial:** *Multi-Agent Research*. Fecha o Domínio 1 (orquestração) com o Domínio 5 (proveniência e incerteza). Coordenador → subagentes especializados, em paralelo.

## 📖 O que você já estudou
- **1.2/1.3** Coordenador-subagente, contexto isolado, paralelismo · **1.6** decomposição · **5.6** proveniência/incerteza

## 🎯 O que você vai construir
Um coordenador que responde uma pergunta de pesquisa delegando a subagentes:
`buscar_web`, `analisar_docs`, `sintetizar`. Você vai exercitar:

1. **Decomposição do coordenador.** Ele quebra a pergunta em subtarefas. Cuidado: **decomposição estreita = cobertura incompleta** — se o relatório sai parcial embora todos os subagentes tenham "acertado", a culpa é do coordenador (§1.2).
2. **Contexto isolado.** Cada subagente começa do zero: tudo que precisa vai **explícito no prompt da `Task`** (§1.3). Se você só diz "sintetize as descobertas", ele pergunta "quais?".
3. **Paralelismo real.** Subtarefas independentes (buscar UE, EUA, China) = **várias `Task` numa mesma resposta** do coordenador — não turnos consecutivos.
4. **Proveniência.** Cada achado carrega a fonte (URL/doc/página); a síntese preserva a atribuição e sinaliza o que é incerto (§5.6).

## 🧠 Como isso vive no Agent SDK
No SDK você define `AgentDefinition` para o coordenador e cada subagente. O coordenador **precisa de `"Task"` em `allowedTools`** para spawnar. O `solucao.py` mostra tanto uma **simulação didática** (roda sem chave, para você ver o fluxo) quanto o **esqueleto real** com `claude_agent_sdk`.

## 🧪 Ligações com o exame
- *"Todos os subagentes ok, mas relatório parcial"* → **decomposição estreita do coordenador** (olhe o log do coordenador, não os subagentes).
- *"Subagente diz: não tenho informação"* → **passar contexto no prompt da Task**.
- *"Como paralelizar?"* → **múltiplas Task numa resposta** (não threads, não turnos).
- *"Coordenador não consegue delegar"* → falta **`"Task"` em allowedTools**.
- *Síntese multi-fonte* → **preservar proveniência** e marcar incerteza.
