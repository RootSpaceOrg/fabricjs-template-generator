---
name: gp2-pipeline
description: "Orchestrator da Pipeline GetPosts v2. Roda em sequência: gp2-request-interpreter → gp2-art-director → gp2-html-designer (3 passos materializados v1-lowfi → v2-midfi → final) → gp2-html-reviewer → gp2-template-marker → gp2-template-converter → gp2-template-uploader. Aplica iteration policy, suporta roteamento retroativo designer↔art-director (status: blocked-on-art-director, máx 2 ciclos), e bloqueia upload sem delight detail ou com archetype/move silenciosamente divergente. Pipeline agnóstica a vertical. Suporta ambientes dev e prod (default: prod). Use sempre que o usuário pedir para criar um template de social media de ponta a ponta."
---

# gp2-pipeline

Orchestrator oficial da Pipeline GetPosts v2.

## Quando usar

Sempre que o usuário pedir para criar um template de social media completo (post, carrossel, story) e quiser ele publicado no editor. Frases-gatilho:

- "cria um carrossel sobre…"
- "faz um post para [qualquer vertical]…"
- "gera um template de…"
- "publica como draft…"

## Sequência oficial

```
1. gp2-request-interpreter          → brief.md (conteúdo/intenção; em reference-driven mode, marca que há referência visual)
2. gp2-art-director                 → visual-plan.md (paleta com hexs, escala tipográfica resolvida, arquétipo A* por slide [_shared/COMPOSITIONS.md], 1-2 moves M* [_shared/CAROUSEL_MOVES.md], mapeamento data-variable; em reference-driven mode, extrai o vocabulário visual completo da referência)
3. gp2-html-designer                → template-v1-lowfi.html → template-v2-midfi.html → template.html (3 entregáveis materializados com auto-critique entre passos; pode reportar status: blocked-on-art-director para gancho retroativo)
4. gp2-html-reviewer                → PASS|REVISE|FAIL (gate técnico + archetype/move/typography fidelity + reference fidelity + delight detail)
5. gp2-template-marker              → template.html marcado + template-summary.md
6. gp2-template-converter           → slide-N.json + manifest.json (emite ClippableImage cru → roda scripts/center-clippable-images.js para centralizar via natural size → self-validation pós-emissão)
7. gp2-template-uploader            → upload S3 + Supabase
8. Relatório consolidado
```

## Iteration policy

| Etapa | Loop interno | Loop externo (orquestrador) |
|-------|--------------|----------------------------|
| Art-director | — | reexecuta se plano estiver incompleto (raro); roteamento retroativo de designer (ver abaixo) |
| Designer (low/mid/high-fi) | 3 passos fixos; refaz 1× cada passo se auto-critique falhar. Cada passo produz `template-vN.html` + screenshots e seu `## Passo N — critique` em `notes.md` | — |
| HTML reviewer | — | máx 2 revisões antes de FAIL; recebe os 3 conjuntos do designer (v1-lowfi, v2-midfi, final) para detectar regressões; se reviewer apontar problema de plano → volta ao art-director |
| Marker audit | — | máx 2 fixes antes de escalar |
| Converter (self-validation) | — | máx 2 fixes antes de escalar |

Ao exceder qualquer teto, pare e reporte:

```
[blocked] gate: <nome>
last error: <descrição>
artifacts: <lista de paths>
```

### Roteamento retroativo (designer → art-director)

O designer pode reportar `status: blocked-on-art-director` quando encontra ambiguidade no `visual-plan.md` que trava a execução (arquétipo incompatível com copy, contraste impossível, move M* que não cabe). Quando isso acontece:

1. Pause o fluxo linear (não avance para reviewer).
2. Re-invoque `gp2-art-director` em **modo de resposta** passando: `visual-plan.md`, `notes.md` do designer (com seção `## Pedidos ao art-director`), screenshots parciais do passo onde o designer parou.
3. Art-director responde fazendo patch cirúrgico no `visual-plan.md` (válidos) ou adicionando `## Resposta art-director` no `notes.md` do designer (inválidos).
4. Retome `gp2-html-designer` no **passo onde parou** (não volte ao Passo 1).
5. **Máx 2 ciclos** designer↔art-director por template. Ao exceder: `[blocked] gate: art-director-loop` e escale ao usuário.

Esse loop é o equivalente ao "diálogo retroativo" do Claude Design — use com parcimônia.

## Gates obrigatórios para upload

Upload **só** acontece quando todos abaixo são verdadeiros:

- `gp2-art-director` produziu `visual-plan.md` completo (família, paleta, plano de slides, movimento memorável, mapeamento data-variable; em reference-driven mode, inclui vocabulário visual extraído da referência);
- `gp2-html-reviewer.status === "PASS"` (findings técnicos críticos = 0; fidelidade ao plano: faithful ou partial com divergências documentadas; execução: adequada ou forte);
- `gp2-template-marker` audit: `PASS`;
- `gp2-template-converter`: `scripts/center-clippable-images.js` exit 0 (todas as `ClippableImage` centralizadas via natural size) + `scripts/validate-slides.js` exit 0 + self-validation pós-emissão sem criticals;
- nenhuma incompatibilidade catastrófica conhecida com o editor.

Se algum falha:
- Em casos seguros (mecânicos, óbvios), revise automaticamente dentro do loop.
- Em casos que precisam de decisão criativa do usuário, pergunte. Não invente direção.
- Se o HTML reviewer apontar `planFidelity: "diverged"` com divergências não documentadas → devolva ao designer com instrução específica (não ao art-director, a menos que o plano seja o problema).

## Standing rule

Quando os gates passam, suba **automaticamente** com:

- `template_type: ai`
- `status: review` (default do uploader — humano aprova depois na tela de revisão; **nunca** passe `--status draft`)
- `owner_user_id: templateGenerator`
- `scope: platform`
- `business_type: ""` (sempre vazio — direcionamento por nicho acontece em outra camada)
- ambiente: **prod** (default, a não ser que o usuário peça dev)

Não pergunte confirmação — é a regra padrão.

## Comando de upload

```bash
python skills/gp2-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "<Nome do Template>" \
  --tags "<tag1,tag2>" \
  --description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)" \
  --execute
```

> `business_type` é sempre vazio (template neutro em relação a nicho) e o status default é `review`. Não passe `--business-type` nem `--status draft`.

Para dev, adicione `--env dev`. Sem flag = prod.

Use sempre `--description-hint` apontando para o `template-summary.md` produzido pelo marker. Consulte `skills/gp2-template-uploader/SKILL.md` para detalhes de dry-run, blockers e checklist.

**Nunca exiba secrets em log.** Senha sempre via env var.

## Batch (vários templates)

Quando o usuário pede N templates de uma vez:

- spawn um sub-agent isolado por template (use Agent tool com `subagent_type: general-purpose`);
- dê a cada sub-agent só o pedido específico + esta SKILL.md;
- mantenha pastas de artifacts separadas (`artifacts/<stage>/<slug-1>/`, `<slug-2>/`, ...);
- consolide IDs e evidências ao final.

## Evidência a reportar

Por template processado:

- template ID (do Supabase);
- nome;
- contagem de slides;
- art-director: família estética + composições usadas (A1–A8 por slide);
- HTML reviewer status + findings técnicos + fidelidade ao plano + data-variable cobertura;
- marker audit status;
- converter validator status (exit code);
- upload status;
- pasta de artifacts;
- paths de evidência (screenshots, visual-plan.md, html-review.md, `template-summary.md`).

## Estrutura de artifacts esperada

```
artifacts/
├── gp2-request-interpreter/<slug>/
│   └── brief.md               ← conteúdo/intenção (sem reference-spec.md — análise visual migrou para art-director)
├── gp2-art-director/<slug>/
│   └── visual-plan.md         ← paleta, tipografia resolvida, arquétipos A*, moves M*, data-variable; em reference-driven inclui vocabulário visual da referência. Pode conter §"Histórico de revisões" após resposta a pedidos do designer.
├── gp2-html-designer/<slug>/
│   ├── template-v1-lowfi.html       ← Passo 1
│   ├── screenshots-v1-lowfi/
│   ├── template-v2-midfi.html       ← Passo 2
│   ├── screenshots-v2-midfi/
│   ├── template.html                ← Passo 3 (final)
│   ├── screenshots/
│   └── notes.md                     ← 3 critiques + decisões + desvios; opcional §"Pedidos ao art-director" / §"Resposta art-director"
├── gp2-template-marker/<slug>/
│   ├── template.html (marcado)
│   ├── marker-audit.json/.md
│   └── template-summary.md
└── gp2-template-converter/<slug>/
    ├── output/slide-N.json
    ├── manifest.json
    └── conversion-report.md
```

## Política de qualidade

- **Não suba template sem delight detail**. Se o reviewer reporta `delightDetails: []`, devolva ao designer pedindo aplicação de ao menos 1 detalhe (tracking notável, contraste de peso, número decorativo, color block intencional, fio tipográfico, sobreposição calculada). Templates sem delight detail são publicáveis tecnicamente mas indistinguíveis de IA default.
- **Não aceite divergência silenciosa de arquétipo/move**. Se `archetypeFidelity.verdict == "diverged"` ou `moveExecution.verdict == "missing"` sem documentação em `notes.md`, é REVISE.
- **Não suba template com design fraco**, mesmo que todos os gates técnicos passem. Se você (orquestrador) olhar para os screenshots high-fi do designer e perceber que está medíocre, devolva ao designer com instrução clara em vez de prosseguir.
- **Não force secondary brand color** quando o brief decidiu por primária somente.
- **Não invente skills** que não estão na lista oficial. A v2 tem 7 skills de execução (`gp2-request-interpreter`, `gp2-art-director`, `gp2-html-designer`, `gp2-html-reviewer`, `gp2-template-marker`, `gp2-template-converter`, `gp2-template-uploader`) + 2 orquestradores (`gp2-pipeline` e `gp2-template-suggester`). Se você sente falta de uma 10ª, é provavelmente cerimônia.
- **Não pule o art-director** mesmo que o pedido pareça simples. Sem visual-plan.md, o designer cai de volta no modo v1 (viés de repetição, cores sem papel explícito, data-variable descobertos pelo marker, sem arquétipos/moves declarados).
- **Não pule passos do designer**. Os 3 entregáveis (v1-lowfi, v2-midfi, final) com critique entre eles são o que faz a v2 entregar qualidade Claude Design. Designer que entrega só `template.html` está operando no modo v1.

## Resposta final por template

```markdown
## Template: <nome>

- **ID:** <Supabase template ID>
- **Slides:** <N>
- **Artifact:** `artifacts/.../<slug>/`

### Direção criativa (art-director)
- Paleta: primary `<hex>` / secondary `<hex>`
- Tipografia: <display> + <body>
- Arquétipos: slide1=<A?>, slide2=<A?>, ... (diversidade: <N> tipos distintos)
- Carousel moves: <M?, M?>
- data-variable mapeados: <N> elementos

### Gates
- Art-director: PASS (visual-plan.md completo)
- HTML reviewer: PASS (técnicos: 0, archetypeFidelity: tight, moveExecution: complete, typography: tight, delight: <N> details, reference: <tight|n/a>)
- Marker audit: PASS
- Converter validator: PASS (exit 0)
- Upload: OK
- Thumbnails: OK

```

Em batch, consolide todos os blocos com totais ao final.
