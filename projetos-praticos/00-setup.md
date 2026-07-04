# 00 — Setup do ambiente

Só precisa fazer isto **se quiser rodar** os labs. Para estudar em modo read-along, pode pular.

## 1. Python + ambiente virtual

```bash
python --version            # precisa ser 3.10+
python -m venv .venv

# ativar:
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows (PowerShell)
```

## 2. Dependências

```bash
pip install anthropic claude-agent-sdk
```

- **`anthropic`** — SDK da Claude API crua (o loop de `messages.create`, `tool_use`/`tool_result`, batches, structured outputs). Usado nos labs que ilustram a **API**.
- **`claude-agent-sdk`** — o Agent SDK (ex-"Claude Code SDK"): coordenador/subagentes, `AgentDefinition`, `allowedTools`, hooks em código. Usado nos labs de **orquestração e agentes**.

> 💡 **Onde cada coisa vive** (fio condutor da apostila): a *Claude API* é o loop cru e stateless; o *Agent SDK* é a biblioteca para construir agentes sobre essa API; o *Claude Code (CLI)* é um agente pronto sobre o Agent SDK, configurado por arquivos (`CLAUDE.md`, `.claude/`, `.mcp.json`). O lab do Domínio 3 é quase todo **config**, não Python.

## 3. API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."     # macOS/Linux
$env:ANTHROPIC_API_KEY = "sk-ant-..."     # Windows (PowerShell)
```

Nunca coloque a key no código nem faça commit dela. Os labs leem de `os.environ["ANTHROPIC_API_KEY"]`.

## 4. Modelos

Use um modelo atual nos exemplos, ex.: `claude-sonnet-4-6` (bom custo/qualidade para agentes) ou o mais capaz da família para tarefas de raciocínio. Os labs deixam o id do modelo numa constante no topo do arquivo para você trocar fácil.

## 5. Rodar um lab

```bash
cd capstone/lab-d1-loop-e-orquestracao
python solucao.py          # ou edite o starter.py e rode ele
```

Se não tiver key, os labs de API/SDK vão falhar na chamada de rede — mas o código e os comentários continuam servindo para estudo.
