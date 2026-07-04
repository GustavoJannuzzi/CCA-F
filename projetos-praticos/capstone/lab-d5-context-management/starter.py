"""
Lab D5 — starter. Preservar fatos fixos + handoff + decidir sessão nova.
"""

# TODO 1: mantenha um dict de FATOS FIXOS que não podem se perder na janela.
# Re-injete-os como um bloco no início do contexto a cada turno.
fatos_fixos = {
    "customer_id": None,      # preenchido após verificação
    "order_id": None,
    "politica": "reembolso <=500 automático; >500 humano",
}


def montar_contexto(fatos, historico_recente):
    """
    TODO 2: retorne o system/prefixo re-injetando os fatos fixos + só o
    histórico recente relevante (não a conversa inteira).
    """
    ...


def handoff_para_humano(fatos, causa_raiz, valor, incertezas):
    """
    TODO 3: monte um resumo ESTRUTURADO para o humano que assumirá.
    Deve conter: cliente, order, causa-raiz, valor, ação recomendada
    e o que ainda é INCERTO.
    """
    ...


def decidir_sessao(contexto_degradou: bool):
    """
    TODO 4: retorne "resume" se o contexto está bom e você só quer continuar;
    retorne "nova_sessao_com_resumo" se o contexto DEGRADOU.
    """
    ...
