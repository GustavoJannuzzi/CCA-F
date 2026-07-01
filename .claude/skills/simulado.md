---
name: simulado
description: Conduz um simulado completo do exame CCA-F com 20 questões cronometradas
context: fork
argument-hint: "[domínio 1-5 | all]"
---

# Simulado CCA-F

Conduza um simulado no formato do exame real com as seguintes características:

## Configuração
- 20 questões de múltipla escolha
- Domínio: conforme argumento passado (ou todos se "all")
- Formato: 4 opções por questão, apenas 1 correta
- Questões baseadas em cenários reais de produção

## Execução
1. Anuncie o início do simulado com o número de questões e domínio
2. Apresente cada questão numerada com:
   - Contexto do cenário (Customer Support, CI/CD, Multi-Agent, etc.)
   - Pergunta clara
   - Opções A, B, C, D
3. AGUARDE a resposta antes de mostrar a próxima questão
4. Registre as respostas mas NÃO REVELE se está certo ou errado até o final

## Relatório Final
Após todas as questões, mostre:
- Score: X/20 (X%)
- Equivalente à escala do exame: ~XXX/1000
- Status: APROVADO (>=720) ou REPROVADO (<720)
- Breakdown por domínio com % de acerto
- Questões erradas com explicação detalhada de cada uma
- Top 3 conceitos para revisar antes do exame

## Questões Sugeridas por Domínio

Para o Domínio 1 (Agentic Architecture):
- Quando usar hooks vs. system prompt para enforcement
- Como subagentes recebem contexto
- Paralelismo de subagentes (single response vs multiple turns)
- stop_reason: "tool_use" vs "end_turn" control flow
- Task decomposition: prompt chaining vs dynamic adaptive

Para o Domínio 2 (Tool Design & MCP):
- Impacto de muitas ferramentas na confiabilidade de seleção
- isError flag e categorias de erro estruturado
- Diferença entre MCP resources e tools
- Escopos de servidor MCP (.mcp.json vs ~/.claude.json)
- tool_choice: auto vs any vs forced

Para o Domínio 3 (Claude Code Config):
- Hierarquia de CLAUDE.md (user/project/directory)
- Escopo de comandos e skills
- Quando usar plan mode vs direct execution
- -p flag para CI/CD
- path-specific rules com glob patterns

Para o Domínio 4 (Prompt Engineering):
- Explicit criteria vs vague instructions para false positives
- Few-shot vs detailed instructions para consistency
- Quando retries são ineficazes
- tool_choice para garantir structured output
- Batch API: casos de uso adequados

Para o Domínio 5 (Context Management):
- Escalation triggers corretos (vs incorretos)
- Structured error context para coordinator recovery
- Progressive summarization risks
- Stratified sampling vs aggregate accuracy metrics
- Lost in the middle mitigation
