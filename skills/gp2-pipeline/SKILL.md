---
name: gp2-pipeline
description: "Orchestrator da Pipeline GetPosts v2. Roda em sequência: gp2-request-interpreter → gp2-html-designer → gp2-html-reviewer → gp2-template-marker → gp2-template-converter → gp2-template-result-reviewer → getposts-template-uploader (delegado para v1) → editor save/thumbnails. Aplica iteration policy, decide quando seguir/refazer/escalar, e consolida evidências. Use sempre que o usuário pedir para criar um template HealthMarket de ponta a ponta."
---

# gp2-pipeline

Orchestrator oficial da Pipeline GetPosts v2.

## Quando usar

Sempre que o usuário pedir para criar um template HealthMarket completo (post, carrossel, story) e quiser ele publicado no editor. Frases-gatilho:

- "cria um carrossel sobre…"
- "faz um post para clínica de…"
- "gera um template de…"
- "publica como draft…"

## Sequência oficial

```
1. gp2-request-interpreter          → brief.md
2. gp2-html-designer                 → template.html (3 renders: low/mid/high-fi)
3. gp2-html-reviewer                 → PASS|REVISE|FAIL (Impeccable separado: técnico vs estilístico)
4. gp2-template-marker               → template.html marcado + template-summary.md
5. gp2-template-converter            → slide-N.json + manifest.json
6. gp2-template-result-reviewer      → PASS|PASS_WITH_WARNINGS|FAIL
7. getposts-template-uploader (v1)   → upload S3 + Supabase
8. editor save/thumbnails            → via flag --execute --generate-thumbnails do uploader
9. Relatório consolidado
```

A skill `getposts-template-uploader` da pipeline v1 é **reaproveitada tal qual** — não recriada. Ela já funciona em produção e gera thumbnails via editor save.

## Iteration policy

| Etapa | Loop interno | Loop externo (orquestrador) |
|-------|--------------|----------------------------|
| Designer (low/mid/high-fi) | passos fixos; refaz 1× cada passo se auto-check falhar | — |
| HTML reviewer | — | máx 2 revisões antes de FAIL |
| Marker audit | — | máx 2 fixes antes de escalar |
| Converter validator | — | máx 2 fixes antes de escalar |
| Result reviewer | — | máx 2 fixes (devolvidos ao converter) |
| Editor save/thumbnails | — | 1 retry após reload/login |

Ao exceder qualquer teto, pare e reporte:

```
[blocked] gate: <nome>
last error: <descrição>
artifacts: <lista de paths>
```

## Gates obrigatórios para upload

Upload **só** acontece quando todos abaixo são verdadeiros:

- `gp2-html-reviewer.status === "PASS"` (findings técnicos = 0; estilísticos podem ter `intentional: true`);
- `gp2-template-marker` audit: `PASS`;
- `gp2-template-converter` validator (`validate-slides.js`): exit 0;
- `gp2-template-result-reviewer.status` ∈ {`PASS`, `PASS_WITH_WARNINGS`};
- nenhuma incompatibilidade catastrófica conhecida com o editor.

Se algum falha:
- Em casos seguros (mecânicos, óbvios), revise automaticamente dentro do loop.
- Em casos que precisam de decisão criativa do usuário, pergunte. Não invente direção.

## Standing rule do Gustavo

Quando os gates passam, suba **automaticamente** com:

- `template_type: ai`
- `status: draft`
- `user_id: public`

Em seguida, abra o editor (via `--execute --generate-thumbnails` do uploader) e clique "Salvar Alterações" para gerar thumbnails. Não pergunte confirmação — é a regra padrão.

## Comando de upload (delegado para uploader v1)

```bash
GETPOSTS_EDITOR_PASSWORD='<password>' \
python /root/.openclaw/workspace/skills/getposts-template-uploader/scripts/import-template.py \
  artifacts/gp2-template-converter/<slug>/ \
  --name "<Nome do Template>" \
  --business-type multi-nicho \
  --tags "<tag1,tag2>" \
  --description-hint "$(cat artifacts/gp2-template-marker/<slug>/template-summary.md)" \
  --status draft \
  --user-id public \
  --execute \
  --generate-thumbnails
```

Use sempre `--description-hint` apontando para o `template-summary.md` produzido pelo marker (substitui o `context-analysis.json` da v1).

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
- HTML reviewer status + contagem de findings (técnicos vs estilísticos);
- marker audit status;
- converter validator status (exit code);
- result reviewer status;
- upload status;
- thumbnail/editor save status;
- pasta de artifacts;
- paths de evidência (screenshots, relatórios, `template-summary.md`).

## Estrutura de artifacts esperada

```
artifacts/
├── gp2-request-interpreter/<slug>/brief.md
├── gp2-html-designer/<slug>/
│   ├── template.html
│   ├── template-v1.html, template-v2.html
│   ├── screenshots/
│   └── notes.md
├── gp2-template-marker/<slug>/
│   ├── template.html (marcado)
│   ├── marker-audit.json/.md
│   └── template-summary.md
├── gp2-template-converter/<slug>/
│   ├── output/slide-N.json
│   ├── manifest.json
│   └── conversion-report.md
└── gp2-template-result-reviewer/<slug>/
    ├── review-report.json/.md
    └── (opcional) review/html|product|diff/slide-N.png
```

## Política de qualidade

- **Não suba template com design fraco**, mesmo que todos os gates técnicos passem. Se você (orquestrador) olhar para os screenshots high-fi do designer e perceber que está medíocre, devolva ao designer com instrução clara em vez de prosseguir.
- **Não force secondary brand color** quando o brief decidiu por primária somente.
- **Não invente skills** que não estão na lista oficial. A v2 tem 7 skills. Se você sente falta de uma 8ª, é provavelmente cerimônia (foi essa lição que fundiu o context-analyzer no marker).

## Resposta final por template

```markdown
## Template: <nome>

- **ID:** <Supabase template ID>
- **Slides:** <N>
- **Artifact:** `artifacts/.../<slug>/`

### Gates
- HTML reviewer: PASS (técnicos: 0, estilísticos: 2 intencionais)
- Marker audit: PASS
- Converter validator: PASS (exit 0)
- Result reviewer: PASS_WITH_WARNINGS (warnings: 1)
- Upload: OK
- Thumbnails: OK

### Evidências
- `artifacts/gp2-html-designer/<slug>/screenshots/`
- `artifacts/gp2-template-result-reviewer/<slug>/review-report.md`
- `artifacts/gp2-template-marker/<slug>/template-summary.md`
```

Em batch, consolide todos os blocos com totais ao final.
