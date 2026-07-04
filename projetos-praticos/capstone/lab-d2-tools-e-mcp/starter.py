"""
Lab D2 — starter. Refatore as tools do agente de suporte.
Foco em: descrições que desambiguam + erros estruturados + tool_choice.
"""

# TODO 1: escreva descrições que digam QUANDO usar cada tool e o que retornam.
#         lookup_order e get_order_status são fáceis de confundir — desambigue.
tools = [
    {
        "name": "lookup_order",
        "description": "...",   # TODO: detalhes completos do pedido; quando usar
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "ex.: ORD-789"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "get_order_status",
        "description": "...",   # TODO: SÓ o status de entrega; quando usar em vez de lookup_order
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "process_refund",
        "description": "...",   # TODO: limites (ex.: <= R$500 sem aprovação humana)
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["order_id", "amount"],
        },
    },
]


def refund_result(order_id, amount):
    """
    TODO 2: retorne um resultado ESTRUTURADO.
    - Se amount > 500: falha. Monte um dict de resultado com:
        * is_error = True                (ÚNICO campo do protocolo MCP)
        * content com um JSON de convenção da app: error_category,
          is_retryable, alternatives  (isso NÃO é protocolo — é seu)
    - Senão: sucesso (is_error ausente/False).
    Retorne o dict no formato tool_result.
    """
    ...


# TODO 3: para cada cenário abaixo, diga qual tool_choice usar (comente):
#   a) chat de suporte geral (pode responder texto)           -> ?
#   b) toda mensagem deve virar uma ação de tool               -> ?
#   c) forçar extração via a tool "classificar_intencao"       -> ?
