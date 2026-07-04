"""
Lab D4 — solução comentada. Critérios explícitos + few-shot + output estruturado + retry.
"""
import os
from anthropic import Anthropic

MODEL = "claude-sonnet-4-6"
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# --- 4.1 CRITÉRIOS EXPLÍCITOS (reduz falso positivo de escalação) ----------
SYSTEM = """Você é o agente de suporte. Resolva o ticket ou escale.

ESCALE PARA HUMANO **somente** se ao menos um for verdadeiro:
- valor de reembolso > R$500;
- é a 2ª+ reclamação do mesmo cliente sobre o mesmo problema;
- há suspeita de fraude (dados inconsistentes, pedido não encontrado).

Caso contrário, RESOLVA você mesmo. Não escale por "parecer complexo":
sem um critério acima satisfeito, resolva.
Sempre registre a decisão chamando a ferramenta registrar_resolucao."""

# --- 4.2 FEW-SHOT: mostra a FRONTEIRA de decisão --------------------------
# Para calibrar QUANDO escalar, a resposta é few-shot com critérios,
# NÃO um "score de confiança".
FEWSHOT = [
    {"role": "user", "content": "Estorno de R$90, pedido atrasado, primeira reclamação."},
    {"role": "assistant", "content": "Decisão: RESOLVER (valor baixo, 1ª vez, sem fraude)."},
    {"role": "user", "content": "Estorno de R$740, item com defeito, primeira vez."},
    {"role": "assistant", "content": "Decisão: ESCALAR (valor > R$500)."},
]

# --- 4.3 OUTPUT ESTRUTURADO via tool_use + JSON schema --------------------
tool_registrar = {
    "name": "registrar_resolucao",
    "description": "Registra a decisão final do ticket no sistema de tickets.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string"},
            "decisao": {"type": "string", "enum": ["resolver", "escalar"]},
            # NULLABLE: pode não haver reembolso. NÃO marque required —
            # senão o modelo inventa um número. Pegadinha do 4.3.
            "valor_reembolso": {"type": ["number", "null"]},
            "justificativa": {"type": "string"},
        },
        "required": ["ticket_id", "decisao", "justificativa"],
    },
}


def _validar(inp):
    faltando = [c for c in ("ticket_id", "decisao", "justificativa") if c not in inp]
    if faltando:
        return f"Faltam campos obrigatórios: {faltando}. Chame a tool de novo completo."
    return None


def resolver_ticket(ticket_texto: str, max_retries=2):
    messages = FEWSHOT + [{"role": "user", "content": ticket_texto}]
    for tentativa in range(max_retries + 1):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, system=SYSTEM,
            tools=[tool_registrar],
            # força a saída estruturada: DEVE chamar esta tool específica
            tool_choice={"type": "tool", "name": "registrar_resolucao"},
            messages=messages,
        )
        bloco = next(b for b in resp.content if b.type == "tool_use")
        erro = _validar(bloco.input)          # 4.4 validação
        if erro is None:
            print("✅ resolução:", bloco.input)
            return bloco.input
        # 4.4 FEEDBACK LOOP: devolve o erro e pede correção
        print(f"↻ retry {tentativa+1}: {erro}")
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": bloco.id, "content": erro, "is_error": True}
        ]})
    raise RuntimeError("Não consegui uma resolução válida após os retries.")


if __name__ == "__main__":
    resolver_ticket("Cliente pede estorno de R$120 de pedido entregue errado, primeira vez.")
