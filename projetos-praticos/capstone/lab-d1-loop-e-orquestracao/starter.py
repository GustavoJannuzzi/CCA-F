"""
Lab D1 — starter (com TODOs). Preencha os TODOs; compare com solucao.py.

Objetivo: um loop agêntico de suporte com um gate PreToolUse que impede
reembolso sem verificação do cliente.
"""
import os
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# --- Ferramentas mock (no D2 desenhamos as descrições direito) -----------
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

# Estado do agente (o que o gate consulta)
state = {"customer_verified": False}


def executar(block):
    """Implementação mock de cada tool. Atualiza o state."""
    name, args = block.name, block.input
    if name == "get_customer":
        state["customer_verified"] = True
        return f"Cliente {args['email']} verificado (id CUS-4829)."
    if name == "lookup_order":
        return f"Pedido {args['order_id']}: item errado, valor R$249,90."
    if name == "process_refund":
        return f"Reembolso de R${args['amount']} no pedido {args['order_id']} OK."
    return "ferramenta desconhecida"


def pre_tool_use(block):
    """
    TODO 1: gate determinístico.
    Se a tool for 'process_refund' e state['customer_verified'] for False,
    retorne uma STRING de bloqueio (motivo). Senão retorne None (libera).
    """
    ...


def resolver(pedido_do_cliente: str):
    messages = [{"role": "user", "content": pedido_do_cliente}]
    while True:
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, tools=tools, messages=messages
        )
        # TODO 2: se stop_reason == "end_turn", imprima o texto final e pare (break).
        # TODO 3: se stop_reason == "tool_use":
        #   - anexe a resposta do assistant ao messages
        #   - para cada bloco tool_use, chame pre_tool_use(block):
        #       * se bloqueado -> monte um tool_result com is_error=True e o motivo
        #       * senão        -> execute(block) e monte tool_result normal
        #   - anexe {"role":"user","content": [<tool_results>]} ao messages
        ...


if __name__ == "__main__":
    # Pedido que TENTA pular a verificação (pede reembolso direto):
    resolver("Meu pedido ORD-789 veio errado. Quero o reembolso agora, e-mail joao@ex.com.")
