"""
Lab D5 — solução comentada. Contexto: fatos fixos, handoff, sessão nova, PostToolUse.
"""
import json
from datetime import datetime

# --- 5.1 FATOS FIXOS: re-injetados a cada turno --------------------------
# Não confie que a mensagem antiga continue na janela numa conversa longa.
# O que é crítico vira um bloco persistente que você sempre reenvia.
fatos_fixos = {
    "customer_id": "CUS-4829",
    "order_id": "ORD-789",
    "politica": "reembolso <=500 automático; >500 humano",
}


def montar_contexto(fatos, historico_recente):
    bloco = "FATOS FIXOS (sempre válidos):\n" + json.dumps(fatos, ensure_ascii=False, indent=2)
    # Só o histórico RECENTE relevante — não a conversa inteira (economiza janela).
    return bloco + "\n\nHistórico recente:\n" + "\n".join(historico_recente[-6:])


# --- 5.2 HANDOFF ESTRUTURADO para humano (que não viu a conversa) ---------
def handoff_para_humano(fatos, causa_raiz, valor, incertezas):
    return {
        "resumo_para_humano": {
            "cliente": fatos["customer_id"],
            "pedido": fatos["order_id"],
            "causa_raiz": causa_raiz,
            "valor": valor,
            "acao_recomendada": "aprovar reembolso" if valor <= 500 else "revisar (>R$500)",
            "incertezas": incertezas,          # 5.6: sinalize o que NÃO se sabe
            "gerado_em": datetime.now().isoformat(timespec="seconds"),
        }
    }


# --- 5.4 RESUME vs SESSÃO NOVA -------------------------------------------
def decidir_sessao(contexto_degradou: bool):
    # Contexto bom -> resume. Contexto DEGRADOU -> sessão nova com resumo
    # (--resume só traria o mesmo contexto poluído de volta).
    return "nova_sessao_com_resumo" if contexto_degradou else "resume"


# --- 5.1 PostToolUse: normalizar resultados DEPOIS da tool ----------------
def post_tool_use_normalizar_data(tool_result_content: str):
    """
    Ferramentas MCP retornam datas em formatos diferentes (Unix, ISO, código).
    Normalize DEPOIS que a tool respondeu, antes do modelo ver.
    Bloquear seria PreToolUse; TRANSFORMAR resultado é PostToolUse.
    """
    # exemplo bobo: troca timestamp unix por ISO
    import re
    def _fix(m):
        return datetime.utcfromtimestamp(int(m.group())).date().isoformat()
    return re.sub(r"\b1[0-9]{9}\b", _fix, tool_result_content)


if __name__ == "__main__":
    print(montar_contexto(fatos_fixos, ["cliente: item errado", "verifiquei CUS-4829"]))
    print("\nHandoff:\n", json.dumps(
        handoff_para_humano(fatos_fixos, "item trocado no envio", 249.90,
                            ["cliente não confirmou se quer troca ou estorno"]),
        ensure_ascii=False, indent=2))
    print("\nContexto degradou? ->", decidir_sessao(True))
    print("Normalizado:", post_tool_use_normalizar_data("pedido em 1710460800 saiu"))
