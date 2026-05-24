# GetPosts Pipeline v2 — HTML → Fabric.js para HealthMarket

Pipeline de produção de templates HealthMarket (Instagram feed/stories/carrossel) que parte de um pedido em linguagem natural e termina com um template publicado no editor, com qualidade de design comparável ao Claude Design e migração determinística para Fabric.js.

Substitui a pipeline v1 em `../getposts-skills-20260513T181951Z/skills/`. Convive lado a lado durante a transição. O uploader v1 é reaproveitado tal qual.

## Por que existe

A v1 entrega o fluxo ponta-a-ponta (incluindo upload/thumbnails), mas o design final fica visivelmente abaixo do Claude Design. Causa raiz: o `getposts-html-designer` da v1 desenha "às cegas" a partir de um brief textual. A v2 explicita o loop de design renderizado (3 passos: low-fi → mid-fi → high-fi) dentro da própria skill de design — mesmo mecanismo que faz Claude Design funcionar bem, agora dentro do openclaw.

A forma da pipeline foi preservada (gates múltiplos, marker pós-design separado, uploader atual reaproveitado), porque a auditoria confirmou que o problema não era estrutural, era estar concentrado em uma única etapa.

## Skills, em ordem

| Ordem | Skill | Função | Output principal |
|-------|-------|--------|------------------|
| 1 | `gp2-request-interpreter` | Lê o pedido + referências e produz brief enxuto. | `brief.md` |
| 2 | `gp2-html-designer` | Gera HTML em **3 iterações com render** (low-fi → mid-fi → high-fi). | `template.html` + `screenshots/` |
| 3 | `gp2-html-reviewer` | Critica os screenshots. Hard-gate só em findings técnicos. | `html-review.json` + status |
| 4 | `gp2-template-marker` | Marca `data-*` (absorve o antigo context-analyzer). | `template.html` marcado + `template-summary.md` |
| 5 | `gp2-template-converter` | HTML marcado → `slide-N.json` Fabric. | `output/<slug>/slide-N.json` + `manifest.json` |
| 6 | `gp2-template-result-reviewer` | Compara HTML × Fabric JSON. | `review-report.json` + status |
| 7 | `getposts-template-uploader` (**delegado para v1**) | Upload S3 + Supabase + thumbnails. | template ID |
| 8 | `gp2-pipeline` | Orchestrator que roda tudo na ordem. | Relatório consolidado |

O uploader não é recriado — a pipeline v2 invoca a skill v1 (`getposts-template-uploader`) diretamente porque ela já funciona e está em produção.

## Standing rule do Gustavo

Quando todos os gates passam, o upload acontece automaticamente com:

- `template_type: ai`
- `status: review` (humano aprova depois via tela de revisão de templates)
- `owner_user_id: templateGenerator`
- `scope: platform`
- `business_type: ""` (sempre vazio)

Em seguida o editor é aberto para salvar e gerar thumbnails.

## Contrato HTML → Fabric

O HTML produzido pela v2 segue **exatamente** o mesmo contrato do Claude Design: [`CLAUDE_DESIGN_RULES.md`](../claude_design_to_fabric/CLAUDE_DESIGN_RULES.md). Isso significa:

- HTML da v2 é convertível pelo agent `claude-design-to-fabricjs-converter` da Estratégia A.
- HTML do Claude Design (Estratégia A) é convertível pela v2 sem mudanças.
- O validador `scripts/validate-slides.js` é uma cópia do validador da Estratégia A.

Veja [`CONTRACT.md`](./CONTRACT.md) para o resumo. Veja [`DESIGN_PRINCIPLES.md`](./DESIGN_PRINCIPLES.md) para o protocolo de 3 renders.

## Estrutura

```
getposts-pipeline-v2/
├── README.md                    ← este arquivo
├── DESIGN_PRINCIPLES.md         ← protocolo das 3 iterações renderizadas
├── CONTRACT.md                  ← contrato HTML que garante migração 100%
├── scripts/
│   ├── validate-slides.js       ← validador Fabric JSON (cópia da Estratégia A)
│   ├── audit-template-markup.py ← validador dos data-* no marker
│   └── render-html-screenshots.js ← helper headless para designer e reviewer
└── skills/
    ├── gp2-pipeline/
    ├── gp2-request-interpreter/
    ├── gp2-html-designer/
    │   └── references/aesthetic-families.md
    ├── gp2-html-reviewer/
    ├── gp2-template-marker/
    ├── gp2-template-converter/
    └── gp2-template-result-reviewer/
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
| Designer interno (3 passos low/mid/high-fi) | fixos, não conta como loop |
| HTML reviewer | 2 revisões |
| Marker audit | 2 fixes |
| Converter validator | 2 fixes |
| Result reviewer | 2 fixes |
| Editor save/thumbnails | 1 retry |

Após o teto, a pipeline para e reporta o gate que falhou com evidências.

## Validação ponta-a-ponta

1. Rode `node scripts/validate-slides.js artifacts/gp2-template-converter/<slug>/` — exit code 0.
2. Importe o JSON no editor HealthMarket (`Frontend/healthmarket-frontend/app`, `npm run start`), abra a aba **Brand**, troque entre 2-3 presets de cor: todos os elementos com `data-variable` devem trocar via `updateTemplateColors`.
3. Rode `gp2-pipeline` em 1 template, confirme o ID retornado, abra no editor e clique "Salvar Alterações" para confirmar a thumbnail.
