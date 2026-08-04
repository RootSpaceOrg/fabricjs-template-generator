# GP3 — fábrica de templates

Arquitetura: [ARCHITECTURE.md](ARCHITECTURE.md). Motor sem estética + packs de
design acopláveis. O que não está lá não existe.

## Peças

| Peça | Arquivo | Papel |
|------|---------|-------|
| Interface | `engine/design-system.css` + `engine/CATALOG.md` | componentes ds-*, grid 12×12, contrato agente↔conversor |
| Conversor | `engine/convert.js` | HTML conforme → Fabric JSON, sem consulta; violação rejeita apontando `data-el-id` |
| Assembler | `engine/assemble.js` | slides isolados → strip.html/png + slide-N.png |
| Runner | `engine/run.py` | estados + gates que EXECUTAM validação; estado em `artifacts/gp3/<slug>/run.json` |
| Packs | `packs/<slug>/` | pack.json (tokens/fit) + recipes/ + images.md + reference.png + lessons.md |

## Fluxo de uma run

```
python gp3/engine/run.py new <slug> --env dev --pack clean-numbered-editorial --n 8
# resolve  → bt/scripts/resolve_tenant.py > resolve.json
# context  → dossie.md (bt/CONTEXT.md continua válido)
# compose  → draw.json (sorteio de recipes) + slides/slide-N.html (CATALOG.md §Recipes→HTML)
# render   → node gp3/engine/assemble.js artifacts/gp3/<slug>/slides
# convert  → node gp3/engine/convert.js artifacts/gp3/<slug>/slides artifacts/gp3/<slug>/output --slug <slug>
# judge    → judge-report.md (bt/JUDGE.md adaptado; strip.png é o objeto julgado)
# finalize → fidelity.md (VEREDITO: FIEL)
# upload   → bt/scripts/upload.py → set <slug> template_id <id>
python gp3/engine/run.py advance <slug>   # entre cada estágio; gates negam avanço incompleto
```

Leis herdadas do bt (ver ARCHITECTURE §5): doutrina do conversor (JSON nunca se
edita), lei de conservação `data-el-id`↔`btElId` (conferida no convert E no
runner), env imutável, judge com golden set, lessons por pack.

## Estado

- Motor v1 funcional (smoke: `artifacts/gp3/_smoke/` — item-a convertido e
  validado por `scripts/validate-slides.js`).
- Pack 1 `clean-numbered-editorial` v1 em `status: draft` — **aguarda
  certificação com aprovação do Gustavo** (corredor completo 1×). Só depois a
  fábrica liga e o fluxo bt aposenta.
- Fora da v1 (adicionar quando doer): costura de watermark cross-slide no
  assembler; formatos ≠1080×1350; slicer próprio (slides já nascem isolados).
