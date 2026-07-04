"""
Lab D4 — starter. Prompt com critérios + few-shot + output estruturado.
"""
import os
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# TODO 1: system prompt com CRITÉRIOS EXPLÍCITOS de escalação.
# Liste o que conta como escalar (ex.: valor > 500, 2ª reclamação, fraude).
# Critério explícito reduz falso positivo (4.1).
SYSTEM = "..."

# TODO 2: few-shot — 2 ou 3 exemplos de (ticket -> decisão) que mostram a
# fronteira de decisão. Coloque como turnos user/assistant no messages (4.2).
FEWSHOT = []  # [{"role":"user","content":...},{"role":"assistant","content":...}, ...]

# TODO 3: tool de OUTPUT ESTRUTURADO. Defina input_schema com:
#   - ticket_id (string, required)
#   - decisao   (enum: "resolver" | "escalar", required)
#   - valor_reembolso (number OU null -> nullable, NÃO required)
#   - justificativa (string, required)
tool_registrar = {
    "name": "registrar_resolucao",
    "description": "Registra a decisão final do ticket no sistema.",
    "input_schema": {"type": "object", "properties": {}, "required": []},  # TODO
}


def resolver_ticket(ticket_texto: str):
    messages = FEWSHOT + [{"role": "user", "content": ticket_texto}]
    # TODO 4: force a saída estruturada com tool_choice apontando para a tool.
    # TODO 5: valide o input retornado; se faltar campo, reenvie o erro ao
    #         modelo (feedback loop) e tente de novo (4.4).
    ...


if __name__ == "__main__":
    resolver_ticket("Cliente pede estorno de R$120 de pedido entregue errado, primeira vez.")
