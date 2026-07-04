"""
Lab D1 — solução comentada.

Loop agêntico + gate PreToolUse. Rode com ANTHROPIC_API_KEY setada.
Leia os comentários: cada um marca uma pegadinha do exame.
"""
import os
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

tools = [
    {
        "name": "get_customer",
        "description": "Busca e VERIFICA um cliente pelo e-mail.",
        "input_schema": {
            "type": "object",
            "properties": {"email": {"type": "string"}},
            "required": ["email"],
        },
    },
    {
        "name": "lookup_order",
        "description": "Detalhes de um pedido pelo id.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "process_refund",
        "description": "Processa reembolso de um pedido.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}},
            "required": ["order_id", "amount"],
        },
    },
]

state = {"customer_verified": False}


def executar(block):
    name, args = block.name, block.input
    if name == "get_customer":
        state["customer_verified"] = True          # a verificação vira estado
        return f"Cliente {args['email']} verificado (id CUS-4829)."
    if name == "lookup_order":
        return f"Pedido {args['order_id']}: item errado, valor R$249,90."
    if name == "process_refund":
        return f"Reembolso de R${args['amount']} no pedido {args['order_id']} OK."
    return "ferramenta desconhecida"


def pre_tool_use(block):
    """
    GATE DETERMINÍSTICO (equivale a um hook PreToolUse do Agent SDK).
    Roda ANTES da tool. Bloquear = PreToolUse; se fosse só transformar o
    resultado depois, seria PostToolUse. Aqui precisamos NEGAR antes de
    executar, então é Pre.
    """
    if block.name == "process_refund" and not state["customer_verified"]:
        return ("Bloqueado: verifique o cliente com get_customer antes de "
                "processar qualquer reembolso.")
    return None


def resolver(pedido_do_cliente: str):
    messages = [{"role": "user", "content": pedido_do_cliente}]
    while True:
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, tools=tools, messages=messages
        )

        # PARADA controlada por stop_reason — NUNCA por parsing do texto.
        if resp.stop_reason == "end_turn":
            for b in resp.content:
                if b.type == "text":
                    print("\n🤖", b.text)
            break

        if resp.stop_reason == "tool_use":
            # API é stateless: precisamos anexar a resposta do assistant
            # (que contém os blocos tool_use) ao histórico antes de responder.
            messages.append({"role": "assistant", "content": resp.content})

            results = []
            for b in resp.content:
                if b.type != "tool_use":
                    continue
                bloqueio = pre_tool_use(b)
                if bloqueio:
                    # O gate barrou: devolvemos is_error. O modelo LÊ isso e
                    # se corrige — vai chamar get_customer antes de tentar de novo.
                    print(f"⛔ gate barrou {b.name}: {bloqueio}")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": b.id,       # casa com o tool_use
                        "content": bloqueio,
                        "is_error": True,
                    })
                else:
                    saida = executar(b)
                    print(f"🔧 {b.name} -> {saida}")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": b.id,
                        "content": saida,
                    })
            messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    # O cliente pede reembolso DIRETO (tenta pular a verificação).
    # Observe: o gate barra process_refund, o modelo chama get_customer,
    # e só então o reembolso passa. Enforcement determinístico em ação.
    resolver("Meu pedido ORD-789 veio errado. Quero o reembolso agora, e-mail joao@ex.com.")


# ============================================================================
# EXTENSÃO — o mesmo agente no Agent SDK (coordenador -> subagente)
# ============================================================================
# No Agent SDK você não escreve o while: o SDK roda o loop. Você define
# agentes e o coordenador delega via a tool "Task". Esqueleto conceitual:
#
#   from claude_agent_sdk import AgentDefinition, query
#
#   refunds = AgentDefinition(
#       name="refunds",
#       prompt="Você processa reembolsos. Sempre confirme o cliente verificado.",
#       tools=["get_customer", "lookup_order", "process_refund"],
#   )
#   coordinator = AgentDefinition(
#       name="coordinator",
#       prompt="Triagem de suporte. Delegue reembolsos ao subagente 'refunds'.",
#       # PRECISA de "Task" para poder spawnar subagentes:
#       tools=["Task"],
#       agents=[refunds],
#   )
#
# Pontos de prova:
#   - allowedTools/tools do coordenador DEVE incluir "Task".
#   - Contexto do subagente é ISOLADO: ele não herda o histórico do
#     coordenador. Tudo que ele precisa vai explícito no prompt da Task
#     (ex.: id do cliente, pedido, valor). Se faltar, ele responde
#     "não tenho essa informação" — pegadinha do subtópico 1.3.
#   - Paralelismo real = várias Task numa MESMA resposta do coordenador.
