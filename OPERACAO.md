# Operação — como a fábrica roda na prática

Complementa [ARCHITECTURE.md](ARCHITECTURE.md) (o que é) e [PACKS.md](PACKS.md)
(o que é um pack). Aqui está o **runbook**: quem dispara o quê, em que ordem.

## 0. Dois modos que NÃO se misturam

| | **Produção** (habitual) | **Criação de pack** (excepcional) |
|---|---|---|
| Quando | usuário/Gustavo pede um post | um estilo novo entra na fábrica |
| Pack | `status: certificado` | `status: draft` até o carimbo |
| Quem roda | agente sozinho, ponta a ponta (`engine/run.py` + skill `template-factory`) | agente compõe, Claude opera corredor e critica |
| Revisão | judge → Gustavo | judge → **revisão prévia do Claude** → Gustavo |
| Saída | template publicado | 3 fitas de prova + `certification/` + carimbo |

**Regra de ouro:** a criação de pack é um andaime, não um caminho novo de
geração. A produção habitual continua sendo *uma run, um agente, o corredor de
sempre* — nada do runbook abaixo entra no fluxo do dia a dia. Se um pack
certificado exigir Claude no meio para gerar um post, o pack não estava pronto.

## 1. Produção (o fluxo normal)

```
pedido (portal/Telegram) → agente: resolve → dossiê → fita.html → render →
convert → JUDGE ATÉ PASSAR (o agente corrige e re-julga sozinho, até 3 voltas)
→ Gustavo recebe a fita já limpa → aprova → agente: fidelidade → publica em dev
```

O judge roda **antes** do Gustavo: ele é a peneira automática, não um porteiro
depois do veredito humano. Aprovar significa "pode publicar" — o agente só
interrompe se encontrar defeito objetivo que o strip não revelava.

Claude não participa. Se a run travar por limitação do motor, aí sim vira
tarefa de Claude — **consertar o motor**, não a peça.

## 2. Criação de pack (o andaime)

Ordem que funcionou (packs 1–3):

1. **Referência → conhecimento** (Claude): assinaturas primeiro, depois
   `pack.json` (paleta fechada), `tecnicas.md`, `images.md`, `lessons.md`.
   Reference.png sai da `pack-queue/`.
2. **Peça de prova** (agente): uma fita/peça pequena para validar as apostas
   do estilo. Se o estilo pedir algo que o catálogo não expressa → mudança de
   MOTOR, com aval do Gustavo (PACKS §6).
3. **Loop de revisão** (Claude ↔ agente): Claude renderiza, critica com
   evidência (mede no JSON, inspeciona o HTML — não adivinha pela imagem) e
   devolve. Repete até passar. Só então vai para o Gustavo.
4. **Vereditos viram conhecimento**: o que o Gustavo reprova vira lei no pack
   (específico do estilo) ou em `knowledge/design/geral.md` (vale para todos).
   Defeito que reaparece 2× = a lei estava mal escrita.
5. **Certificação**: 3 fitas em **3, 5 e 7 slides** (PACKS §4), judge PASS,
   upload dev, `certification/` com strips + reports + shas, carimbo do
   Gustavo (`draft → certificado`).

## 3. Como disparar o agente (OpenClaw)

Turno one-shot por SSH, detached (a janela do agente **não** aguenta uma run
inteira com geração de imagem — fatie):

```bash
setsid nohup node /usr/lib/node_modules/openclaw/dist/index.js agent \
  --agent main -m '<instrução>' > /root/hermes-workspace/<tag>.log 2>&1 &
```

- Fatias que funcionam: *"componha e PARE no compose"* · *"julgue e faça
  upload"* · *"gere estes N assets"*.
- Sempre peça `git pull --rebase` no início e cite os arquivos de conhecimento
  que ele deve ler.
- Acompanhe com poll do `run.json` (`stage`) e do `pgrep` do turno; o log fica
  no arquivo acima.

**Clones no VPS:** agente em `/root/.openclaw/workspace/external/fabricjs-template-generator`;
Claude em `/root/hermes-workspace/fabricjs-template-generator`. Conhecimento
sincroniza por git (pull no início, push no fim).

## 4. Corredor mecânico (Claude, entre as fatias)

```bash
export PATH=/root/.nvm/versions/node/v24.18.1/bin:$PATH
R=artifacts/runs/<slug>
node engine/assemble.js $R          # fita.html → strip.png + slide-N.png
node engine/convert.js  $R $R/output --slug <slug>
node engine/tools/validate-slides.js $R/output
python3 engine/run.py advance <slug>
```

Upload dev: `engine/tools/import-template.py` (assume role + S3). Reupload de
uma run já publicada = sobrescrever `editor_templates/<template_id>/<i>/template.json`.

## 5. Revisão prévia do Claude — como criticar

- **Meça, não adivinhe**: `fontSize`/`fill`/`top` no JSON, `grid-area` no HTML.
  Metade dos defeitos "de composição" era limitação de motor.
- Devolva crítica **numerada e específica** (elemento, sintoma, correção
  sugerida), separando o que é motor (Claude conserta) do que é composição
  (agente refaz).
- Nunca reescreva a fita para "adiantar" — isso quebra a prova da certificação
  (ARCHITECTURE §4).

## 6. Sinais de que o pack está pronto

Voltas de revisão caindo a cada fita (packs 1–3: 6 → 2 → 1). Fita nova saindo
quase limpa = o conhecimento está escrito. Se toda fita precisa de muitas
voltas, falta conhecimento — escreva lei, não HTML.
