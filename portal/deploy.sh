#!/usr/bin/env bash
# Atualiza a fábrica na VPS: repositório + os arquivos que o portal executa.
#
# Por que existe: `git pull` sozinho NÃO atualiza o portal. Ele roda de
# /root/portal (cópia), não do repositório — então prompt novo em comandos.py
# fica no repo e o agente continua recebendo o texto velho. Aconteceu em
# 2026-08-09: a lei de transição na emenda foi commitada, deployada "com git
# pull" e a certificação inteira rodou sem ela.
#
# Uso (na VPS): bash /root/.openclaw/workspace/external/fabricjs-template-generator/portal/deploy.sh
set -euo pipefail

REPO=/root/.openclaw/workspace/external/fabricjs-template-generator
DEST=/root/portal

cd "$REPO"
# o npm install reescreve o lockfile; descartar evita o pull recusar
git checkout -- package-lock.json 2>/dev/null || true
git pull -q --rebase origin main
echo "repo: $(git log --oneline -1)"

mkdir -p "$DEST/static"
for f in app.py comandos.py jobs.py knowledge.py telegram.py; do
  [ -f "portal/$f" ] && cp "portal/$f" "$DEST/$f"
done
cp portal/static/*.css "$DEST/static/" 2>/dev/null || true

systemctl restart factory-portal factory-worker
sleep 3
systemctl is-active factory-portal factory-worker

# prova que a cópia bateu com o repo — o erro que motivou este script
for f in app.py comandos.py jobs.py knowledge.py telegram.py; do
  if [ -f "portal/$f" ] && ! diff -q "portal/$f" "$DEST/$f" >/dev/null; then
    echo "FALHOU: $f divergente"; exit 1
  fi
done
echo "portal sincronizado com o repo"
