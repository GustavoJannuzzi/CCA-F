# Padrões de tools (importado pelo CLAUDE.md via @./docs/padroes-de-tools.md)

- Descrições de tool devem dizer QUANDO usar e o que retornam (desambiguar pares parecidos).
- Erros: retorne payload estruturado no `content`; lembre que só `isError` é campo do protocolo MCP.
- Nomes de tool em snake_case, verbos no infinitivo (get_customer, process_refund).

<!-- Este arquivo demonstra a organização MODULAR do CLAUDE.md: em vez de um
     arquivo gigante, você quebra em módulos e importa com @caminho. -->
