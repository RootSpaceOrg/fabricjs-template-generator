# bt-pipeline — Orquestrador

Entrada: **ideia + business_type** (+ opcionais: etapa do funil, referência visual, regras de estilo, ambiente, N).
Saída: **1 template publicado** (`userReady`, `status review`) + relatório.

Defaults: `tenant kultivai`, `vertical health`, ambiente **dev** (prod só quando o usuário pedir "em prod"), **N=3** candidatos (N=1 se o usuário pedir "rápido").

## Dois modos de geração

| Modo | Quando | Como |
|------|--------|------|
| **Estilo certificado** (default quando existe estilo com fit) | pedido nomeia um estilo de `bt/styles/`, OU o context encontra estilo `status: certificado` com fit (família × funil × vertical) | Passo 3 vira **instanciação**: preencher o `strip-blueprint.html` do estilo (copy nos placeholders respeitando min/max + imagens pelas fórmulas `data-bt-generate` + blocos opcionais), N=1, judge em modo QA (R1–R6 + overflow + coerência das imagens; sem pairwise). Marker só gera `data-te-description` (o resto vem pré-anotado). Ver `bt/styles/README.md`. |
| **Livre (laboratório)** | nenhum estilo certificado serve, pedido explícito "design livre", ou criação de candidato a novo estilo | Fluxo completo abaixo (best-of-N + judge pairwise). Vencedores excepcionais viram candidatos a novo estilo (protocolo de certificação no README de styles). |

Enquanto não houver estilos `certificado`, todo pedido roda em modo livre.

## Estado obrigatório — `bt/scripts/run.py`

A coordenação é mecânica, não narrativa. TODA execução:

```bash
python bt/scripts/run.py new <slug> --env <dev|prod> [--n 3]   # primeiro comando, sempre
python bt/scripts/run.py status <slug>                          # o que falta no estágio atual
python bt/scripts/run.py advance <slug>                         # só avança se o artefato exigido existe
```

- Estágios: resolve → context → candidates → judge → fixes → finalize → upload. Cada um exige artefato em disco (lista no `--help`); `advance` **nega** sem ele.
- **Nunca declare um estágio concluído sem `advance` ter aceitado.** "Disparei o sub-agente" não é progresso; artefato no disco é.
- **Um `advance` aceito NÃO é ponto de parada** — é o sinal para começar o próximo estágio IMEDIATAMENTE, na mesma sessão. A run só para em 3 situações: `done`, gate reprovado com evidência, ou pergunta que só o usuário responde. "Checkpoint pronto" anunciado como entrega é a falha de condução nº 1 desta pipeline — se precisar encerrar a sessão no meio, poste o output do `status` e diga explicitamente "run INCOMPLETA em <estágio>".
- **Retomada**: execução interrompida (sub-agente que morreu, sessão cortada) se retoma com `status <slug>` — ele diz exatamente o que falta; continue dali. Nunca recomece do zero se o run.json existe.
- O `--env` gravado no `new` é imutável e é o único ambiente permitido em todos os comandos da run.

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

### 3. Candidatos de design

Cada candidato recebe: o `brief.md` completo + [`DESIGN.md`](./DESIGN.md) como instrução + **uma família estética distinta** (você atribui — 3 famílias diferentes de `skills/gp2-html-designer/references/aesthetic-families.md`, coerentes com o tom do brief; com referência visual anexada, os 3 herdam a referência mas variam a interpretação). Produz: `artifacts/bt/<slug>/candidates/<A|B|C>/strip.html` + `template.html` (fatiado via `slice-strip.js`) + `strip.png` + `screenshots/` + `design-notes.md`.

**Modo de execução (na ordem de preferência do runtime):**
1. Sub-agentes em paralelo, SE o runtime tem delegação confiável.
2. **Sequencial na própria sessão** (A, depois B, depois C) — mais lento e sempre funciona. Se um sub-agente morrer sem deixar `candidates/<X>/` completo, NÃO re-delegue: execute aquele candidato você mesmo, sequencialmente.

Candidato que falhar não derruba o batch — o judge decide entre os que entregaram (≥1 obrigatório; `advance` avisa se ficou abaixo do alvo N).

### 4. Julgamento

**Antes de julgar, gere as flags de procedência R1** (determinístico, você mesmo):

```bash
grep -l "professional-photo-[12]" artifacts/bt/<slug>/candidates/*/template.html
```

Candidato com slot de pessoa: match = `procedência: canônico`; sem match = `procedência: outro`. Passe a flag por candidato como insumo do judge.

Preferência: **1 sub-agent em contexto limpo** com [`JUDGE.md`](./JUDGE.md), recebendo só screenshots anonimizados (A/B/C) + **flags de procedência R1** + storyline + rubrica + exemplares. **Fallback (delegação indisponível/falhou 1×):** julgue na própria sessão seguindo o JUDGE.md à risca — abra SOMENTE os screenshots e strip.png (não releia design-notes/HTML dos candidatos) e registre no report `judge: same-session (fallback)`. Julgamento imperfeito e registrado > pipeline morta. Produz `judge-report.md` com: vencedor, scores, blockers técnicos e **top-3 fixes**.

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

- **Conhecimento é estado da fábrica — sincronize via git**: no INÍCIO de toda run/certificação, `git pull --rebase`. Ao FINAL (e sempre que escrever dossiê, lesson ou score), commit + push **apenas dos caminhos de conhecimento**: `bt/knowledge/`, `bt/evals/lessons.md`, `bt/evals/scores.jsonl`, `bt/styles/*/lessons.md` e artefatos de certificação de estilo (`bt/styles/<slug>/`). Mensagem curta (ex: `knowledge: dossiê laserterapia atualizado`). NUNCA commite `artifacts/` nem mudanças em regras/skills sem pedido do Gustavo. Conflito em arquivo append-only (lessons/scores) → resolva mantendo as duas linhas. Sem isso, cada runtime (OpenClaw, Hermes) acumula conhecimento divergente no próprio clone.
- **Ambiente é mecânico, não narrativo**: o ambiente pedido pelo usuário vira `--env <x>` literal em TODO comando (resolve_tenant, generate-image, uploader) e aparece no cabeçalho do relatório. Pedido "dev" + qualquer comando sem `--env dev` = bug seu. NUNCA suba pra prod quando o pedido diz dev — na dúvida, dev.

- Nunca pule o judge, mesmo com N=1 (com 1 candidato ele vira gate de qualidade + blockers técnicos).
- Nunca publique candidato reprovado, abaixo da barra (total <30 ou craft <6) ou sem os fixes aplicados.
- Storyline sem os 5 beats → volte ao passo 2, não siga.
- Após publicar, anexe o score do vencedor em `bt/evals/scores.jsonl` (ver `evals/README.md`).
- Mudou qualquer arquivo de `bt/`? Rode a regressão de `evals/` antes do próximo batch de produção.
