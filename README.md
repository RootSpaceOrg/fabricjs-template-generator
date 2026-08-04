# Fábrica de templates

Fábrica de templates da plataforma (mkt-platform): motor sem estética (design
system fechado + conversor determinístico + runner com gates) + packs de design
certificados. Arquitetura: [ARCHITECTURE.md](ARCHITECTURE.md). Criar packs:
[PACKS.md](PACKS.md). Gatilho de agente:
[skills/template-factory/SKILL.md](skills/template-factory/SKILL.md).
O que não está nos documentos não existe.

## Peças

| Peça | Arquivo | Papel |
|------|---------|-------|
| Interface | `engine/design-system.css` + `engine/CATALOG.md` | componentes ds-*, grid 12×12, contrato agente↔conversor |
| Conversor | `engine/convert.js` | HTML conforme → Fabric JSON, sem consulta; violação rejeita apontando `data-el-id` |
| Assembler | `engine/assemble.js` | slides isolados → strip.html/png + slide-N.png |
| Runner | `engine/run.py` | estados + gates que EXECUTAM validação; estado em `artifacts/runs/<slug>/run.json` |
| Packs | `packs/<slug>/` | pack.json (tokens/fit) + recipes/ + images.md + reference.png + lessons.md |

## Fluxo de uma run

```
python engine/run.py new <slug> --env dev --pack clean-numbered-editorial --n 8
# resolve  → engine/tools/resolve_tenant.py > resolve.json
# context  → dossie.md (CONTEXT.md)
# compose  → draw.json (sorteio de recipes) + slides/slide-N.html (CATALOG.md §Recipes→HTML)
# render   → node engine/assemble.js artifacts/runs/<slug>/slides
# convert  → node engine/convert.js artifacts/runs/<slug>/slides artifacts/runs/<slug>/output --slug <slug>
# judge    → judge-report.md (JUDGE.md; strip.png é o objeto julgado)
# finalize → fidelity.md (VEREDITO: FIEL)
# upload   → engine/tools/upload.py → set <slug> template_id <id>
python engine/run.py advance <slug>   # entre cada estágio; gates negam avanço incompleto
```

Leis (ver ARCHITECTURE §5): doutrina do conversor (JSON nunca se edita), lei de
conservação `data-el-id`↔`elId` (conferida no convert E no runner), env
imutável, judge ancorado na reference.png do pack, lessons por pack.

## Setup local

[SETUP.md](SETUP.md). Credenciais AWS para upload: `.env` apontado por
`SECRETS_DIR`.

## Estado

- Motor v1 funcional (smoke: `artifacts/runs/_smoke/` — item-a convertido e
  validado por `engine/tools/validate-slides.js`).
- Pack 1 `clean-numbered-editorial` v1 em `status: draft` — **aguarda
  certificação com aprovação do Gustavo** (corredor completo 1×). Só depois a
  fábrica liga.
- Fora da v1 (adicionar quando doer): costura de watermark cross-slide no
  assembler; formatos ≠1080×1350; slicer próprio (slides já nascem isolados).
