# GetPosts Pipeline v2 — HTML → Fabric.js para HealthMarket

Pipeline de produção de templates HealthMarket (Instagram feed/stories/carrossel) que parte de um pedido em linguagem natural e termina com um template publicado no editor, com qualidade de design comparável ao Claude Design e migração determinística para Fabric.js.

Substitui a pipeline v1 em `../getposts-skills-20260513T181951Z/skills/`. Convive lado a lado durante a transição. O uploader v1 é reaproveitado tal qual.

## Por que existe

A v1 entrega o fluxo ponta-a-ponta (incluindo upload/thumbnails), mas o design final fica visivelmente abaixo do Claude Design. Causa raiz: o `getposts-html-designer` da v1 desenha "às cegas" a partir de um brief textual. A v2 explicita o loop de design renderizado (3 passos: low-fi → mid-fi → high-fi) dentro da própria skill de design — mesmo mecanismo que faz Claude Design funcionar bem, agora dentro do openclaw.

A forma da pipeline foi preservada (gates múltiplos, marker pós-design separado, uploader atual reaproveitado), porque a auditoria confirmou que o problema não era estrutural, era estar concentrado em uma única etapa.

## Setup local

Para rodar a pipeline localmente (Linux, VPS ou Windows): veja [`SETUP.md`](./SETUP.md) — passo-a-passo cross-OS com comandos de validação por etapa.

Resumo rápido:

```bash
pip install -r requirements.txt
npm install
npx playwright install chromium
```

## Skills, em ordem

| Ordem | Skill | Função | Output principal |
|-------|-------|--------|------------------|
| 1 | `gp2-request-interpreter` | Lê o pedido + referências e produz brief enxuto. | `brief.md` |
| 2 | `gp2-art-director` | Decide família estética, paleta, composição por slide, movimento, mapeamento `data-variable`. | `visual-plan.md` |
| 3 | `gp2-html-designer` | Gera HTML em **3 iterações com render** (low-fi → mid-fi → high-fi) executando o visual-plan. | `template.html` + `screenshots/` |
| 4 | `gp2-html-reviewer` | Critica os screenshots (técnico + fidelidade ao plano). Hard-gate em findings técnicos. | `html-review.json` + status |
| 5 | `gp2-template-marker` | Marca `data-*` (absorve o antigo context-analyzer) + emite `template-summary.md`. | `template.html` marcado + `template-summary.md` |
| 6 | `gp2-template-converter` | HTML marcado → `slide-N.json` Fabric. Emite `ClippableImage` cru e roda `scripts/center-clippable-images.js` para centralizar via natural size (espelha `ClippableImage.replaceImage()` do editor). Self-validation pós-emissão. | `output/<slug>/slide-N.json` + `manifest.json` |
| 7 | `gp2-template-uploader` | Upload S3 + invoca `app-lambda-template-handler` (Supabase + embedding). | template ID |
| — | `gp2-pipeline` | Orchestrator que roda tudo na ordem com iteration policy. | Relatório consolidado |
| — | `gp2-template-suggester` | Orquestrador alternativo: gera N prompts autônomos para catálogo e dispara `gp2-pipeline` por sub-agente. | N templates publicados |

> O step v1 `gp2-template-result-reviewer` foi removido — os checks úteis foram absorvidos pelo `gp2-template-converter` como self-validation pós-emissão. O script `scripts/review-fabric-json.py` continua disponível para debug standalone.

## Standing rule do Gustavo

Quando todos os gates passam, o upload acontece automaticamente com:

- `template_type: ai`
- `status: review` (humano aprova depois via tela de revisão de templates)
- `owner_user_id: templateGenerator`
- `scope: platform`
- `business_type: ""` (sempre vazio)

Em seguida o editor é aberto para salvar e gerar thumbnails.

## Contrato HTML → Fabric

A pipeline v2 é autocontida. O contrato HTML → Fabric vive em:

- [`skills/_shared/HTML_TECHNICAL_SPEC.md`](./skills/_shared/HTML_TECHNICAL_SPEC.md) — regras estruturais, tabela de `data-*`, anti-patterns.
- [`skills/_shared/GRADIENT_SYSTEM.md`](./skills/_shared/GRADIENT_SYSTEM.md) — sistema de gradientes (`data-darken` / `data-glow` / `data-gradient`).
- [`CONTRACT.md`](./CONTRACT.md) — resumo high-level e mapa dos validadores.
- [`DESIGN_PRINCIPLES.md`](./DESIGN_PRINCIPLES.md) — protocolo de 3 renders do designer.

O validador `scripts/validate-slides.js` é a fonte de verdade do Fabric JSON emitido; `scripts/audit-template-markup.py` audita o HTML marcado. PASS em ambos = pronto para o editor.

## Estrutura

```
getposts-pipeline-v2/
├── README.md                    ← este arquivo
├── DESIGN_PRINCIPLES.md         ← protocolo das 3 iterações renderizadas
├── CONTRACT.md                  ← contrato HTML que garante migração 100%
├── scripts/
│   ├── validate-slides.js          ← validador Fabric JSON
│   ├── audit-template-markup.py    ← validador dos data-* no marker
│   ├── center-clippable-images.js  ← pós-processo do converter: centraliza ClippableImage via natural size (espelha replaceImage do editor)
│   └── render-html-screenshots.js  ← helper headless para designer e reviewer
└── skills/
    ├── _shared/                    ← specs cross-skill (gradient system, HTML technical spec)
    ├── gp2-pipeline/
    ├── gp2-template-suggester/
    ├── gp2-request-interpreter/
    ├── gp2-art-director/
    ├── gp2-html-designer/
    │   └── references/             ← aesthetic-families, professional-photo-placements
    ├── gp2-html-reviewer/
    ├── gp2-template-marker/
    │   └── references/element-descriptions.md
    ├── gp2-template-converter/
    └── gp2-template-uploader/
        └── scripts/                ← import-template.py, save-template-in-editor.js
```

## Como usar (openclaw)

Peça ao openclaw:

```
Rode gp2-pipeline com este pedido: "<seu pedido em linguagem natural>"
[opcional: anexe imagens de referência]
```

O orchestrator (`gp2-pipeline`) chama cada skill em sequência, aplica a política de loops e reporta status no final.

Para rodar uma skill isolada (útil para iterar só no design):

```
Rode gp2-html-designer com este brief: <conteúdo de brief.md>
```

## Política de iteração

| Etapa | Loop máx |
|-------|----------|
| Art-director | reexecuta se plano incompleto (raro) |
| Designer interno (3 passos low/mid/high-fi) | fixos; 1 retry por passo se auto-check falhar |
| HTML reviewer | 2 revisões |
| Marker audit | 2 fixes |
| Converter self-validation | 2 fixes |

Após o teto, a pipeline para e reporta o gate que falhou com evidências.

## Validação ponta-a-ponta

1. Rode `node scripts/validate-slides.js artifacts/gp2-template-converter/<slug>/` — exit code 0.
2. Importe o JSON no editor HealthMarket (`Frontend/healthmarket-frontend/app`, `npm run start`), abra a aba **Brand**, troque entre 2-3 presets de cor: todos os elementos com `data-variable` devem trocar via `updateTemplateColors`.
3. Rode `gp2-pipeline` em 1 template, confirme o ID retornado, abra no editor e clique "Salvar Alterações" para confirmar a thumbnail.
