#!/usr/bin/env bash
# Rode o MESMO review localmente antes de abrir o PR.
# Requer: claude code instalado e ANTHROPIC_API_KEY setada.
set -euo pipefail

# diff das suas mudanças ainda não commitadas (ou troque por um range de commits)
git diff > /tmp/pr.diff

claude -p "$(cat prompt-review.md)

DIFF A REVISAR:
$(cat /tmp/pr.diff)" \
  --output-format json \
  --max-turns 6 \
| jq -r '.result'
