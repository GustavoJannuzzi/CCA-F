---
titulo: "Simulado 3 — Claude Architect Certification: Claude Code Foundations (Cenários)"
data_criacao: 2026-04-09
data_atualizacao: 2026-04-09
tema: "Estudo"
cliente: "Interno"
status: "ativo"
tags: [simulado, certificacao, claude-code, anthropic, estudo, cenarios, avancado]
---

# Simulado 3 — Claude Architect Certification: Claude Code Foundations

**60 questões orientadas a cenários e decisões arquiteturais | Resposta correta indicada após cada questão**

---

## Domínio 1 — Agentic Architecture (Q01–Q12)

**Q01.** Você está construindo um pipeline que deve: (1) buscar dados de uma API externa, (2) processar esses dados com Python, e (3) gerar um relatório em PDF. Qual arquitetura agêntica é mais adequada?

- A) Um único agente com três ferramentas sequenciais, pois as etapas têm dependência entre si
- B) Três subagentes paralelos, um para cada etapa
- C) Um orquestrador que delega cada etapa a um subagente especializado, aguardando o resultado de cada um antes de iniciar o próximo
- D) Um agente stateless que executa as três etapas em uma única chamada de ferramenta

> **Resposta: A** — Como as etapas têm dependência sequencial (o resultado da etapa 1 alimenta a 2, que alimenta a 3), um único agente com ferramentas sequenciais é mais adequado. Subagentes paralelos seriam para tarefas independentes.

---

**Q02.** Seu agente autônomo está processando 500 contratos jurídicos para extrair cláusulas específicas. Na metade do processo, a ferramenta de extração começa a retornar erros 429 (rate limit). Qual é a abordagem correta?

- A) Encerrar o pipeline e reportar quantos contratos foram processados antes do erro
- B) Ignorar os erros e continuar tentando — rate limits são temporários
- C) Implementar exponential backoff, salvar o progresso atual em estado externo e retomar do ponto de falha após o rate limit passar
- D) Trocar imediatamente para um modelo menor que consome menos tokens por segundo

> **Resposta: C** — Salvar checkpoints + retry com backoff é a abordagem correta. Abandonar o trabalho parcial desperdiça recursos; ignorar erros causa falhas silenciosas.

---

**Q03.** Você precisa que um agente Claude Code acesse um banco de dados interno da empresa para responder perguntas dos usuários. O banco contém dados sensíveis. Como estruturar o acesso corretamente?

- A) Fornecer as credenciais completas do banco no system prompt para Claude ter acesso direto via SQL
- B) Criar uma ferramenta MCP que executa queries parametrizadas com validação de input, usando credenciais armazenadas em variáveis de ambiente — nunca no prompt
- C) Dar ao agente acesso root ao banco pois isso facilita o desenvolvimento
- D) Armazenar as credenciais no CLAUDE.md do projeto para serem carregadas na sessão

> **Resposta: B** — Credenciais nunca no prompt/CLAUDE.md. Uma ferramenta MCP com queries parametrizadas (prevenção de SQL injection) e credenciais em variáveis de ambiente é a abordagem segura.

---

**Q04.** Um subagente em seu pipeline retorna o seguinte resultado inesperado: `{"status": "success", "data": null, "rows_affected": 0}`. O orquestrador deve:

- A) Considerar a operação bem-sucedida pois `status: "success"` foi retornado
- B) Tratar como falha silenciosa: `data: null` e `rows_affected: 0` com status success indica que algo não funcionou como esperado — investigar antes de prosseguir
- C) Encerrar o pipeline imediatamente pois dados nulos são sempre um erro crítico
- D) Solicitar ao usuário que verifique o banco de dados manualmente

> **Resposta: B** — Respostas ambíguas (success + data nulo) devem ser tratadas como potenciais falhas silenciosas. O orquestrador deve inspecionar o resultado semanticamente, não apenas o campo `status`.

---

**Q05.** Você está desenvolvendo um agente que lê emails, classifica-os por prioridade e arquiva automaticamente os menos importantes. Qual é a principal salvaguarda necessária antes de implantar em produção?

- A) Garantir que o agente use o modelo mais capaz disponível
- B) Implementar um período de "dry run" sem arquivamento real, revisar classificações humanas por pelo menos 1 semana, e manter um mecanismo de reversão (unarchive) antes de habilitar ações destrutivas
- C) Dar ao agente acesso apenas a emails com mais de 30 dias
- D) Configurar rate limiting para no máximo 10 emails por hora

> **Resposta: B** — Antes de ações irreversíveis em dados reais: dry run + validação humana + mecanismo de reversão. Arquivamento automático sem essas salvaguardas pode causar perda de informações importantes.

---

**Q06.** Seu agente usa parallel tool use para buscar dados de 5 APIs simultaneamente. Uma das APIs demora 30 segundos enquanto as outras retornam em 2 segundos. Qual é o comportamento correto do loop agêntico nessa situação?

- A) Claude cancela automaticamente a API lenta após 10 segundos e continua com os 4 resultados disponíveis
- B) Claude aguarda todos os tool results antes de gerar a resposta final — o timeout deve ser gerenciado na implementação da ferramenta, não pelo modelo
- C) Claude gera uma resposta parcial com os 4 resultados e atualiza quando o 5º chegar
- D) Claude automaticamente faz retry da API lenta em paralelo com a espera

> **Resposta: B** — O loop agêntico aguarda todos os `tool_result` antes de continuar. Timeouts e fallbacks são responsabilidade da implementação da ferramenta, não do modelo.

---

**Q07.** Você precisa construir um agente que pode criar, modificar e deletar registros em um CRM. Um usuário pede para "limpar todos os contatos inativos". Como o agente deve proceder?

- A) Executar a limpeza imediatamente — a instrução do usuário é clara
- B) Antes de qualquer deleção, listar os contatos que seriam afetados, apresentar ao usuário para confirmação explícita, e só então proceder — dado que deleção em massa é irreversível
- C) Criar um backup automático e então executar a limpeza sem confirmação
- D) Recusar a operação pois deleção em massa excede o escopo de um agente

> **Resposta: B** — Ações irreversíveis de alto impacto (deleção em massa) requerem confirmação humana explícita, mesmo quando o usuário pediu. "Limpar todos" pode significar coisas diferentes para o usuário e para o agente.

---

**Q08.** Você está projetando a memória de um agente de suporte ao cliente. O agente atende 1.000 clientes diferentes por dia. O que NÃO deve ser armazenado em memória persistente de longo prazo?

- A) Preferências de comunicação do cliente (ex: prefere respostas curtas)
- B) Histórico completo de todas as mensagens de todas as conversas de todos os clientes
- C) Tipos de problemas frequentemente reportados por categoria de produto
- D) Procedimentos de escalonamento que mudam raramente

> **Resposta: B** — Histórico completo de todas as conversas é dados brutos que crescem indefinidamente. Memória de longo prazo deve armazenar insights destilados, padrões e fatos não-óbvios — não logs completos.

---

**Q09.** Um agente Claude Code deve automaticamente fazer deploy de código em produção quando os testes passam. Qual configuração mínima de segurança é indispensável?

- A) Apenas garantir que os testes sejam completos antes do deploy
- B) Permissões restritas ao mínimo necessário (apenas comandos de deploy), hooks que validam a branch e o status dos testes, e um mecanismo de rollback testado — nunca deploy autônomo sem essas salvaguardas
- C) Desabilitar o modo interativo para que o deploy não seja interrompido por confirmações
- D) Usar `--dangerously-skip-permissions` para garantir que o deploy não falhe por permissões insuficientes

> **Resposta: B** — Deploy autônomo em produção exige: princípio do menor privilégio, validações via hooks, e rollback confiável. `--dangerously-skip-permissions` em produção é um anti-pattern de segurança.

---

**Q10.** Seu pipeline de análise de dados usa um agente Claude para interpretar resultados. Após uma atualização do modelo, você percebe que as interpretações mudaram sutilmente. Como detectar e gerenciar essa regressão?

- A) Reverter para a versão anterior do modelo e nunca atualizar
- B) Implementar um conjunto de evals com casos de teste curados e comparar outputs antes/depois de atualizações de modelo — pinning de versão de modelo em produção até validar
- C) Aceitar variações naturais de modelos como parte normal da operação
- D) Aumentar a temperatura para que o modelo explore mais opções e compense

> **Resposta: B** — Regressões de modelo são reais. Boas práticas: pinning de versão em produção, evals automatizadas como gate de atualização, e testes A/B antes de migrar.

---

**Q11.** Em uma arquitetura com agente orquestrador + 4 subagentes especializados, como garantir que uma falha em um subagente não corrompa silenciosamente o resultado final?

- A) Executar cada subagente duas vezes e comparar os resultados
- B) O orquestrador deve validar semanticamente cada resultado de subagente antes de usá-lo no pipeline, com critérios de aceitação claros para cada etapa
- C) Usar apenas subagentes com histórico de 100% de sucesso
- D) Desabilitar o subagente problemático e continuar com os demais

> **Resposta: B** — Validação de resultados intermediários é essencial em pipelines multi-agente. O orquestrador não deve assumir que `status: success` significa "resultado correto e utilizável".

---

**Q12.** Você precisa que o mesmo pipeline agêntico funcione tanto em ambiente de desenvolvimento (com logs verbosos e sem ações destrutivas) quanto em produção (com ações reais e logs estruturados). Qual é a melhor abordagem?

- A) Manter dois codebases separados para dev e produção
- B) Usar variáveis de ambiente para controlar o comportamento (modo dry-run, nível de log, confirmações automáticas), com o mesmo código base configurado diferentemente por ambiente
- C) Desabilitar todos os hooks em desenvolvimento para acelerar iteração
- D) Usar modelos diferentes (Haiku em dev, Opus em produção) como principal diferenciador

> **Resposta: B** — Feature flags via env vars (DRY_RUN=true, LOG_LEVEL=debug, REQUIRE_CONFIRMATION=false) é a abordagem padrão para paridade dev/prod sem duplicação de código.

---

## Domínio 2 — Claude Code Config (Q13–Q24)

**Q13.** Você está configurando Claude Code para um projeto com uma equipe de 5 desenvolvedores. Cada desenvolvedor tem preferências pessoais de formatação mas o projeto tem padrões compartilhados. Como organizar as configurações corretamente?

- A) Cada desenvolvedor cria seu próprio fork do projeto com suas configurações
- B) Padrões do projeto em `.claude/settings.json` (versionado); preferências pessoais em `.claude/settings.local.json` (no .gitignore de cada dev)
- C) Todas as configurações no `~/.claude/settings.json` global de cada desenvolvedor
- D) Usar apenas o `CLAUDE.md` para tudo, incluindo preferências pessoais

> **Resposta: B** — `.claude/settings.json` versionado = padrões do time. `.claude/settings.local.json` no gitignore = personalização individual. Essa separação é exatamente para esse caso de uso.

---

**Q14.** Um desenvolvedor do time está tendo problemas de performance — Claude Code está lento e às vezes falha. Você suspeita que os hooks configurados para o projeto são a causa. Como investigar?

- A) Deletar todos os hooks e recriar do zero
- B) Temporariamente desabilitar os hooks um a um, medir o impacto de cada um, e identificar qual causa a lentidão ou falha
- C) Substituir todos os hooks por scripts Python mais eficientes
- D) Aumentar o timeout padrão de todos os hooks para 5 minutos

> **Resposta: B** — Diagnóstico sistemático: desabilitar um hook por vez, medir, identificar o culpado. Deletar tudo de uma vez impede identificar a causa raiz.

---

**Q15.** Você quer que Claude Code rode `npm run lint` automaticamente após cada vez que editar um arquivo `.ts`. Qual é a configuração correta?

- A) Adicionar no `CLAUDE.md`: "sempre rode npm run lint após editar arquivos TypeScript"
- B) Configurar um hook `PostToolUse` (ou similar ao evento de edição de arquivo) em `settings.json` com o comando `npm run lint -- --files $FILE`
- C) Criar um custom command `/lint` que o desenvolvedor precisa chamar manualmente
- D) Adicionar no system prompt: "após cada edição de .ts, execute npm run lint"

> **Resposta: B** — Hooks são o mecanismo correto para automação baseada em eventos de ferramentas. O CLAUDE.md e system prompt são instruções textuais, não comandos executáveis automaticamente.

---

**Q16.** Sua empresa quer garantir que Claude Code nunca execute comandos `rm -rf` em nenhum projeto. Onde e como implementar essa restrição?

- A) Instruir todos os desenvolvedores via CLAUDE.md para não usar esse comando
- B) Configurar `blockedTools` ou um hook `PreToolUse` no `~/.claude/settings.json` global que intercepta e bloqueia execuções de Bash com pattern `rm -rf`
- C) Criar um alias de sistema que substitui `rm -rf` por um comando seguro
- D) Contar com o julgamento do modelo para nunca executar comandos destrutivos

> **Resposta: B** — Restrições de segurança críticas devem ser enforçadas via configuração (blockedTools ou hooks PreToolUse), não via instruções textuais que o modelo pode ignorar em edge cases.

---

**Q17.** Um script de CI/CD precisa usar Claude Code para analisar 200 PRs por dia sem interação humana. Como configurar corretamente?

- A) Executar `claude` interativamente e usar scripts de automação de terminal para simular input
- B) Usar `claude -p "analise este PR: {pr_diff}"` em modo não-interativo, com `--dangerously-skip-permissions` apenas se necessário em ambiente CI controlado com permissões restritas
- C) Criar um webhook que dispara uma sessão interativa do Claude Code automaticamente
- D) Usar a API Anthropic diretamente — Claude Code não é adequado para CI

> **Resposta: B** — `claude -p` é a flag documentada para uso não-interativo/headless em CI. `--dangerously-skip-permissions` pode ser necessário em CI mas exige que o ambiente já seja controlado e seguro.

---

**Q18.** Você percebe que o `CLAUDE.md` do projeto tem 5.000 palavras e inclui: o histórico completo do projeto, cada decisão técnica tomada nos últimos 2 anos, exemplos de código de todas as funções, e as regras de contribuição. Qual é o problema e como corrigir?

- A) Nenhum problema — quanto mais contexto, melhor
- B) CLAUDE.md excessivamente longo dilui as instruções importantes e aumenta custo de tokens. Refatorar: manter apenas regras de contribuição, convenções ativas e arquitetura atual; mover histórico para `Referencias/` com links
- C) O problema é o tamanho do arquivo no disco — usar compressão
- D) Dividir em múltiplos arquivos CLAUDE.md em subpastas

> **Resposta: B** — CLAUDE.md deve ser conciso e focado no que é sempre relevante. Histórico, exemplos exaustivos e decisões antigas devem viver em documentação referenciável, não carregada a cada sessão.

---

**Q19.** Você quer criar um custom command `/review-security` que aplica um checklist de segurança em qualquer arquivo. Como implementar?

- A) Adicionar uma função no `CLAUDE.md` que descreve o checklist
- B) Criar `~/.claude/commands/review-security.md` com o prompt detalhado do checklist de segurança — Claude o executará quando o usuário digitar `/review-security`
- C) Criar um script Python em `~/.claude/scripts/review_security.py`
- D) Registrar via `claude add-command --name review-security --prompt "..."`

> **Resposta: B** — Custom commands são arquivos markdown em `~/.claude/commands/` (ou `.claude/commands/` no projeto). O arquivo contém o prompt que será executado.

---

**Q20.** Um servidor MCP local precisa de uma API key para acessar um serviço externo. Qual é a forma correta de fornecer essa credencial?

- A) Hardcodar a API key diretamente no `args` do `mcpServers` em `settings.json`
- B) Passar a API key como variável de ambiente no campo `env` da configuração do mcpServer, armazenando o valor real em `.env` fora do controle de versão
- C) Incluir a API key no `CLAUDE.md` em uma seção de configuração
- D) Pedir ao usuário que cole a API key no chat quando o servidor solicitar

> **Resposta: B** — Credenciais nunca em arquivos versionados. A configuração de mcpServers suporta passar variáveis de ambiente para o processo do servidor, mantendo segredos fora do código.

---

**Q21.** Sua equipe quer compartilhar custom commands do Claude Code entre todos os membros. Como fazer isso?

- A) Cada desenvolvedor cria seus próprios comandos localmente — não é possível compartilhar
- B) Versionar os comandos em `.claude/commands/` no repositório do projeto — como essa pasta é versionada, todos que clonam o projeto têm os mesmos comandos disponíveis
- C) Compartilhar os arquivos via email ou Slack manualmente
- D) Usar um repositório separado apenas para comandos, referenciado via submódulo git

> **Resposta: B** — `.claude/commands/` no projeto é versionado e disponível para toda a equipe. `~/.claude/commands/` é pessoal do desenvolvedor.

---

**Q22.** Você está integrando Claude Code com GitHub Actions para review automático de PRs. O workflow precisa fazer checkout do código, analisar e comentar no PR. Qual é a configuração correta de permissões?

- A) Dar ao job permissão de admin no repositório para garantir que nada falhe
- B) Configurar permissões mínimas no GITHUB_TOKEN: `pull-requests: write` para comentários e `contents: read` para checkout — princípio do menor privilégio aplicado ao CI
- C) Usar um personal access token com acesso a todos os repositórios da organização
- D) Não configurar permissões — GitHub Actions tem acesso total por padrão

> **Resposta: B** — Menor privilégio também se aplica ao CI: apenas as permissões necessárias para a tarefa específica. Admin access em CI é um risco de segurança significativo.

---

**Q23.** Um desenvolvedor quer testar mudanças no `settings.json` do projeto sem afetar os outros membros da equipe que já têm o projeto clonado. Qual é a abordagem correta?

- A) Fazer as mudanças diretamente no `.claude/settings.json` e commitar para testar
- B) Usar `.claude/settings.local.json` (que está no .gitignore) para testar localmente antes de propor mudanças via PR no `settings.json` principal
- C) Criar uma branch separada apenas para testar configurações
- D) Fazer backup do settings.json, modificar, testar, e restaurar manualmente

> **Resposta: B** — `settings.local.json` é exatamente para isso: experimentar configurações localmente sem impactar o time. Depois de validado, propor a mudança via PR no `settings.json` compartilhado.

---

**Q24.** Você está recebendo erros de "context too long" em sessões longas do Claude Code. Qual configuração ou abordagem resolve isso sem perder continuidade?

- A) Aumentar `max_tokens` nas configurações do projeto
- B) O Claude Code gerencia compressão automaticamente, mas você pode ajudar estruturando o trabalho em tarefas menores, usando `/clear` para reiniciar quando apropriado, e confiando no CLAUDE.md para reconstituir contexto essencial
- C) Dividir o projeto em múltiplos repositórios menores
- D) Usar apenas modelos com janela de contexto maior

> **Resposta: B** — Compressão automática é o comportamento padrão. Para sessões muito longas: `/clear` + CLAUDE.md bem estruturado (que reconstitui contexto essencial) é mais eficaz que tentar manter tudo em memória.

---

## Domínio 3 — Prompt Engineering (Q25–Q36)

**Q25.** Você está construindo um assistente para extrair dados estruturados de contratos em PDF. O formato de output deve ser JSON com 15 campos específicos. Qual técnica de prompt é mais eficaz?

- A) Descrever os 15 campos em texto narrativo e deixar Claude escolher o formato
- B) Fornecer o schema JSON exato esperado + 2-3 exemplos concretos de input (trecho de contrato) → output (JSON preenchido), com instrução explícita para retornar apenas JSON válido
- C) Usar apenas zero-shot com temperatura 0 para maximizar determinismo
- D) Pedir ao Claude que primeiro liste os campos encontrados e depois formate em JSON

> **Resposta: B** — Para extração estruturada: schema explícito + few-shot examples de input/output + instrução de formato é o trio mais eficaz. Zero-shot sem exemplos frequentemente produz JSON com campos faltando ou mal mapeados.

---

**Q26.** Seu sistema de QA automatizado com Claude está retornando falsos positivos (classifica código correto como bugado). Como melhorar a precisão com prompt engineering?

- A) Aumentar a temperatura para que Claude seja menos assertivo
- B) Adicionar exemplos few-shot de "código correto que não é bug" (casos negativos) e refinar o critério de classificação com definições precisas do que constitui um bug no contexto do projeto
- C) Pedir ao Claude para ser mais conservador e duvidar de seus próprios julgamentos
- D) Trocar para um modelo menor que é mais conservador em suas classificações

> **Resposta: B** — Few-shot com exemplos negativos (casos que NÃO são bugs) é essencial para calibrar classificadores. Definições precisas de "bug" no contexto específico reduzem interpretações equivocadas.

---

**Q27.** Um prompt de system para um chatbot de atendimento tem crescido organicamente e agora tem 8.000 tokens com instruções contraditórias. Quais são os sintomas e a solução?

- A) 8.000 tokens é o tamanho ideal — mais contexto sempre melhora
- B) Sintomas: respostas inconsistentes, Claude ignorando algumas instruções, comportamentos imprevisíveis. Solução: auditoria completa do prompt, remoção de redundâncias e contradições, estruturação com XML tags por seção, teste empírico após cada mudança
- C) Solução: mover metade das instruções para o human turn
- D) Solução: dividir em dois modelos, cada um com metade das instruções

> **Resposta: B** — Instruções contraditórias + volume excessivo = comportamento imprevisível. A solução é revisão estruturada, não apenas redução de tamanho. XML tags por seção ajudam Claude a priorizar corretamente.

---

**Q28.** Você precisa que Claude analise código e detecte vulnerabilidades de segurança APENAS nas categorias OWASP Top 10 — sem reportar outros tipos de problemas. Como garantir isso no prompt?

- A) Confiar no conhecimento do modelo sobre OWASP sem especificação adicional
- B) Listar explicitamente as 10 categorias OWASP no prompt + instrução negativa clara ("não reporte vulnerabilidades fora dessas categorias") + exemplo de output mostrando como categorizar corretamente
- C) Pedir ao Claude para "focar em segurança" e filtrar os resultados no pós-processamento
- D) Usar temperatura 0 que naturalmente limita o escopo das respostas

> **Resposta: B** — Escopo preciso requer: lista explícita das categorias permitidas + instrução negativa explícita de exclusão + exemplo demonstrando o comportamento esperado. Confiança implícita no modelo sem especificação resulta em escopo não controlado.

---

**Q29.** Um sistema RAG usa Claude para responder perguntas sobre documentação interna. O sistema frequentemente "alucina" informações que não estão nos documentos. Qual é a modificação mais impactante no prompt?

- A) Aumentar o número de documentos recuperados para dar mais contexto ao modelo
- B) Adicionar instrução explícita: "responda APENAS com base nos documentos fornecidos entre as tags <docs>. Se a informação não estiver nos documentos, responda 'Não encontrei essa informação na documentação disponível.'"
- C) Usar temperatura 0 para eliminar criatividade nas respostas
- D) Trocar para um modelo maior que "sabe mais"

> **Resposta: B** — A instrução explícita de grounding ("apenas com base nos docs") + instrução de fallback explícita ("diga quando não encontrar") é a mudança mais impactante. Temperatura 0 não previne alucinação; modelos maiores também alucinam.

---

**Q30.** Você está escrevendo um prompt para Claude resumir artigos científicos para um público não especialista. O prompt atual produz resumos muito técnicos. Como corrigir?

- A) Pedir ao Claude para "simplificar" — é suficientemente claro
- B) Especificar o público-alvo com precisão ("escreva para alguém com ensino médio completo sem formação científica"), adicionar restrições de vocabulário ("evite jargão técnico; quando necessário, explique o termo em linguagem simples") e fornecer um exemplo de resumo no estilo desejado
- C) Reduzir o max_tokens para forçar resumos mais curtos e simples
- D) Usar role prompting pedindo para Claude ser "um professor do ensino médio" apenas

> **Resposta: B** — "Simplificar" é ambíguo. Definição precisa do público + restrições explícitas de vocabulário + exemplo do estilo desejado são muito mais eficazes que role prompting genérico.

---

**Q31.** Você testou um prompt em 50 casos e ele funciona em 46 mas falha em 4 casos específicos. Qual é a abordagem de prompt engineering correta?

- A) Aceitar 92% de acurácia como suficiente e ir para produção
- B) Analisar os 4 casos de falha para identificar o padrão: adicionar examples dos casos de borda ao prompt, ou adicionar instruções específicas para esses padrões — sem degradar os 46 casos que já funcionam
- C) Aumentar drasticamente a temperatura para que o modelo "tente mais opções"
- D) Reescrever o prompt completamente do zero para os 4 casos problemáticos

> **Resposta: B** — Debugging de prompt: analisar padrões de falha → adições cirúrgicas (few-shot de casos de borda, instruções específicas) → testar que os 46 casos anteriores ainda funcionam. Reescrever completamente frequentemente destrói o que já funcionava.

---

**Q32.** Seu agente precisa fazer uma série de perguntas de esclarecimento ao usuário antes de executar uma tarefa complexa. Como estruturar isso no prompt?

- A) Pedir ao Claude para "fazer perguntas quando necessário"
- B) Definir explicitamente as condições que disparam perguntas ("se o usuário não especificou [X], pergunte [pergunta específica] antes de prosseguir"), limitar o número de perguntas por turno e priorizar as mais críticas
- C) Instruir Claude a sempre fazer 3 perguntas independente do contexto
- D) Deixar o usuário especificar tudo upfront na interface antes de acionar o agente

> **Resposta: B** — Perguntas sem estrutura levam a interrogatórios frustrantes. Condições claras + limite de perguntas por turno + priorização das críticas resulta em uma experiência de esclarecimento eficiente.

---

**Q33.** Um modelo Claude em produção começa a produzir respostas diferentes após uma atualização de versão. Você precisa garantir estabilidade. Qual é a prática documentada para isso?

- A) Sempre usar o alias `claude-latest` para garantir as correções mais recentes
- B) Fazer pinning da versão específica do modelo (ex: `claude-sonnet-4-6`) em produção, validar evals antes de migrar para nova versão, manter o alias `latest` apenas em desenvolvimento
- C) Reescrever o prompt a cada atualização de modelo para compensar diferenças
- D) Usar sempre o modelo mais antigo disponível para máxima estabilidade

> **Resposta: B** — Pinning de versão de modelo é essencial em produção. `claude-latest` em produção é um anti-pattern: uma atualização silenciosa pode quebrar comportamentos críticos.

---

**Q34.** Você percebe que Claude frequentemente adiciona disclaimers longos e desnecessários em respostas de um sistema de análise financeira interna, onde os usuários são analistas experts. Como eliminar esse comportamento?

- A) Aceitar os disclaimers como comportamento de segurança imutável do modelo
- B) Adicionar instrução explícita no system prompt: "os usuários são analistas financeiros certificados — omita disclaimers genéricos sobre consultar especialistas ou verificar informações" + especificar o tom técnico esperado
- C) Usar temperatura 0 para tornar as respostas mais diretas
- D) Remover o system prompt completamente

> **Resposta: B** — Claude ajusta o nível de disclaimers baseado no contexto fornecido. Especificar a expertise do público-alvo e instruir explicitamente sobre tom/disclaimers no system prompt é eficaz.

---

**Q35.** Você está construindo um pipeline que processa o mesmo tipo de documento repetidamente com instruções fixas e apenas o documento muda. Como otimizar o custo e latência dessa arquitetura?

- A) Comprimir o prompt de sistema a cada chamada para reduzir tokens
- B) Usar prompt caching: marcar o system prompt fixo como cacheável — ele será processado uma vez e reutilizado nas chamadas subsequentes, reduzindo significativamente custo e latência
- C) Enviar apenas o documento sem system prompt para economizar tokens
- D) Usar um modelo menor apenas para esse pipeline

> **Resposta: B** — Prompt caching é exatamente para esse padrão: system prompt longo e fixo + conteúdo variável. A parte fixa é cacheada, o documento variável é processado normalmente.

---

**Q36.** Um usuário reporta que o agente "mudou de opinião" no meio de uma análise longa, contradizendo conclusões anteriores no mesmo contexto. Qual é a causa mais provável e como mitigar?

- A) Bug no código da aplicação — não é problema de prompt
- B) Degradação de atenção em contextos muito longos: o modelo pode perder consistência com conclusões distantes no contexto. Mitigação: structured reasoning (anotar conclusões intermediárias explicitamente), resumir decisões chave em formato que persista no contexto, ou dividir em análises menores com checkpoints
- C) O usuário está confundindo duas sessões diferentes
- D) Aumentar max_tokens para que o modelo tenha "mais espaço para pensar"

> **Resposta: B** — Inconsistência em contextos longos é um fenômeno conhecido. Mitigações: annotations explícitas de conclusões ("CONCLUSÃO PARCIAL: X"), seções de resumo intermediárias, ou reduzir o tamanho do problema sendo processado de uma vez.

---

## Domínio 4 — Tool Design & MCP (Q37–Q48)

**Q37.** Você precisa criar uma ferramenta MCP que permite ao agente pesquisar e atualizar tickets no Jira. Como separar corretamente as responsabilidades entre múltiplas ferramentas?

- A) Uma única ferramenta `jira_operations` com um parâmetro `action` (search/create/update/delete)
- B) Ferramentas separadas: `jira_search_tickets`, `jira_get_ticket`, `jira_update_ticket`, `jira_create_ticket` — cada uma com schema específico e descrição clara de quando usar cada uma
- C) Uma ferramenta por endpoint da API do Jira, independente do número
- D) Apenas ferramentas de leitura — escrita deve ser feita diretamente via API

> **Resposta: B** — Ferramentas granulares com nomes semânticos permitem ao modelo selecionar com precisão. Uma ferramenta genérica `do_jira` com parâmetro `action` é ambígua e dificulta o modelo escolher corretamente.

---

**Q38.** Um servidor MCP que você está desenvolvendo precisa retornar erros de forma que o agente possa raciocinar sobre eles. Qual é o formato correto de retorno de erro em uma tool call MCP?

- A) Lançar uma exceção que encerra a conexão MCP
- B) Retornar um `tool_result` com `isError: true` e uma mensagem descritiva do erro — o modelo recebe o erro como conteúdo e pode decidir o próximo passo
- C) Retornar HTTP 500 que o cliente MCP automaticamente traduz em mensagem de erro
- D) Retornar `null` para indicar ausência de resultado

> **Resposta: B** — Erros em tools MCP devem ser retornados como tool_result com `isError: true` e descrição útil. Isso mantém o loop agêntico funcionando — o modelo pode raciocinar sobre o erro ao invés de receber uma exceção que quebra o fluxo.

---

**Q39.** Você está implementando um servidor MCP que consulta um banco de dados com queries potencialmente lentas (5-30 segundos). Como lidar com isso corretamente?

- A) Configurar timeout de 5 segundos e retornar erro se a query demorar mais
- B) Implementar a query de forma síncrona com timeout generoso, retornar resultado quando concluído — ou usar Tasks (experimental) para operações de longa duração com recuperação de resultado diferida
- C) Executar queries em background e retornar imediatamente com `status: "processing"`
- D) Limitar todas as queries a no máximo 1 segundo via LIMIT na SQL

> **Resposta: B** — Para operações longas: resposta síncrona com timeout adequado é a abordagem padrão. Para operações muito longas, Tasks (experimental) do MCP oferece durable execution com polling de status.

---

**Q40.** Você está projetando uma ferramenta MCP de busca que aceita uma string de query. Um usuário malicioso pode tentar injetar SQL através dessa ferramenta. Como proteger?

- A) Confiar que Claude vai sanitizar o input antes de passar para a ferramenta
- B) Na implementação da ferramenta: usar queries parametrizadas (prepared statements), nunca interpolação de string direta, validar e sanitizar o input no servidor MCP — nunca depender do modelo para segurança
- C) Limitar o comprimento máximo da query a 100 caracteres
- D) Usar apenas stored procedures que aceitam tipos específicos

> **Resposta: B** — Segurança deve ser implementada na ferramenta, não delegada ao modelo. Queries parametrizadas são o padrão para prevenir SQL injection — o modelo não é uma barreira de segurança confiável.

---

**Q41.** Um cliente MCP precisa descobrir quais ferramentas um servidor oferece antes de iniciar operações. Qual é a sequência correta segundo o protocolo MCP?

- A) O servidor envia automaticamente a lista de tools na mensagem de boas-vindas
- B) Cliente envia `initialize` → servidor responde com capabilities → cliente envia `notifications/initialized` → cliente chama `tools/list` para descobrir as ferramentas disponíveis
- C) Cliente chama `tools/list` diretamente sem inicialização prévia
- D) O host configura as tools no momento da inicialização do servidor, sem necessidade de discovery

> **Resposta: B** — O ciclo de vida MCP é: (1) initialize/response para capability negotiation, (2) initialized notification do cliente, (3) tools/list para discovery. Chamar tools/call sem tools/list primeiro é possível mas não recomendado.

---

**Q42.** Você está construindo um MCP server que expõe acesso ao filesystem local. Quais são as principais considerações de segurança?

- A) Expor o filesystem completo para que o agente tenha máxima flexibilidade
- B) Restringir acesso a diretórios específicos (sandboxing), validar que paths não escapam do diretório permitido (path traversal prevention), limitar operações de escrita/deleção a caminhos autorizados
- C) Usar apenas operações de leitura — nunca expor escrita via MCP
- D) Exigir autenticação OAuth para cada operação de arquivo individual

> **Resposta: B** — Filesystem MCP exige: sandbox de diretório (whitelist de paths), prevenção de path traversal (../../../etc/passwd), e permissões granulares (leitura vs escrita por diretório).

---

**Q43.** Um MCP server remoto usando Streamable HTTP precisa autenticar clientes. Qual método é recomendado pela especificação MCP?

- A) Basic authentication com usuário e senha em cada request
- B) OAuth — o MCP recomenda usar OAuth para obter tokens de autenticação no transport Streamable HTTP
- C) API keys fixas hardcodadas no servidor
- D) Autenticação via certificado TLS mútuo apenas

> **Resposta: B** — Documentação MCP: "MCP recommends using OAuth to obtain authentication tokens" para o Streamable HTTP transport.

---

**Q44.** Você quer que seu MCP server notifique o cliente quando novas ferramentas ficam disponíveis (ex: após uma feature ser habilitada). O que é necessário na implementação?

- A) O cliente precisa fazer polling periódico de `tools/list` para detectar mudanças
- B) O servidor deve declarar `"tools": {"listChanged": true}` nas suas capabilities durante initialize, e então enviar `notifications/tools/list_changed` (sem id, sem response esperada) quando a lista mudar
- C) Reiniciar a conexão MCP completa quando as tools mudarem
- D) Enviar um `tools/list` response atualizado sem que o cliente solicite

> **Resposta: B** — Para notificações dinâmicas de tools: (1) declarar `listChanged: true` nas capabilities, (2) enviar notificação JSON-RPC sem id quando mudar. O cliente então fará `tools/list` para atualizar seu registro.

---

**Q45.** Como a primitiva "Resource" do MCP difere de uma "Tool" em termos de casos de uso práticos?

- A) Resources são mais rápidos que Tools para qualquer operação
- B) Resources fornecem dados contextuais para leitura (ex: schema de banco, conteúdo de arquivo, política da empresa) sem efeitos colaterais; Tools executam ações que modificam estado (ex: criar registro, enviar email)
- C) Resources são definidos pelo cliente; Tools pelo servidor
- D) Resources retornam JSON; Tools retornam texto livre

> **Resposta: B** — Semântica MCP: Resources = dados/contexto read-only. Tools = ações com potenciais efeitos colaterais. Um "schema do banco" é um Resource; "executar query" é uma Tool.

---

**Q46.** Você precisa implementar uma ferramenta que cria usuários em um sistema. Como garantir que chamadas acidentalmente duplicadas não criem dois usuários com os mesmos dados?

- A) Limitar o rate de chamadas a 1 por minuto
- B) Implementar idempotência: verificar se o usuário com aquele email/ID já existe antes de criar, retornar o usuário existente se já houver — same input sempre produz same output
- C) Gerar um UUID aleatório para cada chamada tornando cada criação única
- D) Adicionar um parâmetro `idempotency_key` obrigatório que o modelo deve gerar

> **Resposta: B** — Idempotência em ferramentas de criação: verificar existência antes de criar (upsert pattern). O modelo pode tentar re-executar uma ferramenta em caso de falha de rede — idempotência garante que isso seja seguro.

---

**Q47.** Em qual situação você usaria a primitiva "Prompt" do MCP em vez de simplesmente incluir o prompt no system prompt do cliente?

- A) Prompts MCP são sempre preferíveis a system prompts — nunca use system prompts
- B) Quando o prompt é reutilizável entre múltiplos contextos, ou quando o servidor tem domínio específico e deve definir os templates de interação (ex: servidor de banco de dados fornece template few-shot de como formular queries)
- C) Apenas quando o system prompt excede 1.000 tokens
- D) Quando o prompt precisa mudar dinamicamente a cada requisição

> **Resposta: B** — Prompts MCP são templates reutilizáveis expostos pelo servidor que tem o contexto de domínio (ex: few-shot para queries SQL, instruções de formatação de relatório). O cliente os descobre via `prompts/list` e os usa como templates.

---

**Q48.** Um agente está fazendo múltiplas chamadas de ferramentas para buscar dados de APIs diferentes e montar um relatório. Como estruturar o retorno das ferramentas para maximizar a utilidade para o modelo?

- A) Retornar dados brutos no formato nativo de cada API (XML, JSON, CSV conforme a API original)
- B) Normalizar os retornos em um formato consistente, incluir apenas os campos relevantes para a tarefa do agente, e adicionar metadados úteis (ex: timestamp, fonte, unidade dos valores) — facilita o modelo montar o relatório coerentemente
- C) Retornar sempre o máximo de dados possível para que o modelo escolha o que usar
- D) Comprimir os dados em base64 para economizar tokens de context

> **Resposta: B** — Ferramentas bem projetadas pré-processam dados para o modelo: formato consistente, campos relevantes, metadados contextuais. "Máximo de dados" desperdiça tokens e confunde o modelo.

---

## Domínio 5 — Context & Reliability (Q49–Q60)

**Q49.** Um sistema RAG retorna frequentemente documentos irrelevantes que degradam a qualidade das respostas do Claude. Qual é a causa mais provável e como corrigir?

- A) O modelo Claude está ignorando os documentos fornecidos
- B) Problema de retrieval: embeddings ou lógica de busca mal calibrados. Melhorar: ajustar o modelo de embedding, usar busca híbrida (semântica + keyword), implementar re-ranking dos resultados, e aumentar precision do retrieval mesmo que reduza recall
- C) Fornecer mais documentos para compensar a irrelevância dos primeiros
- D) Trocar Claude por um modelo com maior janela de contexto

> **Resposta: B** — A qualidade do RAG depende primariamente da qualidade do retrieval. "Garbage in, garbage out" — documentos irrelevantes no contexto degradam o modelo mesmo que seja excelente. A solução está no pipeline de retrieval.

---

**Q50.** Você está projetando um sistema onde Claude deve gerar código Python que será executado automaticamente. Qual é o conjunto mínimo de salvaguardas necessário?

- A) Confiar no código gerado pelo Claude — modelos avançados raramente geram código com bugs
- B) Executar em sandbox isolado (sem acesso à rede, filesystem restrito, CPU/memória limitados), validar o código com análise estática antes da execução, limitar timeouts de execução, e revisar código que acessa recursos externos
- C) Usar apenas `eval()` restrito a expressões matemáticas
- D) Executar o código uma vez em staging antes de produção

> **Resposta: B** — Código gerado por IA deve ser executado em sandbox com recursos limitados. Análise estática + sandboxing + timeouts são as salvaguardas mínimas para execução automática.

---

**Q51.** Um pipeline de 10 etapas falha na etapa 8 após 2 horas de processamento. Como arquitetar o sistema para evitar perda de trabalho nesse cenário?

- A) Aumentar o timeout para 4 horas e re-executar do início quando falhar
- B) Implementar checkpoints persistentes após cada etapa (salvar estado em banco/arquivo), com lógica de retry que retoma da última etapa com checkpoint bem-sucedido
- C) Executar todas as 10 etapas em paralelo para que a falha de uma não afete as outras
- D) Dividir em 5 pipelines de 2 etapas cada, executados sequencialmente

> **Resposta: B** — Checkpoints são o padrão para pipelines longos. Reexecutar do zero desperdiça recursos e tempo. Estado persistente entre etapas transforma uma falha catastrófica em uma recuperação pontual.

---

**Q52.** Você precisa garantir que um agente Claude Code responda de forma consistente à mesma pergunta quando chamado múltiplas vezes. Qual configuração maximiza o determinismo?

- A) `temperature: 1.0` para gerar sempre a mesma resposta "mais provável"
- B) `temperature: 0` — maximiza determinismo escolhendo sempre o token de maior probabilidade; para casos críticos, adicionar top_k e top_p restritivos
- C) Usar seed fixo na API para garantir reprodutibilidade perfeita
- D) Desabilitar tool use para reduzir variabilidade

> **Resposta: B** — `temperature: 0` é o principal controle de determinismo disponível na API. Nota: não garante 100% de determinismo em todos os cenários (há aleatoriedade em infraestrutura distribuída), mas é o máximo que a API oferece.

---

**Q53.** Um sistema de monitoramento mostra que as respostas do Claude estão se degradando gradualmente ao longo de sessões longas — as primeiras respostas são excelentes mas as tardias ficam vagas. O que está acontecendo e como mitigar?

- A) O modelo "cansa" com uso prolongado — reiniciar o servidor corrige
- B) Degradação de atenção em contextos muito longos: o modelo presta menos atenção a informações distantes no contexto. Mitigações: resumir periodicamente a sessão, usar `/clear` e reiniciar com contexto destilado, ou dividir em sessões menores com handoff explícito de estado
- C) Problema de rede — as últimas requisições chegam com mais latência
- D) Aumentar max_tokens para que o modelo "tenha mais espaço"

> **Resposta: B** — Contextos muito longos sofrem de "lost in the middle" — informações no meio/início do contexto recebem menos atenção. Sessões mais curtas com handoff de estado explícito é mais confiável que uma sessão infinita.

---

**Q54.** Você está avaliando se deve usar Claude Haiku ou Claude Opus para um sistema de classificação de sentimento em reviews de produtos (positivo/neutro/negativo). Qual é a abordagem correta de decisão?

- A) Sempre usar Opus — confiabilidade máxima independente do custo
- B) Testar ambos com um eval set representativo dos seus dados, medir acurácia, analisar casos de falha — Haiku pode ser suficiente para classificação binária/ternária simples com instruções claras, economizando 10-20x no custo
- C) Sempre usar Haiku — classificação simples não precisa de modelo avançado
- D) Usar Sonnet como meio-termo sem testar

> **Resposta: B** — A escolha de modelo deve ser baseada em evidências do caso de uso específico, não em generalizações. Evals com seus dados reais são a única forma confiável de decidir.

---

**Q55.** Um agente autônomo precisa enviar emails automaticamente em nome de usuários. Quais são as salvaguardas mínimas obrigatórias antes de habilitar isso em produção?

- A) Apenas garantir que o agente use o modelo mais capaz
- B) Rate limiting estrito (ex: máximo N emails/hora), revisão humana obrigatória para destinatários externos à organização, logs de auditoria de todos os emails enviados, mecanismo de opt-out para usuários, e período de beta fechado com supervisão manual
- C) Configurar o modelo com temperature: 0 para máxima consistência
- D) Criar um email de "agente" separado para que seja identificável

> **Resposta: B** — Ações que afetam terceiros (emails externos) requerem salvaguardas robustas: rate limiting, supervisão, auditoria e opt-out. Emails automatizados sem controle podem causar dano de reputação e problemas legais.

---

**Q56.** Como implementar observabilidade eficaz em um sistema multi-agente de produção com Claude Code?

- A) Salvar apenas o output final de cada sessão para análise posterior
- B) Implementar tracing distribuído com IDs de correlação por pipeline, logging estruturado (JSON) de cada tool call com parâmetros e resultado, métricas de latência e taxa de erro por etapa, e alertas para anomalias de comportamento do agente
- C) Usar apenas o logging padrão do Claude Code sem customização
- D) Monitorar apenas uso de tokens como proxy de qualidade

> **Resposta: B** — Observabilidade em sistemas agênticos requer: IDs de correlação (rastrear req end-to-end), structured logging (consultável), métricas operacionais, e alertas semânticos (não só técnicos).

---

**Q57.** Um usuário descobre que pode fazer o agente ignorar o system prompt injetando instruções em um documento que o agente processa. Qual é a mitigação técnica mais robusta?

- A) Aumentar a especificidade do system prompt para "cobrir" mais casos
- B) Estruturar o prompt com separação clara entre instruções (system prompt) e dados externos (user content), usar XML tags para demarcar conteúdo externo, adicionar instrução explícita de que conteúdo nos dados não pode sobrescrever instruções do sistema, e considerar filtros de conteúdo pré-processamento
- C) Codificar o system prompt em base64 para que o usuário não consiga lê-lo
- D) Restringir documentos a formatos que não suportam texto (apenas imagens)

> **Resposta: B** — Mitigação de prompt injection: separação estrutural clara (XML tags), instrução explícita de autoridade do system prompt, e pré-processamento/sanitização de conteúdo externo. Não existe solução perfeita, mas a combinação reduz significativamente o risco.

---

**Q58.** Você precisa migrar um sistema de Claude Sonnet 3.7 para Claude Sonnet 4.6. Qual é o processo correto para garantir que não há regressões?

- A) Atualizar o model ID em produção diretamente — modelos mais novos são sempre melhores
- B) Criar um eval set dos casos de uso críticos, rodar ambos os modelos em paralelo nos mesmos inputs, comparar outputs quantitativa e qualitativamente, identificar regressões antes de migrar tráfego, e migrar gradualmente (canary release)
- C) Testar apenas os 5 casos de uso mais frequentes e migrar se passarem
- D) Migrar em staging apenas e assumir que produção se comportará igual

> **Resposta: B** — Migração de modelo exige evals robustos + comparação paralela + migração gradual. Modelos mais novos geralmente são melhores mas podem ter comportamentos diferentes em casos específicos do seu domínio.

---

**Q59.** Você detecta que o agente está consumindo tokens em excesso por incluir contexto desnecessário em cada chamada. Como otimizar sem perder qualidade?

- A) Reduzir o max_tokens para forçar respostas mais curtas
- B) Auditoria do que está sendo incluído no contexto: remover informações redundantes, usar prompt caching para partes fixas, implementar RAG para fornecer apenas contexto relevante por query, e usar sumarização de histórico em vez de histórico completo
- C) Trocar para um modelo menor que processa menos tokens
- D) Limitar o número de tool calls por sessão

> **Resposta: B** — Otimização de tokens: (1) auditoria do que está no contexto, (2) cache para partes fixas, (3) RAG para contexto dinâmico relevante, (4) sumarização em vez de histórico bruto. Reduzir max_tokens degrada qualidade.

---

**Q60.** Um arquiteto precisa decidir entre duas abordagens para um sistema de análise: (A) um agente único com muitas ferramentas vs. (B) múltiplos agentes especializados orquestrados. Quais são os trade-offs corretos?

- A) (A) é sempre superior pois evita latência de comunicação entre agentes
- B) (A) é mais simples para tarefas menores com ferramentas complementares; (B) é superior para tarefas complexas onde especialização melhora qualidade, paralelismo aumenta throughput, e isolamento de contexto reduz interferência — a escolha depende da complexidade e dos requisitos de performance e manutenibilidade
- C) (B) é sempre superior pois especialização sempre melhora qualidade
- D) A decisão deve ser baseada apenas no custo — (A) é mais barato portanto preferível

> **Resposta: B** — A resposta correta reconhece os trade-offs reais: agente único é mais simples e suficiente para tarefas coesas; multi-agente adiciona complexidade mas oferece paralelismo, especialização e isolamento. A escolha é contextual.

---

## Distribuição por Domínio

| Domínio | Questões | % do Exame |
|---------|----------|------------|
| Agentic Architecture | Q01–Q12 | 20% |
| Claude Code Config | Q13–Q24 | 20% |
| Prompt Engineering | Q25–Q36 | 20% |
| Tool Design & MCP | Q37–Q48 | 20% |
| Context & Reliability | Q49–Q60 | 20% |

---

## Dica de Estudo

As questões deste simulado exigem aplicar conhecimento a cenários — não apenas memorizar definições. Para cada questão errada, identifique:
1. Qual conceito fundamental você não domina ainda
2. Qual documentação oficial consultar (docs.anthropic.com / modelcontextprotocol.io)
3. Como o conceito se aplica ao seu contexto de trabalho real

---

*Simulado 3 — questões orientadas a cenários e decisões arquiteturais. Não é material oficial da Anthropic.*
