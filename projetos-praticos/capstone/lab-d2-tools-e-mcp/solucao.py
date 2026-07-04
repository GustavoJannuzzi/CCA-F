"""
Lab D2 — solução comentada. Tools desenhadas para desambiguar + erro estruturado.
"""
import json

# ---------------------------------------------------------------------------
# 1) DESCRIÇÕES QUE DESAMBIGUAM
# Regra de ouro (2.1): a descrição é o "manual" que o modelo lê para ESCOLHER.
# Quando duas tools são parecidas, a correção é MELHORAR A DESCRIÇÃO
# (dizer quando usar cada uma), não adicionar few-shot.
# ---------------------------------------------------------------------------
tools = [
    {
        "name": "lookup_order",
        "description": (
            "Retorna os DETALHES COMPLETOS de um pedido: itens, valores, datas, "
            "endereço e histórico de pagamento. Use quando precisar de qualquer "
            "informação além do status de entrega (ex.: para avaliar um reembolso). "
            "Para saber apenas 'onde está meu pedido', prefira get_order_status."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "ex.: ORD-789"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "get_order_status",
        "description": (
            "Retorna SOMENTE o status de entrega de um pedido (ex.: 'em trânsito', "
            "'entregue em 15/03'). Leve e rápido. Use para perguntas de rastreio. "
            "NÃO retorna valores nem itens — para isso use lookup_order."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "process_refund",
        "description": (
            "Processa o reembolso de um pedido. Só pode ser chamada APÓS o cliente "
            "ter sido verificado. Reembolsos acima de R$500 exigem aprovação humana "
            "e serão recusados por esta ferramenta."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number", "description": "em reais"},
            },
            "required": ["order_id", "amount"],
        },
    },
]


# ---------------------------------------------------------------------------
# 2) ERRO ESTRUTURADO
# PEGADINHA (2.2): no protocolo MCP, o ÚNICO campo padrão é isError.
# error_category / is_retryable / alternatives NÃO são protocolo —
# são convenção da SUA app, transportados dentro do `content`.
# ---------------------------------------------------------------------------
def refund_result(tool_use_id, order_id, amount):
    if amount > 500:
        payload = {
            "message": f"Reembolso de R${amount} excede o limite de R$500.",
            # convenção da app (dentro do content, não campos do protocolo):
            "error_category": "approval_required",
            "is_retryable": False,
            "alternatives": ["escalar_para_humano", "reembolso_parcial<=500"],
        }
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": json.dumps(payload, ensure_ascii=False),
            "is_error": True,          # <- ESTE é o campo do protocolo
        }
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": f"Reembolso de R${amount} no pedido {order_id} processado.",
        # sem is_error => sucesso
    }


# ---------------------------------------------------------------------------
# 3) tool_choice — quando usar cada modo (2.3)
# ---------------------------------------------------------------------------
TOOL_CHOICE = {
    "a_chat_geral": {"type": "auto"},                          # pode responder texto
    "b_sempre_uma_acao": {"type": "any"},                      # deve chamar ALGUMA tool
    "c_forcar_extracao": {"type": "tool", "name": "classificar_intencao"},  # tool específica
}

if __name__ == "__main__":
    print("Erro estruturado (amount=900):")
    print(json.dumps(refund_result("tu_1", "ORD-789", 900), indent=2, ensure_ascii=False))
    print("\nSucesso (amount=249.90):")
    print(json.dumps(refund_result("tu_2", "ORD-789", 249.90), indent=2, ensure_ascii=False))
    print("\ntool_choice por cenário:", json.dumps(TOOL_CHOICE, indent=2, ensure_ascii=False))
