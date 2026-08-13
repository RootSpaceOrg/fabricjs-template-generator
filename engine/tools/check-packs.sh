#!/usr/bin/env bash
# Roda o conversor em TODOS os exemplares de TODOS os packs.
#
# Existe porque mexer em gate ou em CSS compartilhado quebra pack que ninguem
# estava olhando: um exemplar certificado ficou reprovando por semanas, e dois
# outros quebraram quando uma imagem foi trocada em so um dos tres consumidores.
# `build-exemplos.js <pack>` valida um pack; isto valida a casa inteira.
#
# Uso: bash engine/tools/check-packs.sh
# Saida: uma linha por exemplar. Codigo != 0 se algum reprovar.
set -uo pipefail
cd "$(dirname "$0")/../.."

falhas=0
for f in packs/*/exemplos/*.html; do
  pack=$(basename "$(dirname "$(dirname "$f")")")
  nome=$(basename "$f" .html)
  printf '%-32s %-38s ' "$pack" "$nome"
  if saida=$(node engine/convert.js "$f" /tmp/check-packs --slug c 2>&1); then
    echo "PASS"
  else
    echo "REJEITADO"
    echo "$saida" | grep -E '^(REJEITADO|  )' | head -4 | sed 's/^/      /'
    falhas=$((falhas + 1))
  fi
done

echo
if [ "$falhas" -gt 0 ]; then
  echo "$falhas exemplar(es) reprovando."
  exit 1
fi
echo "todos os exemplares passam."
