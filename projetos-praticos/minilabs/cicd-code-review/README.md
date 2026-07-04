# Mini-lab — Claude Code em CI/CD (review de PR headless)

> **Cenário oficial:** *Claude Code for CI/CD*. Fecha o Domínio 3 (§3.6) com um pé no Domínio 5 (review multi-passagem). Aqui o Claude Code roda **sem humano no terminal**.

## 📖 O que você já estudou
- **3.6** Claude Code em CI/CD · **4.6** review multi-instância/multi-passagem · **5.4** contexto em codebase grande

## 🎯 O que você vai construir
Um workflow do GitHub Actions que, a cada PR, roda o Claude Code em **modo headless** para revisar o diff e postar comentários. Peças:

| Arquivo | Papel |
|---------|-------|
| [`.github/workflows/claude-review.yml`](.github/workflows/claude-review.yml) | dispara no PR, roda `claude -p` |
| [`prompt-review.md`](prompt-review.md) | o prompt de review (critérios explícitos) |
| [`run-local.sh`](run-local.sh) | rodar o mesmo review localmente |

## 🧠 Por que headless e as flags que caem na prova
- **`claude -p "..."` (print mode)** = não-interativo, one-shot. Em CI, **evita o processo travar esperando input** — esta é a razão que a prova quer.
- **`--output-format json`** = saída estruturada para o script consumir (parsear achados, decidir se falha o build).
- **`--max-turns N`** = teto de turnos → **controle de custo** em automação.
- **`--permission-mode`** para não pedir confirmação interativa (em CI não há quem confirme).

## 🧠 Multi-passagem (§4.6 / §5.4)
Um PR com 14 arquivos **não** cabe bem numa "única passagem com contexto gigante" — a resposta certa do exame é **múltiplas passagens**: um review por arquivo + uma passagem de integração. Isso mantém cada contexto focado e evita degradação. O workflow abaixo mostra o gancho para isso.

## 🧪 Ligações com o exame
- *"CI trava esperando input"* → `claude -p` (não-interativo).
- *"Integrar saída com o pipeline"* → `--output-format json`.
- *"Controlar custo da automação"* → `--max-turns`.
- *"Revisar 14 arquivos"* → **múltiplas passagens**, não uma só com contexto enorme.
- *Verificação pré-merge síncrona* → **API síncrona**, NÃO Batches API (batch é 24h, sem SLA — impróprio para bloquear merge).
