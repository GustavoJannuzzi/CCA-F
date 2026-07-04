"""
Mini-lab Multi-Agent — starter. Coordenador -> subagentes com contexto isolado.
Foco conceitual (roda sem chave): entender decomposição, contexto e paralelismo.
"""

# TODO 1: decomponha a pergunta em subtarefas INDEPENDENTES (paralelizáveis)
# e dependentes (sequenciais). Ex.: buscar por região = paralelo;
# sintetizar depende das buscas = sequencial.
def decompor(pergunta: str):
    ...  # retorne (subtarefas_paralelas, subtarefas_sequenciais)


# TODO 2: monte o prompt de uma Task com CONTEXTO COMPLETO (o subagente não
# herda nada). Inclua o que buscar + como reportar (com fonte!).
def prompt_task(subtarefa: str) -> str:
    ...


# TODO 3: cada achado deve carregar PROVENIÊNCIA (fonte). Modele o retorno.
def achado(conteudo: str, fonte: str, confianca: str):
    ...


# TODO 4: na síntese, preserve a atribuição das fontes e sinalize incertezas.
def sintetizar(achados: list) -> str:
    ...
