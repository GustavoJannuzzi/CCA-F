---
titulo: "Simulado 2 — Claude Architect Certification: Claude Code Foundations"
data_criacao: 2026-04-09
data_atualizacao: 2026-04-09
tema: "Estudo"
cliente: "Interno"
status: "ativo"
tags: [simulado, certificacao, claude-code, anthropic, estudo, documentacao-oficial]
---

# Simulado 2 — Claude Architect Certification: Claude Code Foundations

**60 questões | Baseado na documentação oficial | Resposta correta indicada após cada questão**

---

## Domínio 1 — Agentic Architecture (Q01–Q12)

**Q01.** Quando Claude chama uma client tool (ferramenta definida pelo desenvolvedor), qual é o valor de `stop_reason` retornado na resposta da API?

- A) `"end_turn"`
- B) `"tool_use"`
- C) `"max_tokens"`
- D) `"tool_call"`

> **Resposta: B** — A API retorna `stop_reason: "tool_use"` quando Claude quer invocar uma client tool. Sua aplicação executa a ferramenta e retorna o resultado via `tool_result`.

---

**Q02.** Qual é a diferença fundamental entre "client tools" e "server tools" na arquitetura de tool use do Claude?

- A) Client tools são mais rápidas; server tools são mais seguras
- B) Client tools são executadas na aplicação do desenvolvedor; server tools (como web_search) são executadas na infraestrutura da Anthropic
- C) Client tools requerem autenticação OAuth; server tools são públicas
- D) Client tools funcionam offline; server tools requerem conexão com a internet

> **Resposta: B** — Client tools: Claude retorna `tool_use` block → sua aplicação executa → envia `tool_result`. Server tools (ex: `web_search_20260209`): a Anthropic executa internamente, você recebe os resultados diretamente.

---

**Q03.** De acordo com a documentação oficial, qual é o comportamento esperado de Claude Opus vs. Claude Sonnet quando um parâmetro obrigatório de uma ferramenta está ausente no prompt do usuário?

- A) Ambos sempre perguntam ao usuário antes de chamar a ferramenta
- B) Ambos inferem um valor padrão sem avisar o usuário
- C) Claude Opus é muito mais propenso a pedir o parâmetro ausente; Claude Sonnet pode tentar inferir um valor razoável
- D) Claude Opus ignora a ferramenta; Claude Sonnet usa um valor vazio

> **Resposta: C** — A documentação afirma: "Claude Opus is much more likely to recognize that a parameter is missing and ask for it. Claude Sonnet may ask... but may also do its best to infer a reasonable value."

---

**Q04.** O que o Agent SDK do Claude Code permite que não é possível apenas com sub-agentes nativos?

- A) Executar tarefas em paralelo
- B) Construir agentes customizados com controle total sobre orquestração, acesso a ferramentas e permissões, usando as capacidades do Claude Code
- C) Conectar a servidores MCP externos
- D) Usar modelos diferentes para cada etapa do pipeline

> **Resposta: B** — O Agent SDK oferece controle programático completo sobre a lógica do agente, diferente dos sub-agentes que são coordenados diretamente pelo Claude Code.

---

**Q05.** Em qual plataforma do Claude Code as tarefas agendadas continuam rodando mesmo quando o computador do usuário está desligado?

- A) Desktop scheduled tasks
- B) Cloud scheduled tasks (tarefas agendadas na nuvem)
- C) Terminal /loop tasks
- D) VS Code background tasks

> **Resposta: B** — Cloud scheduled tasks rodam na infraestrutura da Anthropic, independentemente do estado do computador do usuário. Desktop tasks rodam na máquina local.

---

**Q06.** Qual é o fluxo correto do loop agêntico quando Claude invoca uma client tool?

- A) Claude envia tool_use → aguarda resposta → gera output final
- B) Claude envia stop_reason: tool_use com tool_use block → aplicação executa → aplicação envia tool_result → Claude continua
- C) Claude executa a ferramenta internamente e inclui o resultado no output
- D) A aplicação envia o tool_result antes de Claude fazer a chamada

> **Resposta: B** — O loop: (1) Claude responde com `stop_reason: "tool_use"` e um ou mais `tool_use` blocks. (2) Sua aplicação executa a ferramenta. (3) Você envia de volta uma mensagem com `tool_result`. (4) Claude continua a resposta.

---

**Q07.** O que faz o comando `claude --teleport` no Claude Code?

- A) Transfere arquivos locais para a nuvem Anthropic
- B) Puxa para o terminal uma sessão que foi iniciada na web ou no app iOS
- C) Conecta Claude Code a um servidor remoto via SSH
- D) Migra configurações entre diferentes máquinas

> **Resposta: B** — `--teleport` permite continuar no terminal uma sessão iniciada na web ou no aplicativo iOS do Claude.

---

**Q08.** O que é "Dispatch" no contexto do Claude Code Desktop?

- A) Um sistema de fila para processar múltiplas tasks em sequência
- B) Um mecanismo que permite enviar uma tarefa do celular e abrir a sessão resultante no Desktop
- C) Um orquestrador de sub-agentes integrado ao VS Code
- D) Um sistema de notificações para alertas de conclusão de tasks

> **Resposta: B** — Dispatch: você envia a tarefa pelo celular e o Desktop app cria e abre a sessão localmente.

---

**Q09.** Qual é o caso de uso documentado da integração do Claude Code com Slack?

- A) Sincronizar o CLAUDE.md automaticamente com canais do Slack
- B) Monitorar canais em tempo real e criar alertas de código
- C) Mencionar @Claude com um bug report e receber um pull request como resposta
- D) Compartilhar sessões do Claude Code com a equipe via Slack

> **Resposta: C** — Documentação: "Route bug reports from Slack to pull requests... mention @Claude in Slack with a bug report and get a pull request back."

---

**Q10.** Qual surface do Claude Code suporta integrações com third-party providers (provedores de terceiros)?

- A) Apenas o Desktop app
- B) Terminal CLI e VS Code
- C) Apenas o Web app
- D) Todos os surfaces igualmente

> **Resposta: B** — A documentação especifica: "The Terminal CLI and VS Code also support third-party providers."

---

**Q11.** Quais funcionalidades específicas a extensão de VS Code do Claude Code oferece que não estão no terminal?

- A) Acesso a MCP servers e hooks
- B) Inline diffs, @-mentions, plan review e conversation history diretamente no editor
- C) Suporte a múltiplos modelos Claude simultaneamente
- D) Execução de testes automatizados integrada

> **Resposta: B** — Documentação VS Code: "inline diffs, @-mentions, plan review, and conversation history directly in your editor."

---

**Q12.** Em um pipeline multi-agente, qual é a abordagem correta para um agente orquestrador lidar com a falha de um subagente?

- A) Encerrar todo o pipeline imediatamente e reportar ao usuário
- B) Ignorar a falha e prosseguir com os demais subagentes
- C) Repetir a chamada ao subagente com os mesmos parâmetros infinitamente
- D) Diagnosticar a causa da falha, tentar alternativas viáveis e escalar ao usuário apenas se não houver solução

> **Resposta: D** — O orquestrador deve raciocinar sobre o erro, tentar abordagens alternativas e só escalar ao usuário quando esgotadas as opções automáticas.

---

## Domínio 2 — Claude Code Config (Q13–Q24)

**Q13.** Com que frequência o arquivo `CLAUDE.md` é carregado pelo Claude Code?

- A) Uma vez, na primeira sessão do projeto
- B) No início de cada sessão
- C) Apenas quando explicitamente referenciado com `@CLAUDE.md`
- D) A cada chamada de ferramenta

> **Resposta: B** — Documentação: "CLAUDE.md is a markdown file you add to your project root that Claude Code reads at the start of every session."

---

**Q14.** O que é "auto memory" no Claude Code e como ele é construído?

- A) Um arquivo de memória que o usuário atualiza manualmente após cada sessão
- B) Memória que Claude constrói automaticamente enquanto trabalha, salvando aprendizados como comandos de build e insights de debugging
- C) Um sistema de cache de respostas que evita chamadas repetidas à API
- D) Um backup automático do histórico de conversas no disco local

> **Resposta: B** — Documentação: "Claude also builds auto memory as it works, saving learnings like build commands and debugging insights across sessions without you writing anything."

---

**Q15.** Para qual caso de uso os hooks do Claude Code são especificamente exemplificados na documentação oficial?

- A) Enviar notificações ao usuário quando uma task é concluída
- B) Auto-formatar após cada edição de arquivo ou rodar lint antes de um commit
- C) Validar o schema de ferramentas MCP antes de registrá-las
- D) Fazer backup automático do CLAUDE.md antes de cada sessão

> **Resposta: B** — Documentação: "Hooks let you run shell commands before or after Claude Code actions, like auto-formatting after every file edit or running lint before a commit."

---

**Q16.** Qual é o propósito do comando `/schedule` no Claude Code?

- A) Agendar reuniões no Google Calendar via MCP
- B) Criar tarefas agendadas recorrentes para automatizar trabalho repetitivo
- C) Programar o encerramento automático de uma sessão longa
- D) Definir prioridades de execução entre múltiplos agentes

> **Resposta: B** — `/schedule` cria scheduled tasks (cloud ou desktop) para automatizar trabalho recorrente como PR reviews matinais ou análises de CI.

---

**Q17.** Qual é a sintaxe correta para usar Claude Code de forma não-interativa em um script de CI/CD?

- A) `claude --batch "analise este log"`
- B) `claude --silent "analise este log"`
- C) `claude -p "analise este log"` ou `claude --print "analise este log"`
- D) `echo "analise este log" | claude --pipe`

> **Resposta: C** — A flag `-p` / `--print` executa Claude de forma não-interativa, imprime o resultado e encerra. Ideal para pipelines.

---

**Q18.** Qual chave no arquivo `settings.json` do Claude Code é usada para adicionar a definição de um servidor MCP?

- A) `"tools"`
- B) `"mcpServers"`
- C) `"integrations"`
- D) `"plugins"`

> **Resposta: B** — A configuração de MCP servers fica sob a chave `mcpServers` no `~/.claude/settings.json`, com `command` e `args` para cada servidor.

---

**Q19.** O arquivo `.claude/settings.local.json` tem qual característica importante em relação ao controle de versão?

- A) É automaticamente criptografado pelo Claude Code antes de ser commitado
- B) Deve ser adicionado ao `.gitignore` pois contém overrides locais que não devem ser versionados
- C) É somente leitura e não pode ser editado diretamente
- D) É sincronizado automaticamente com as configurações globais do usuário

> **Resposta: B** — `settings.local.json` é para ajustes pessoais/locais do desenvolvedor que não devem ir para o repositório.

---

**Q20.** Ao adicionar `strict: true` na definição de uma ferramenta, qual garantia isso oferece?

- A) A ferramenta só pode ser chamada com confirmação explícita do usuário
- B) As chamadas de ferramenta feitas por Claude sempre corresponderão exatamente ao schema definido
- C) A ferramenta executa em modo sandbox sem acesso à rede
- D) O resultado da ferramenta é validado antes de ser retornado ao modelo

> **Resposta: B** — Documentação: "Add `strict: true` to your tool definitions to ensure Claude's tool calls always match your schema exactly."

---

**Q21.** Quais surfaces do Claude Code compartilham os mesmos arquivos CLAUDE.md, configurações e servidores MCP?

- A) Apenas Terminal e VS Code
- B) Todos os surfaces (Terminal, VS Code, JetBrains, Desktop, Web) conectam ao mesmo engine
- C) Apenas surfaces locais (Terminal, VS Code, Desktop); Web usa configurações separadas
- D) Cada surface mantém suas próprias configurações independentes

> **Resposta: B** — Documentação: "Each surface connects to the same underlying Claude Code engine, so your CLAUDE.md files, settings, and MCP servers work across all of them."

---

**Q22.** Como o Claude Code pode ser integrado a pipelines de CI/CD para automação de code review?

- A) Via webhook direto na API Anthropic sem configuração adicional
- B) Através de integrações com GitHub Actions ou GitLab CI/CD
- C) Apenas via scripts bash que invocam `claude --batch`
- D) Somente através de ferramentas MCP customizadas

> **Resposta: B** — Documentação: "In CI, you can automate code review and issue triage with GitHub Actions or GitLab CI/CD."

---

**Q23.** Qual é o impacto de incluir a definição de ferramentas (`tools` parameter) em uma requisição à API Anthropic em termos de tokens?

- A) Nenhum impacto — tools são processados separadamente e não contam como tokens
- B) Adiciona tokens do sistema automaticamente (ex: 346 tokens para `auto/none` no Opus 4.6) mais os tokens das definições de ferramentas
- C) Dobra o custo da requisição independente do número de ferramentas
- D) Impacta apenas o output, não o input

> **Resposta: B** — A documentação detalha tokens adicionais de system prompt por model/tool_choice: ex. Claude Opus 4.6 com `auto/none` adiciona 346 tokens de system prompt, além dos tokens das próprias definições.

---

**Q24.** Qual é a funcionalidade do `/loop` no Claude Code?

- A) Criar um loop de sub-agentes para tarefas paralelas
- B) Repetir um prompt em intervalos definidos dentro de uma sessão CLI para polling rápido
- C) Reiniciar a sessão periodicamente para evitar degradação de contexto
- D) Criar um ciclo de feedback entre dois agentes

> **Resposta: B** — `/loop` repete um prompt em intervalos (ex: `/loop 5m /foo`) dentro de uma sessão CLI, útil para polling rápido.

---

## Domínio 3 — Prompt Engineering (Q25–Q36)

**Q25.** De acordo com as boas práticas da Anthropic, qual é a função principal das tags XML em prompts para Claude?

- A) São obrigatórias para que Claude processe qualquer input estruturado
- B) Separar claramente diferentes seções do prompt (instruções, contexto, exemplos, dados), reduzindo ambiguidade
- C) Ativar modos internos especiais de processamento do modelo
- D) Substituir o uso de few-shot examples em prompts avançados

> **Resposta: B** — Tags XML como `<context>`, `<instructions>`, `<example>` são uma best practice para estruturar prompts, não um requisito. Ajudam Claude a distinguir instrução de dado.

---

**Q26.** Em qual tipo de tarefa o "role prompting" (pedir a Claude para assumir um papel específico) é mais eficaz?

- A) Tarefas onde qualquer resposta serve — para dar liberdade criativa ao modelo
- B) Tarefas onde um domínio de conhecimento específico ou estilo de comunicação é necessário (ex: "você é um engenheiro de segurança sênior")
- C) Apenas em tarefas criativas como escrita e arte; prejudica tarefas técnicas
- D) Exclusivamente no system prompt — nunca no human turn

> **Resposta: B** — Role prompting ajuda Claude a adotar o nível de expertise, vocabulário e perspectiva corretos para a tarefa.

---

**Q27.** O que é "prompt chaining" e quando é recomendado?

- A) Encadear múltiplos modelos em sequência para aumentar a qualidade
- B) Dividir uma tarefa complexa em etapas sequenciais onde o output de cada prompt alimenta o próximo
- C) Combinar o system prompt com o human turn em uma única mensagem
- D) Usar o mesmo prompt em múltiplos modelos e comparar as respostas

> **Resposta: B** — Prompt chaining é recomendado para tarefas complexas que se beneficiam de verificações intermediárias e onde cada etapa tem critérios de sucesso claros.

---

**Q28.** Qual é a diferença prática entre zero-shot e few-shot prompting para tarefas de extração de dados?

- A) Zero-shot é sempre inferior — deve-se sempre usar few-shot
- B) Zero-shot confia nas instruções textuais; few-shot usa exemplos concretos de input/output para demonstrar o formato exato esperado
- C) Zero-shot usa temperatura 0; few-shot usa temperatura mais alta para criatividade
- D) A diferença é apenas semântica — o modelo processa ambos da mesma forma

> **Resposta: B** — Para extração de dados com formato específico (JSON, CSV, etc.), few-shot com exemplos concretos é significativamente mais eficaz que zero-shot.

---

**Q29.** Qual é o benefício do "extended thinking" (pensamento estendido) no Claude e em que tipo de tarefa ele é mais indicado?

- A) Aumenta a velocidade de resposta em tarefas simples
- B) Permite que Claude raciocine internamente antes do output final — ideal para problemas de múltiplos passos, matemática, lógica e decisões complexas
- C) Reduz o uso de tokens ao consolidar raciocínio intermediário
- D) Garante que Claude sempre peça confirmação do usuário antes de agir

> **Resposta: B** — Extended thinking (scratchpad interno) melhora significativamente performance em tarefas que requerem raciocínio profundo multi-etapas.

---

**Q30.** De acordo com as best practices da Anthropic, como deve ser a estrutura de um system prompt para uma aplicação de produção?

- A) Genérico e reutilizável para minimizar manutenção
- B) Específico para o caso de uso, testado empiricamente contra critérios de sucesso, versionado junto ao código
- C) O mais curto possível para economizar tokens
- D) Idêntico ao prompt usado em desenvolvimento para garantir consistência

> **Resposta: B** — A documentação enfatiza: testar contra critérios de sucesso definidos, versionar o prompt como código, e ser específico sobre comportamento esperado.

---

**Q31.** Ao construir avaliações (evals) para um sistema com Claude, qual é a abordagem recomendada como ponto de partida antes de prompt engineering?

- A) Começar com prompt engineering e criar evals depois para validar
- B) Primeiro definir critérios de sucesso claros e formas de medir empiricamente — depois otimizar o prompt
- C) Usar o prompt generator da Console e aceitar o resultado sem modificações
- D) Testar com usuários reais em produção antes de qualquer eval estruturado

> **Resposta: B** — Documentação: "This guide assumes that you have: (1) A clear definition of the success criteria for your use case, (2) Some ways to empirically test against those criteria."

---

**Q32.** Como a técnica de "grounding" melhora a confiabilidade de um sistema RAG com Claude?

- A) Aumentando a temperatura para gerar mais alternativas de resposta
- B) Fornecendo ao modelo documentos ou dados relevantes como contexto, ancorando as respostas em fatos verificáveis e reduzindo alucinações
- C) Usando sempre o modelo mais capaz disponível independente do custo
- D) Desabilitando o histórico de conversa para evitar contaminação

> **Resposta: B** — Grounding em RAG: recuperar documentos relevantes e fornecê-los como contexto faz Claude basear as respostas em fontes verificáveis, não em conhecimento paramétrico que pode estar desatualizado.

---

**Q33.** Por que a documentação da Anthropic recomenda avaliar latência e custo separadamente do prompt engineering?

- A) Porque latência e custo são fixos e não podem ser otimizados
- B) Porque latência e custo são frequentemente mais impactados pela escolha do modelo do que pelo prompt, e misturar essas dimensões confunde a otimização
- C) Porque prompt engineering sempre aumenta custo e latência
- D) Porque são responsabilidade da equipe de infraestrutura, não do engenheiro de prompts

> **Resposta: B** — Documentação: "Not every success criteria or failing eval is best solved by prompt engineering. For example, latency and cost can be sometimes more easily improved by selecting a different model."

---

**Q34.** Ao usar few-shot examples em prompts, onde é mais indicado posicioná-los?

- A) Sempre no final do human turn, após a pergunta principal
- B) No system prompt quando os exemplos são fixos e reutilizáveis; no human turn quando são dinâmicos ou específicos da tarefa
- C) Apenas no human turn — exemplos no system prompt são ignorados pelo modelo
- D) Em um arquivo separado referenciado via `@examples.txt`

> **Resposta: B** — Exemplos fixos de formato/comportamento pertencem ao system prompt (podem ser cacheados). Exemplos dinâmicos e específicos da tarefa vão no human turn.

---

**Q35.** Qual é o efeito de usar `top_p: 1` e `temperature: 0` simultaneamente em uma requisição ao Claude?

- A) Causa um erro de configuração conflitante na API
- B) Maximiza o determinismo: `temperature: 0` é o controle principal; `top_p: 1` garante que todo o vocabulário está disponível, mas a temperatura baixa domina a seleção
- C) Produz outputs mais criativos pois os parâmetros se cancelam
- D) Ativa um modo de resposta especial de alta precisão

> **Resposta: B** — Com `temperature: 0`, o modelo escolhe sempre o token de maior probabilidade. `top_p: 1` mantém o vocabulário completo, mas não compete com o efeito dominante da temperatura.

---

**Q36.** Qual ferramenta oficial da Anthropic está disponível na Claude Console para ajudar a criar prompts iniciais sem escrever do zero?

- A) Prompt Debugger
- B) Prompt Generator
- C) Prompt Linter
- D) Prompt Optimizer

> **Resposta: B** — Documentação: "Don't have a first draft prompt? Try the prompt generator in the Claude Console!" A Console também oferece prompt improver e templates.

---

## Domínio 4 — Tool Design & MCP (Q37–Q48)

**Q37.** Na arquitetura MCP, qual é a distinção correta entre "MCP Host", "MCP Client" e "MCP Server"?

- A) Host = servidor remoto; Client = aplicação local; Server = ferramenta
- B) Host = a aplicação AI (ex: Claude Code) que gerencia conexões; Client = componente que mantém conexão com um server; Server = programa que fornece contexto/ferramentas
- C) Host e Client são intercambiáveis; Server é sempre remoto
- D) Host = usuário final; Client = modelo Claude; Server = API Anthropic

> **Resposta: B** — MCP Architecture: Host (ex: Claude Code, VS Code) cria um MCP Client por Server. Cada Client mantém uma conexão dedicada com seu MCP Server correspondente.

---

**Q38.** Qual é a diferença entre o transporte `stdio` e o transporte `Streamable HTTP` no MCP, segundo a documentação oficial?

- A) stdio é mais novo e recomendado; Streamable HTTP é legado
- B) stdio usa streams de entrada/saída padrão para comunicação entre processos locais; Streamable HTTP usa HTTP POST + SSE opcional, suporta servidores remotos e múltiplos clientes simultâneos
- C) stdio é para Windows; Streamable HTTP é para Linux/Mac
- D) stdio suporta apenas tools; Streamable HTTP suporta tools, resources e prompts

> **Resposta: B** — Documentação MCP: "Stdio transport: Uses standard input/output streams for direct process communication between local processes... Streamable HTTP transport: Uses HTTP POST for client-to-server messages with optional SSE for streaming."

---

**Q39.** Qual protocolo de mensagens o MCP usa como base para comunicação entre client e server?

- A) GraphQL
- B) gRPC
- C) JSON-RPC 2.0
- D) WebSocket com protocolo proprietário

> **Resposta: C** — Documentação: "MCP uses JSON-RPC 2.0 as its underlying RPC protocol. Client and servers send requests to each other and respond accordingly."

---

**Q40.** O que acontece durante a fase de "capability negotiation" no ciclo de vida de uma conexão MCP?

- A) O server envia uma lista de todas as ferramentas disponíveis para o client catalogar
- B) Client e server trocam mensagens `initialize`/response para declarar quais features (tools, resources, prompts, notifications) cada lado suporta
- C) O host autentica o server via OAuth antes de estabelecer a conexão
- D) O client faz uma requisição de teste para verificar a latência do server

> **Resposta: B** — O `initialize` request/response contém o campo `capabilities` que declara o que cada lado suporta. Se não houver versão compatível, a conexão deve ser encerrada.

---

**Q41.** Quais são as três primitivas de servidor definidas pelo MCP?

- A) Actions, Events, Callbacks
- B) Tools, Resources, Prompts
- C) Functions, Schemas, Templates
- D) Endpoints, Handlers, Middlewares

> **Resposta: B** — Documentação: "MCP defines three core primitives that servers can expose: Tools (executable functions), Resources (data sources), Prompts (reusable templates)."

---

**Q42.** Qual é a finalidade da primitiva "Sampling" no MCP e quem a expõe?

- A) É exposta pelo server para amostrar dados de um banco de dados
- B) É exposta pelo client, permitindo que MCP servers solicitem completions do modelo de linguagem da aplicação host sem depender de um SDK de modelo específico
- C) É exposta pelo server para retornar amostras de dados de treinamento
- D) É uma feature experimental que nenhum client atual suporta

> **Resposta: B** — Documentação: "Sampling: Allows servers to request language model completions from the client's AI application. Useful when server authors want access to a language model but want to stay model-independent."

---

**Q43.** Qual é a estrutura de uma notificação MCP (ex: `notifications/tools/list_changed`) e por que ela não tem campo `id`?

- A) Notificações sempre têm `id` — a ausência é um bug de implementação
- B) Notificações seguem a semântica JSON-RPC 2.0 onde a ausência de `id` indica que nenhuma resposta é esperada
- C) O `id` é opcional e sua ausência apenas reduz o overhead de rede
- D) Notificações usam um campo `notification_id` diferente do `id` padrão

> **Resposta: B** — Documentação: "Notifications are sent as JSON-RPC 2.0 notification messages (without expecting a response)." A ausência de `id` é intencional: sem `id` = sem resposta esperada.

---

**Q44.** Quando um MCP server declara `"tools": {"listChanged": true}` no campo `capabilities` da resposta de inicialização, o que isso indica?

- A) Que o server tem mais de uma ferramenta disponível
- B) Que o server enviará notificações `notifications/tools/list_changed` quando suas ferramentas mudarem
- C) Que as ferramentas do server mudam a cada 24 horas automaticamente
- D) Que o client precisa chamar `tools/list` antes de cada `tools/call`

> **Resposta: B** — `listChanged: true` indica suporte a notificações dinâmicas de mudança de lista de ferramentas. O client que receber essa notificação deve chamar `tools/list` para atualizar seu registro.

---

**Q45.** Como o `inputSchema` de uma ferramenta MCP é definido, segundo a documentação oficial?

- A) Em formato YAML com tipos Python nativos
- B) Como um objeto JSON Schema com propriedades, tipos e campos `required`
- C) Como uma string descritiva em linguagem natural
- D) Em formato OpenAPI 3.0 com referências `$ref`

> **Resposta: B** — A documentação mostra explicitamente: `"inputSchema": {"type": "object", "properties": {...}, "required": [...]}` seguindo JSON Schema.

---

**Q46.** O que são "Tasks (Experimental)" como primitiva utilitária do MCP?

- A) Uma forma de criar ferramentas assíncronas com callbacks
- B) Wrappers de execução durável que permitem recuperação de resultados diferida e rastreamento de status para operações de longa duração
- C) Um sistema de agendamento integrado ao MCP para tarefas recorrentes
- D) Uma primitiva para coordenar múltiplos servers em uma única operação

> **Resposta: B** — Documentação: "Tasks (Experimental): Durable execution wrappers that enable deferred result retrieval and status tracking for MCP requests (e.g., expensive computations, batch processing, multi-step operations)."

---

**Q47.** De acordo com a documentação MCP, qual transport é recomendado para servidores remotos que precisam suportar autenticação?

- A) stdio com tokens passados via variáveis de ambiente
- B) Streamable HTTP, que suporta métodos padrão HTTP como bearer tokens, API keys e headers customizados — recomendando OAuth
- C) WebSocket com TLS mútuo
- D) stdio via SSH tunnel para servidores remotos

> **Resposta: B** — Documentação: "Streamable HTTP transport... supports standard HTTP authentication methods including bearer tokens, API keys, and custom headers. MCP recommends using OAuth to obtain authentication tokens."

---

**Q48.** Por que MCP é descrito como um "protocolo stateful" (com estado)?

- A) Porque as ferramentas mantêm estado interno entre chamadas
- B) Porque requer gerenciamento de ciclo de vida (inicialização, negociação de capabilities, encerramento) e a conexão persiste entre operações
- C) Porque armazena o histórico de todas as chamadas no server
- D) Porque o modelo Claude mantém contexto das ferramentas usadas anteriormente

> **Resposta: B** — Documentação: "MCP is a stateful protocol that requires lifecycle management." (Nota: um subconjunto pode ser stateless usando Streamable HTTP.)

---

## Domínio 5 — Context & Reliability (Q49–Q60)

**Q49.** Qual é o principal benefício do "prompt caching" na API Anthropic, especialmente em aplicações que reutilizam system prompts longos?

- A) Elimina completamente o custo de tokens para requisições repetidas
- B) Reutiliza prefixos processados entre requisições, reduzindo significativamente latência e custo quando partes do prompt não mudam
- C) Comprime automaticamente o prompt antes de enviar, reduzindo tokens de input
- D) Permite que requisições sejam processadas em paralelo no backend da Anthropic

> **Resposta: B** — Prompt caching é especialmente valioso para system prompts longos, documentos de referência e exemplos few-shot que não mudam entre requisições.

---

**Q50.** Como o Claude Code lida com o contexto de conversas longas que se aproximam do limite da janela de contexto?

- A) Encerra a sessão automaticamente e pede ao usuário que reinicie
- B) Comprime automaticamente mensagens anteriores mantendo as mais recentes e relevantes acessíveis
- C) Faz uma chamada separada à API para resumir o histórico
- D) Trunca as mensagens mais antigas sem aviso

> **Resposta: B** — O Claude Code usa compressão automática de contexto para manter sessões longas funcionando sem perder continuidade.

---

**Q51.** Segundo a documentação de tool use, quais são as fontes de tokens adicionais gerados ao usar ferramentas em uma requisição?

- A) Apenas as definições de ferramentas no parâmetro `tools`
- B) O parâmetro `tools` (nomes, descrições e schemas) + blocos `tool_use` nas respostas + blocos `tool_result` nas requisições + system prompt automático de tool use
- C) Apenas os blocos `tool_use` e `tool_result` durante a conversa
- D) Um overhead fixo por requisição, independente do número de ferramentas

> **Resposta: B** — Documentação: "The additional tokens from tool use come from: The `tools` parameter... `tool_use` content blocks... `tool_result` content blocks... we also automatically include a special system prompt for the model which enables tool use."

---

**Q52.** Para um sistema de agente em produção que processa documentos muito maiores que a janela de contexto, qual arquitetura é mais robusta?

- A) Aumentar `max_tokens` até o documento caber completamente no contexto
- B) RAG (Retrieval-Augmented Generation): indexar documentos em vector store, recuperar chunks relevantes por semântica e fornecer apenas o contexto necessário ao modelo
- C) Dividir o documento em partes iguais e processar cada parte em sessões independentes sem relação entre elas
- D) Usar apenas Claude Opus que tem janela de contexto maior

> **Resposta: B** — RAG é a abordagem padrão para lidar com volumes de dados que excedem o contexto: indexação semântica + recuperação precisa + contexto mínimo necessário.

---

**Q53.** Em uma arquitetura de agente autônomo em produção, qual é o indicador mais crítico para detectar que o agente está gerando respostas de baixa qualidade ou alucinando?

- A) Tempo de resposta acima de um limiar fixo
- B) Falha em evals automatizadas — schemas inválidos, respostas fora do domínio esperado, ou divergência de um LLM-as-judge
- C) Número de tokens consumidos por sessão
- D) Número de tool calls por turno

> **Resposta: B** — Monitoramento eficaz combina: validação de schema de output, evals automatizadas com casos de teste, e LLM-as-judge para avaliação semântica de qualidade.

---

**Q54.** O que acontece quando Claude recebe um `tool_result` com conteúdo de erro (ex: stack trace, mensagem de falha)?

- A) Claude encerra o loop e retorna o erro diretamente ao usuário sem processamento
- B) Claude raciocina sobre o erro como faria com qualquer resultado de ferramenta — pode tentar uma abordagem diferente, solicitar informação adicional ou escalar ao usuário
- C) Claude ignora o erro e tenta novamente com os mesmos parâmetros
- D) Claude descarta o resultado e usa seu conhecimento interno como fallback

> **Resposta: B** — O modelo trata `tool_result` com erro como informação: pode reformular a chamada, tentar outra ferramenta ou informar o usuário com contexto claro sobre o problema.

---

**Q55.** Qual é a implicação de rodar Claude Code em modo headless (`-p` / `--print`) para confiabilidade de sistemas autônomos?

- A) Maior confiabilidade pois o modelo é mais conservador sem interação humana
- B) Maior risco: sem supervisão humana no loop, é essencial ter salvaguardas robustas (hooks, validações, permissões restritas) pois erros não são detectados em tempo real
- C) Menor confiabilidade técnica por limitações do modo não-interativo
- D) Nenhuma diferença de confiabilidade — apenas de UX

> **Resposta: B** — Modo headless remove o safety net da supervisão humana. É essencial: permissões mínimas (`allowedTools`), hooks de validação, e evals antes de ir para produção.

---

**Q56.** Por que o princípio do menor privilégio é especialmente crítico para agentes Claude em modo autônomo?

- A) Porque reduz o custo de tokens ao limitar as ferramentas disponíveis
- B) Porque agentes autônomos executam ações sem revisão humana a cada passo, então permissões excessivas podem resultar em ações irreversíveis de grande impacto não intencionadas
- C) Porque a API Anthropic limita automaticamente agentes com muitas permissões
- D) Porque o modelo performa melhor com menos ferramentas disponíveis

> **Resposta: B** — Um agente com permissões de deletar arquivos, modificar produção e enviar emails representa um risco imenso se operar com autonomia total. Conceder apenas o necessário limita o blast radius de erros.

---

**Q57.** Em um pipeline multi-agente com Claude Code, como implementar rastreabilidade eficaz entre etapas?

- A) Usar um único agente para centralizar todos os logs em um lugar
- B) Implementar IDs de correlação únicos por pipeline, logging estruturado por etapa com timestamps, e rastreamento explícito de quais tools foram chamadas com quais parâmetros
- C) Salvar apenas o output final de cada agente pois logs intermediários sobrecarregam o sistema
- D) Confiar no histórico de conversas do Claude como fonte única de verdade

> **Resposta: B** — Rastreabilidade em sistemas distribuídos requer: IDs de correlação para conectar eventos, logs estruturados (JSON) para consulta, e rastreamento granular de tool calls para debugging.

---

**Q58.** Qual estratégia de retry é adequada para ferramentas que falham por problemas transitórios (ex: timeout de rede)?

- A) Retry imediato e ilimitado até obter sucesso
- B) Exponential backoff com número máximo de tentativas definido, idealmente com idempotência na ferramenta para que retries sejam seguros
- C) Nunca fazer retry — escalar imediatamente ao usuário
- D) Retry apenas se o erro for explicitamente marcado como `retryable: true` na definição da ferramenta

> **Resposta: B** — Exponential backoff evita sobrecarregar sistemas degradados. Idempotência garante que chamadas repetidas não causem efeitos colaterais duplicados (ex: criar o mesmo registro duas vezes).

---

**Q59.** Ao escolher entre Claude Opus e Claude Haiku para um pipeline de produção de alto volume, qual é a consideração mais importante de confiabilidade além do custo?

- A) Haiku sempre é menos confiável — usar Opus em produção independente do custo
- B) Avaliar empiricamente com evals no caso de uso específico: Haiku pode ser suficiente para tarefas simples/estruturadas, mas Opus é superior em raciocínio complexo, instrução following e casos de borda
- C) Escolher baseado apenas na latência medida em produção
- D) Usar sempre o modelo mais recente disponível independente da versão

> **Resposta: B** — A escolha deve ser baseada em evals específicos para o caso de uso. Modelos menores são suficientes para tarefas bem definidas, mas modelos maiores têm vantagem em raciocínio complexo e situações ambíguas.

---

**Q60.** Qual técnica de prompt engineering tem o maior impacto direto na redução de alucinações factuais em respostas do Claude?

- A) Aumentar a temperatura para gerar mais candidatos de resposta
- B) Fornecer fontes e documentos relevantes no contexto (grounding/RAG) e instruir explicitamente o modelo a basear respostas apenas no material fornecido
- C) Usar sempre few-shot examples com respostas longas e detalhadas
- D) Reduzir o system prompt ao mínimo para não distrair o modelo

> **Resposta: B** — Grounding com contexto relevante + instrução explícita ("responda apenas com base nos documentos fornecidos, indique quando não há informação suficiente") é a técnica mais eficaz contra alucinações factuais.

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

*Simulado 2 — baseado na documentação oficial da Anthropic e do MCP. Não é material oficial da Anthropic.*
