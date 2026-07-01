---
titulo: "Simulado 1 — Claude Architect Certification: Claude Code Foundations"
data_criacao: 2026-04-09
data_atualizacao: 2026-04-09
tema: "Estudo"
cliente: "Interno"
status: "ativo"
tags: [simulado, certificacao, claude-code, anthropic, estudo]
---

# Simulado 1 — Claude Architect Certification: Claude Code Foundations

**60 questões | Múltipla escolha | Resposta correta indicada após cada questão**

---

## Domínio 1 — Agentic Architecture (Q01–Q12)

**Q01.** Em uma arquitetura multi-agente com Claude Code, qual é o papel principal do agente "orquestrador"?

- A) Executar diretamente todas as ferramentas disponíveis no sistema
- B) Decompor tarefas complexas e direcionar subagentes especializados
- C) Armazenar o histórico de contexto de todos os subagentes
- D) Validar os outputs de ferramentas MCP antes de retorná-los ao usuário

> **Resposta: B**

---

**Q02.** Qual das seguintes afirmações melhor descreve o padrão "ReAct" em sistemas agênticos?

- A) O modelo apenas reage a eventos externos sem raciocinar sobre eles
- B) O modelo alterna entre raciocínio (Reasoning) e ação (Acting) de forma iterativa
- C) O modelo rejeita ações que não estejam em sua lista de ferramentas pré-aprovadas
- D) O modelo recompila o contexto a cada turno descartando o histórico anterior

> **Resposta: B**

---

**Q03.** Em qual cenário o uso de subagentes paralelos é MAIS indicado?

- A) Quando as tarefas têm dependências sequenciais estritas entre si
- B) Quando é necessário manter um único contexto compartilhado e atômico
- C) Quando tarefas independentes podem ser executadas simultaneamente para ganho de performance
- D) Quando o orquestrador precisa validar cada etapa antes de iniciar a próxima

> **Resposta: C**

---

**Q04.** O que é "blast radius" no contexto de ações agênticas?

- A) O número de tokens consumidos por uma chamada de ferramenta
- B) O escopo de impacto e reversibilidade de uma ação tomada pelo agente
- C) A latência máxima tolerável em pipelines de agentes encadeados
- D) O limite de chamadas de API por sessão de um agente autônomo

> **Resposta: B**

---

**Q05.** Qual estratégia reduz o risco de "prompt injection" em pipelines agênticos que processam dados externos?

- A) Aumentar o tamanho da janela de contexto do modelo
- B) Tratar todo conteúdo de fontes externas como potencialmente não confiável e sanitizá-lo
- C) Desabilitar ferramentas de leitura de arquivos no agente
- D) Usar apenas modelos de linguagem menores para tarefas de processamento de dados

> **Resposta: B**

---

**Q06.** Em uma arquitetura com memória persistente, qual tipo de dado é MAIS adequado para armazenar em memória de longo prazo entre sessões?

- A) O histórico completo de mensagens da conversa atual
- B) Fatos não-óbvios sobre preferências do usuário e decisões arquiteturais do projeto
- C) Resultados intermediários de ferramentas executadas na sessão corrente
- D) Logs de debug de chamadas MCP da sessão anterior

> **Resposta: B**

---

**Q07.** Qual é a principal vantagem do padrão "tool-use loop" sobre uma única chamada de ferramenta?

- A) Reduz o número total de tokens consumidos por sessão
- B) Permite que o modelo observe resultados parciais e ajuste o plano de ação iterativamente
- C) Garante que todas as ferramentas sejam chamadas exatamente uma vez por turno
- D) Elimina a necessidade de tratamento de erros nas ferramentas

> **Resposta: B**

---

**Q08.** Quando um subagente retorna um resultado inesperado em um pipeline orquestrado, qual é a abordagem recomendada?

- A) Ignorar o resultado e continuar o pipeline com valores padrão
- B) Encerrar toda a sessão e solicitar que o usuário reinicie
- C) O orquestrador deve diagnosticar a falha antes de tentar alternativas ou escalar ao usuário
- D) Chamar o mesmo subagente repetidamente até obter o resultado esperado

> **Resposta: C**

---

**Q09.** Qual das seguintes características define um agente "stateless" (sem estado)?

- A) O agente mantém memória entre chamadas usando variáveis globais
- B) Cada invocação do agente é independente e não depende de execuções anteriores
- C) O agente não pode usar ferramentas externas durante sua execução
- D) O agente processa apenas um tipo de input por vez

> **Resposta: B**

---

**Q10.** No contexto de Claude Code, o que diferencia uma "action" de uma "observation" no loop agêntico?

- A) Actions são produzidas pelo usuário; observations são produzidas pelo modelo
- B) Actions são chamadas de ferramentas iniciadas pelo modelo; observations são os resultados retornados
- C) Actions modificam arquivos; observations apenas leem dados
- D) Actions são síncronas; observations são sempre assíncronas

> **Resposta: B**

---

**Q11.** Qual é o risco principal de conceder permissões excessivamente amplas a um agente autônomo?

- A) O agente pode consumir mais tokens do que o necessário por sessão
- B) O agente pode executar ações irreversíveis com grande impacto fora do escopo pretendido
- C) O agente passa a ignorar as instruções do sistema configuradas
- D) O tempo de resposta do agente aumenta proporcionalmente às permissões concedidas

> **Resposta: B**

---

**Q12.** Em qual situação um agente deve PAUSAR e solicitar confirmação humana antes de agir?

- A) Sempre que precisar ler um arquivo do sistema
- B) Quando a ação é irreversível, afeta sistemas compartilhados, ou tem alto blast radius
- C) Apenas quando o usuário explicitamente configurou "modo seguro"
- D) Quando o agente detecta que está próximo do limite de contexto

> **Resposta: B**

---

## Domínio 2 — Claude Code Config (Q13–Q24)

**Q13.** Onde o Claude Code armazena as configurações globais que se aplicam a todas as sessões do usuário?

- A) `./claude.json` na raiz de cada projeto
- B) `~/.claude/settings.json`
- C) `/etc/claude/config.toml`
- D) `CLAUDE.md` no diretório home do usuário

> **Resposta: B**

---

**Q14.** Qual é a função principal do arquivo `CLAUDE.md` em um projeto?

- A) Armazenar credenciais de API de forma segura e criptografada
- B) Definir instruções e contexto do projeto que serão carregados automaticamente em cada sessão
- C) Listar as ferramentas MCP disponíveis para o projeto
- D) Configurar variáveis de ambiente para execução de scripts

> **Resposta: B**

---

**Q15.** Qual mecanismo do Claude Code permite executar comandos automaticamente em resposta a eventos como início de sessão ou chamadas de ferramentas?

- A) Triggers
- B) Hooks
- C) Watchers
- D) Interceptors

> **Resposta: B**

---

**Q16.** Ao configurar um hook no Claude Code, qual é o comportamento padrão quando o hook retorna um código de saída diferente de zero?

- A) O Claude ignora o erro e continua normalmente
- B) A ação que disparou o hook é bloqueada e o erro é reportado
- C) O Claude reinicia a sessão automaticamente
- D) O hook é desabilitado permanentemente até reconfiguração manual

> **Resposta: B**

---

**Q17.** Qual flag do CLI do Claude Code permite iniciar uma sessão com um prompt inicial sem interação do usuário?

- A) `--auto`
- B) `--prompt`
- C) `-p` / `--print`
- D) `--batch`

> **Resposta: C**

---

**Q18.** O que são "slash commands" no Claude Code e como são criados pelo usuário?

- A) Comandos built-in do CLI que não podem ser customizados
- B) Atalhos configurados em `~/.claude/commands/` como arquivos markdown com prompts
- C) Scripts Python registrados via `claude register-command`
- D) Macros de teclado definidos em `keybindings.json`

> **Resposta: B**

---

**Q19.** Qual é a diferença entre `allowedTools` e `blockedTools` na configuração do Claude Code?

- A) São equivalentes — usar um torna o outro desnecessário
- B) `allowedTools` define uma lista de permissão explícita; `blockedTools` define exceções à permissão total
- C) `allowedTools` funciona apenas em modo headless; `blockedTools` funciona em modo interativo
- D) `blockedTools` só pode ser configurado globalmente, nunca por projeto

> **Resposta: B**

---

**Q20.** Como o Claude Code resolve conflitos quando há configurações definidas tanto em `~/.claude/settings.json` quanto em `.claude/settings.json` do projeto?

- A) As configurações globais sempre têm prioridade sobre as do projeto
- B) As configurações do projeto têm prioridade sobre as globais
- C) Claude solicita ao usuário que escolha qual configuração aplicar
- D) Ambas são mescladas e em caso de conflito a última carregada prevalece aleatoriamente

> **Resposta: B**

---

**Q21.** Para que serve o modo `--dangerously-skip-permissions` no Claude Code?

- A) Ignorar erros de sintaxe em arquivos de configuração
- B) Executar ações sem solicitar aprovação do usuário — usado em ambientes CI/CD controlados
- C) Contornar limites de rate da API Anthropic
- D) Desabilitar verificações de segurança de prompt injection

> **Resposta: B**

---

**Q22.** Qual é a finalidade do arquivo `.claude/settings.local.json`?

- A) Sobrepor configurações do projeto com ajustes locais que NÃO devem ser versionados no git
- B) Armazenar o histórico de sessões locais do projeto
- C) Configurar variáveis de ambiente específicas para testes locais
- D) Registrar métricas de uso de tokens por projeto

> **Resposta: A**

---

**Q23.** Como o Claude Code lida com segredos (API keys, senhas) nas configurações?

- A) Criptografa automaticamente qualquer valor que contenha a palavra "key" ou "secret"
- B) Recomenda usar variáveis de ambiente; nunca deve-se salvar valores sensíveis nos arquivos de config
- C) Armazena em keychain do SO automaticamente
- D) Aceita apenas referências a arquivos `.env` — nunca valores inline

> **Resposta: B**

---

**Q24.** Em qual arquivo e formato se configura um servidor MCP para uso no Claude Code?

- A) `~/.claude/mcp.json` em formato YAML
- B) `~/.claude/settings.json` sob a chave `mcpServers`, em formato JSON com `command` e `args`
- C) `.claude/tools.toml` com seção `[mcp]`
- D) `CLAUDE.md` em bloco de código com linguagem `mcp`

> **Resposta: B**

---

## Domínio 3 — Prompt Engineering (Q25–Q36)

**Q25.** Qual das seguintes técnicas é mais eficaz para guiar Claude em tarefas de raciocínio complexo antes de gerar a resposta final?

- A) Aumentar o `max_tokens` da requisição
- B) Usar chain-of-thought (CoT) — pedir ao modelo que "pense passo a passo" antes de responder
- C) Reduzir o system prompt para minimizar distrações
- D) Adicionar múltiplos exemplos de output no formato JSON

> **Resposta: B**

---

**Q26.** O que é "few-shot prompting" e quando é mais indicado?

- A) Fornecer ao modelo apenas uma instrução muito curta e direta
- B) Incluir exemplos de input/output no prompt para demonstrar o padrão esperado, especialmente em tarefas com formato específico
- C) Usar modelos menores para tarefas simples
- D) Limitar o número de tokens do output a poucas frases

> **Resposta: B**

---

**Q27.** Qual é o risco principal de um system prompt excessivamente longo e genérico?

- A) Aumenta a latência sem impacto na qualidade das respostas
- B) Pode diluir instruções importantes e causar comportamentos inconsistentes
- C) Excede o limite de tokens do modelo e causa erros de API
- D) Impede o uso de ferramentas externas durante a sessão

> **Resposta: B**

---

**Q28.** Em prompt engineering para Claude, qual abordagem é recomendada para especificar o formato de output?

- A) Confiar no modelo para escolher o melhor formato sem instruções
- B) Descrever explicitamente o formato desejado (JSON, markdown, lista, etc.) com um exemplo quando possível
- C) Usar apenas temperatura 0 para garantir outputs determinísticos
- D) Incluir o formato apenas no final do prompt do usuário, nunca no system prompt

> **Resposta: B**

---

**Q29.** O que é "prompt injection" e como mitigá-lo em aplicações com Claude?

- A) Injeção de código Python no contexto do modelo; mitigado com sandboxing
- B) Tentativa de conteúdo malicioso em dados externos manipular as instruções do modelo; mitigado tratando inputs externos como não confiáveis
- C) Excesso de tokens no prompt do sistema causando truncamento; mitigado com compressão
- D) Conflito entre o system prompt e o human turn; mitigado com delimitadores claros

> **Resposta: B**

---

**Q30.** Qual é a função de delimitadores XML (como `<context>`, `<instructions>`) em prompts para Claude?

- A) São obrigatórios para que Claude processe o prompt corretamente
- B) Ajudam a separar visualmente seções do prompt, reduzindo ambiguidade sobre o que é instrução vs. dado
- C) Ativam modos especiais de processamento interno do modelo
- D) São usados exclusivamente para tool use e não têm efeito em prompts de texto

> **Resposta: B**

---

**Q31.** Quando é indicado usar "negative prompting" (dizer ao modelo o que NÃO fazer)?

- A) Sempre — instruções negativas são sempre mais eficazes que positivas
- B) Nunca — Claude não processa instruções negativas corretamente
- C) Como complemento a instruções positivas quando há comportamentos específicos a evitar, mas não como substituto
- D) Apenas em tarefas criativas, não em tarefas técnicas

> **Resposta: C**

---

**Q32.** Qual técnica de prompt é mais indicada para tarefas que requerem Claude a seguir um processo de múltiplos passos com checagem de cada etapa?

- A) Zero-shot prompting com output estruturado
- B) Scratchpad / extended thinking — permitir que o modelo raciocine internamente antes do output final
- C) Reduzir o número de instruções para evitar sobrecarga cognitiva
- D) Usar apenas perguntas abertas sem exemplos

> **Resposta: B**

---

**Q33.** Em Claude Code, qual é o impacto de incluir um `CLAUDE.md` bem estruturado no projeto?

- A) Apenas estético — não afeta o comportamento do modelo
- B) Fornece contexto persistente sobre convenções, arquitetura e preferências, melhorando consistência entre sessões
- C) Substitui completamente a necessidade de prompts no human turn
- D) Funciona apenas na primeira sessão; sessões subsequentes ignoram o arquivo

> **Resposta: B**

---

**Q34.** O que é "context stuffing" e por que deve ser evitado?

- A) Técnica de comprimir múltiplos prompts em um; evitado por causar rate limits
- B) Preencher o contexto com informações irrelevantes ou excessivas, degradando a qualidade das respostas e desperdiçando tokens
- C) Reusar o mesmo context window para múltiplos usuários; evitado por privacidade
- D) Usar o mesmo system prompt em todos os projetos; evitado por falta de especificidade

> **Resposta: B**

---

**Q35.** Como Claude deve ser instruído para lidar com incerteza em suas respostas?

- A) Sempre responder com confiança total para não confundir o usuário
- B) Ser explicitamente instruído a indicar quando não tem certeza, usar hedge language e sugerir verificação
- C) Recusar responder quando não tiver 100% de certeza
- D) Gerar múltiplas versões da resposta e deixar o usuário decidir

> **Resposta: B**

---

**Q36.** Qual é a melhor prática para prompts de sistema em aplicações de produção?

- A) Manter o system prompt secreto para segurança, sem documentação
- B) Ser específico, testar variações, versionar o prompt junto ao código e documentar o comportamento esperado
- C) Usar o mesmo system prompt genérico em todas as aplicações para manter consistência
- D) Evitar qualquer instrução sobre formato para dar liberdade ao modelo

> **Resposta: B**

---

## Domínio 4 — Tool Design & MCP (Q37–Q48)

**Q37.** O que é o Model Context Protocol (MCP) no ecossistema Claude?

- A) Um protocolo de criptografia para proteger dados enviados à API Anthropic
- B) Um padrão aberto que permite que modelos de linguagem se conectem a ferramentas e fontes de dados externas
- C) Um formato de compressão para reduzir o tamanho dos prompts enviados ao modelo
- D) Um sistema de autenticação para acesso multi-usuário ao Claude Code

> **Resposta: B**

---

**Q38.** Qual é a diferença entre um servidor MCP `stdio` e `http` (SSE)?

- A) `stdio` é mais seguro; `http` tem melhor performance em todos os casos
- B) `stdio` se comunica via entrada/saída padrão (processo local); `http` usa Server-Sent Events para comunicação via rede
- C) `stdio` suporta apenas ferramentas de leitura; `http` suporta ferramentas de escrita
- D) São equivalentes — a diferença é apenas de nomenclatura

> **Resposta: B**

---

**Q39.** Ao projetar uma ferramenta (tool) para Claude, qual é a prática mais importante na descrição da ferramenta?

- A) Minimizar a descrição para economizar tokens no contexto
- B) Ser claro e específico sobre o que a ferramenta faz, seus parâmetros e quando deve ser usada
- C) Listar todos os possíveis casos de erro na descrição
- D) Usar nomes de ferramentas genéricos para facilitar reuso entre projetos

> **Resposta: B**

---

**Q40.** O que acontece quando Claude chama uma ferramenta que retorna um erro?

- A) A sessão é encerrada automaticamente e o usuário deve reiniciar
- B) Claude recebe o resultado de erro como tool result e pode raciocinar sobre ele para tentar alternativas ou escalar
- C) O erro é silenciado e Claude tenta a próxima ferramenta da lista
- D) Claude repete a chamada exatamente igual até 3 vezes antes de parar

> **Resposta: B**

---

**Q41.** Qual é o formato correto de um tool result retornado ao modelo após execução de uma ferramenta?

- A) Um objeto JSON com campos `success` e `data` obrigatórios
- B) Uma mensagem com `role: tool` contendo o `tool_use_id` e o conteúdo do resultado
- C) Uma string simples sem estrutura específica
- D) Um objeto com campos `status_code` e `body` no padrão HTTP

> **Resposta: B**

---

**Q42.** Em qual situação é recomendado criar múltiplas ferramentas pequenas e especializadas em vez de uma ferramenta grande e genérica?

- A) Quando há restrições de memória no servidor MCP
- B) Quando diferentes operações têm semânticas distintas — ferramentas granulares permitem ao modelo escolher com precisão
- C) Apenas quando o número total de ferramentas for menor que 5
- D) Quando as ferramentas são usadas exclusivamente em modo batch

> **Resposta: B**

---

**Q43.** O que é um "resource" no contexto do MCP, diferentemente de uma "tool"?

- A) Resources são ferramentas que consomem mais tokens; tools são mais eficientes
- B) Resources expõem dados/conteúdo para leitura pelo modelo; tools executam ações com efeitos colaterais
- C) Resources são síncronos; tools são assíncronos
- D) Resources são definidos em JSON Schema; tools são definidos em YAML

> **Resposta: B**

---

**Q44.** Como garantir idempotência em ferramentas que modificam estado (escrita, deleção)?

- A) Desabilitar essas ferramentas em produção
- B) Projetar as ferramentas para que chamadas repetidas com os mesmos parâmetros produzam o mesmo resultado final sem efeitos colaterais duplicados
- C) Adicionar um parâmetro `confirm: boolean` obrigatório em todas as ferramentas de escrita
- D) Usar apenas ferramentas de leitura e delegar escrita ao usuário

> **Resposta: B**

---

**Q45.** Qual é a melhor prática para tratar parâmetros opcionais em definições de ferramentas?

- A) Tornar todos os parâmetros obrigatórios para evitar ambiguidade
- B) Documentar claramente o comportamento padrão de cada parâmetro opcional e usar valores sensatos como default
- C) Remover parâmetros opcionais e criar versões separadas da ferramenta para cada variação
- D) Usar apenas parâmetros do tipo string para simplicidade

> **Resposta: B**

---

**Q46.** Qual é o risco de uma ferramenta com efeitos colaterais irreversíveis chamada por um agente autônomo?

- A) Nenhum risco — agentes autônomos têm salvaguardas automáticas
- B) O agente pode executar a ação sem confirmação humana, causando impacto permanente
- C) A ferramenta automaticamente solicita confirmação via MCP antes de executar
- D) O modelo sempre avisa o usuário antes de chamar qualquer ferramenta destrutiva

> **Resposta: B**

---

**Q47.** Como o Claude Code trata ferramentas que demoram mais do que o esperado para retornar?

- A) Cancela automaticamente após 30 segundos
- B) Aguarda o resultado e usa o output; timeouts devem ser gerenciados pela implementação da ferramenta
- C) Retenta a chamada com parâmetros modificados
- D) Ignora o resultado e continua o pipeline

> **Resposta: B**

---

**Q48.** Qual dos seguintes é um exemplo de boa nomenclatura para uma ferramenta MCP?

- A) `tool1`, `tool2`, `tool3`
- B) `do_stuff`
- C) `search_web`, `read_file`, `create_github_issue`
- D) `executeOperation`, `runProcess`

> **Resposta: C**

---

## Domínio 5 — Context & Reliability (Q49–Q60)

**Q49.** O que é "context window" e qual sua implicação para aplicações com Claude?

- A) A janela gráfica da interface do Claude Code
- B) O limite de tokens que o modelo pode processar em uma única requisição, incluindo input e output
- C) O número máximo de sessões simultâneas permitidas por conta
- D) O tempo máximo de inatividade antes de uma sessão expirar

> **Resposta: B**

---

**Q50.** Qual técnica é mais eficaz para lidar com documentos muito longos que excedem a janela de contexto?

- A) Truncar o documento no limite de tokens sem aviso
- B) Usar retrieval (RAG) para selecionar apenas as partes relevantes do documento
- C) Dividir o documento em partes iguais e processar cada uma em sessões separadas sem relação entre elas
- D) Aumentar o `max_tokens` da requisição até o documento caber

> **Resposta: B**

---

**Q51.** O que é "prompt caching" na API Anthropic e qual seu principal benefício?

- A) Armazenar respostas do modelo para reuso em perguntas idênticas
- B) Reutilizar prefixos de prompt que não mudam entre requisições, reduzindo latência e custo
- C) Salvar o histórico de prompts localmente para auditoria
- D) Comprimir o prompt antes de enviar para a API

> **Resposta: B**

---

**Q52.** Como o Claude Code gerencia o contexto quando a conversa se aproxima do limite da janela?

- A) Encerra a sessão e exige que o usuário reinicie do zero
- B) Comprime automaticamente mensagens anteriores, mantendo o contexto mais recente e relevante
- C) Solicita ao usuário que resuma manualmente a conversa
- D) Remove aleatoriamente mensagens para liberar espaço

> **Resposta: B**

---

**Q53.** Qual é a melhor estratégia para garantir consistência em pipelines agênticos longos que podem durar muitas etapas?

- A) Usar apenas um único agente sem subagentes para evitar inconsistências
- B) Salvar checkpoints do estado em memória externa e referenciar ao longo do pipeline
- C) Reiniciar o contexto a cada 10 etapas para evitar degradação
- D) Aumentar o temperature para que o modelo explore mais alternativas

> **Resposta: B**

---

**Q54.** O que é "grounding" no contexto de confiabilidade de respostas de LLMs?

- A) Conectar o modelo à internet para respostas em tempo real
- B) Ancorar as respostas do modelo em fatos verificáveis e fontes concretas, reduzindo alucinações
- C) Configurar o modelo para responder apenas dentro de domínios pré-definidos
- D) Usar fine-tuning para especializar o modelo em um domínio específico

> **Resposta: B**

---

**Q55.** Qual é o impacto de `temperature: 0` na confiabilidade das respostas do Claude?

- A) Torna as respostas mais criativas e exploratórias
- B) Maximiza o determinismo, gerando respostas mais consistentes e reproduzíveis — ideal para tarefas que exigem precisão
- C) Desabilita o uso de ferramentas pelo modelo
- D) Reduz o número de tokens consumidos por resposta

> **Resposta: B**

---

**Q56.** Em sistemas de produção com Claude, como monitorar e detectar respostas de baixa qualidade?

- A) Confiar exclusivamente na avaliação subjetiva do usuário final
- B) Implementar verificações automatizadas (validação de schema, testes de regressão de prompt, avaliadores LLM-as-judge)
- C) Aumentar o `top_p` para reduzir a probabilidade de respostas incorretas
- D) Limitar o output a formatos binários (sim/não) para facilitar validação

> **Resposta: B**

---

**Q57.** Qual abordagem melhora a rastreabilidade em pipelines com múltiplos agentes?

- A) Usar apenas um agente para centralizar todos os logs
- B) Implementar IDs de correlação, logging estruturado por etapa e rastreamento de tool calls
- C) Desabilitar logging para reduzir overhead de performance
- D) Salvar apenas o output final de cada agente, descartando logs intermediários

> **Resposta: B**

---

**Q58.** O que é "token budget" e como deve ser gerenciado em aplicações de produção?

- A) O número de caracteres máximo por mensagem — gerenciado via truncamento automático
- B) O limite de tokens disponíveis por requisição ou sessão — deve ser monitorado e o consumo otimizado via prompt engineering e seleção de modelo
- C) Um crédito renovável mensalmente que não precisa de gestão ativa
- D) Um parâmetro de API que controla a velocidade de geração de tokens

> **Resposta: B**

---

**Q59.** Qual é a principal diferença de confiabilidade entre usar Claude em modo "interactive" vs. modo "headless"?

- A) Modo headless é mais lento devido ao overhead de logging automático
- B) Modo interativo permite que o usuário corrija erros em tempo real; modo headless requer salvaguardas robustas pois não há supervisão humana no loop
- C) Modo headless usa um modelo diferente e mais conservador
- D) Não há diferença de confiabilidade — apenas de interface

> **Resposta: B**

---

**Q60.** Qual das seguintes práticas é MAIS importante para garantir a segurança em aplicações Claude em produção?

- A) Nunca usar ferramentas com efeitos colaterais
- B) Implementar o princípio do menor privilégio: conceder ao agente apenas as permissões estritamente necessárias para sua função
- C) Usar apenas modelos Haiku por serem mais conservadores
- D) Desabilitar o system prompt para evitar conflitos com os prompts do usuário

> **Resposta: B**

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

*Simulado criado para estudo — não é material oficial da Anthropic.*
