# bt-pipeline — Orquestrador

Entrada: **ideia + business_type** (+ opcionais: etapa do funil, referência visual, regras de estilo, ambiente, N).
Saída: **1 template publicado** (`userReady`, `status review`) + relatório.

Defaults: `tenant kultivai`, `vertical health`, ambiente **dev** (prod só quando o usuário pedir "em prod"), **N=3** candidatos (N=1 se o usuário pedir "rápido").

## Passos

### 1. Resolver tenant + business_type

```bash
python bt/scripts/resolve_tenant.py --tenant <t> --vertical <v> --subject "<business_type>" --env <env>
```

- exit 0 → `matchedBusinessType.value` é o slug canônico em tudo (dossiê, tags, upload).
- exit 2/3 → pare; reporte o `adminLink` para cadastro. Não invente slug.
- exit 4 → mostre os businessTypes retornados e pergunte. Não force match.

### 2. Contexto + storyline

Siga [`CONTEXT.md`](./CONTEXT.md). Produz `artifacts/bt/<slug>/brief.md` com: dossiê aplicado, etapa do funil, storyline na espinha, copy por slide, restrições de compliance, doutrina de design.

### 3. Candidatos de design (paralelo)

Spawne **N sub-agents em paralelo** (uma única mensagem, N chamadas Agent). Cada um:

- Recebe: o `brief.md` completo + [`DESIGN.md`](./DESIGN.md) como instrução + **uma família estética distinta** (você atribui — 3 famílias diferentes de `skills/gp2-html-designer/references/aesthetic-families.md`, coerentes com o tom do brief; com referência visual anexada, os 3 herdam a referência mas variam a interpretação).
- Produz: `artifacts/bt/<slug>/candidates/<A|B|C>/strip.html` (fita panorâmica) + `template.html` (fatiado via `slice-strip.js`) + `strip.png` + `screenshots/` + `design-notes.md`.

Candidato que falhar não derruba o batch — o judge decide entre os que entregaram (≥1 obrigatório).

### 4. Julgamento

Spawne **1 sub-agent em contexto limpo** com [`JUDGE.md`](./JUDGE.md). Ele recebe só: screenshots dos candidatos (anonimizados A/B/C), a storyline do brief (para checar aderência), a rubrica e os exemplares. Produz `judge-report.md` com: vencedor, scores, blockers técnicos e **top-3 fixes**.

- Todos os candidatos com blocker insanável → 1 nova rodada de candidatos (máx 1); persiste → pare e reporte com evidências.

### 5. Barra de publicação + revisão do vencedor

**Vencer não basta — tem que passar a barra: total ≥30/50 E craft ≥6.**

- **Passou a barra** → aplica os top-3 fixes do judge (1 passada, re-render, screenshots finais). Não re-julgue — fixes são pontuais.
- **Não passou** → os 3 candidatos eram medíocres; "o menos pior" NUNCA é publicado. Rode **1 rodada de redesign**: novos candidatos com os defeitos apontados pelo judge como restrições explícitas no prompt (ex: "fita monocromática reprovada — ≥2 mudanças de fundo obrigatórias") e famílias estéticas diferentes das da rodada 1. Re-julgue.
- **Segunda rodada também abaixo da barra** → pare e reporte com o judge-report + strips das duas rodadas. Publicar peça fraca custa mais caro que não publicar.

### 6. Finalização e publicação

Siga [`FINALIZE.md`](./FINALIZE.md): imagens geradas → marcação → conversão Fabric → validadores → upload `userReady` com business_type/tenant/vertical/tags de funil.

### 7. Relatório

```markdown
## bt-pipeline — <ideia> · <business_type> · <env>
- Template ID: <id> · scope vertical · userReady · review
- Funil: <etapa> · objetivo <obj> · framework <fw>
- Storyline: S1 gancho ... / S2 problema ... / ...
- Candidatos: A (<família>) · B (<família>) · C (<família>) → vencedor <X> (<score> vs <score> vs <score>)
- Top fixes aplicados: <lista>
- Imagens geradas: <n> (<URLs>)
- Dossiê: knowledge/<slug>.md (updated <data>)
- Gates: marker PASS · converter PASS · validate-slides exit 0
```

## Regras do orquestrador

- **Ambiente é mecânico, não narrativo**: o ambiente pedido pelo usuário vira `--env <x>` literal em TODO comando (resolve_tenant, generate-image, uploader) e aparece no cabeçalho do relatório. Pedido "dev" + qualquer comando sem `--env dev` = bug seu. NUNCA suba pra prod quando o pedido diz dev — na dúvida, dev.

- Nunca pule o judge, mesmo com N=1 (com 1 candidato ele vira gate de qualidade + blockers técnicos).
- Nunca publique candidato reprovado, abaixo da barra (total <30 ou craft <6) ou sem os fixes aplicados.
- Storyline sem os 5 beats → volte ao passo 2, não siga.
- Após publicar, anexe o score do vencedor em `bt/evals/scores.jsonl` (ver `evals/README.md`).
- Mudou qualquer arquivo de `bt/`? Rode a regressão de `evals/` antes do próximo batch de produção.
