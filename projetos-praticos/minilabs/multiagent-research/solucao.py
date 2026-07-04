"""
Mini-lab Multi-Agent — solução comentada.

Parte A: simulação didática (roda SEM chave) para ver o fluxo coordenador->subagentes.
Parte B: esqueleto real com claude_agent_sdk (comentado).
"""

# ============================== PARTE A ====================================
def decompor(pergunta: str):
    # PARALELO: subtarefas independentes (§1.3 paralelismo).
    paralelas = [
        "Política de IA na União Europeia (AI Act) em 2025",
        "Política de IA nos EUA (executive orders, NIST) em 2025",
        "Política de IA na China em 2025",
    ]
    # SEQUENCIAL: depende dos resultados acima.
    sequenciais = ["Sintetizar diferenças regulatórias entre as 3 regiões"]
    # ARMADILHA (§1.2): se eu listasse só "UE", a cobertura sairia estreita
    # e o relatório seria parcial mesmo com os subagentes acertando.
    return paralelas, sequenciais


def prompt_task(subtarefa: str) -> str:
    # Contexto ISOLADO: o subagente começa do zero. Passo TUDO explícito,
    # inclusive COMO reportar (com fonte) — senão a proveniência se perde.
    return (
        f"Objetivo: {subtarefa}\n"
        "Critérios de qualidade: fatos verificáveis, 2025, foco regulatório.\n"
        "Reporte cada achado como: '<fato> [fonte: <url/doc>] (confiança: alta/média/baixa)'.\n"
        "Se algo for incerto, diga explicitamente."
    )


def achado(conteudo, fonte, confianca):
    return {"conteudo": conteudo, "fonte": fonte, "confianca": confianca}  # §5.6 proveniência


def sintetizar(achados):
    linhas = ["SÍNTESE (com atribuição de fontes):"]
    incertos = []
    for a in achados:
        linhas.append(f"- {a['conteudo']}  [fonte: {a['fonte']}]")
        if a["confianca"] == "baixa":
            incertos.append(a["conteudo"])
    if incertos:
        linhas.append("\n⚠️ Incertezas a confirmar: " + "; ".join(incertos))
    return "\n".join(linhas)


def executar_simulacao():
    paralelas, sequenciais = decompor("Como IA é regulada globalmente em 2025?")
    print("PARALELAS (mesma resposta do coordenador = várias Task de uma vez):")
    for s in paralelas:
        print("  Task ->", repr(prompt_task(s))[:70], "...")
    print("SEQUENCIAL (após as buscas):", sequenciais)

    achados = [
        achado("UE aprovou o AI Act com tiers de risco", "eur-lex.europa.eu", "alta"),
        achado("EUA seguem via executive orders + NIST framework", "nist.gov", "alta"),
        achado("China endureceu regras de IA generativa", "blog secundário", "baixa"),
    ]
    print("\n" + sintetizar(achados))


if __name__ == "__main__":
    executar_simulacao()


# ============================== PARTE B ====================================
# Esqueleto REAL no Agent SDK (requer chave e o pacote claude_agent_sdk):
#
#   from claude_agent_sdk import AgentDefinition, query
#
#   buscar = AgentDefinition(name="buscar_web",
#       prompt="Você pesquisa fatos e SEMPRE reporta a fonte.",
#       tools=["WebSearch"])
#   sintetizar_ag = AgentDefinition(name="sintetizar",
#       prompt="Você sintetiza preservando as fontes e marcando incertezas.",
#       tools=[])
#   coordenador = AgentDefinition(name="coordenador",
#       prompt="Decomponha a pergunta em subtarefas e delegue. Evite decomposição estreita.",
#       tools=["Task"],              # <- SEM "Task" o coordenador NÃO delega
#       agents=[buscar, sintetizar_ag])
#
# Provas:
#   - "Task" obrigatório em tools do coordenador.
#   - Paralelismo = coordenador emite VÁRIAS Task numa mesma resposta.
#   - Contexto do subagente é isolado -> prompt_task() carrega tudo.
