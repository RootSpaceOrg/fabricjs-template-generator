# Fábrica de templates

Fábrica de templates da plataforma (mkt-platform): motor sem estética (design
system fechado + conversor determinístico + runner com gates) + packs de design
como **conhecimento de estilo**. Arquitetura: [ARCHITECTURE.md](ARCHITECTURE.md).
Criar packs: [PACKS.md](PACKS.md). Gatilho de agente:
[skills/template-factory/SKILL.md](skills/template-factory/SKILL.md).
O que não está nos documentos não existe.

## Papéis

| Papel | Quem | Conhecimento |
|-------|------|--------------|
| Copy specialist | LLM | [CONTEXT.md](CONTEXT.md) (geral) + `knowledge/copy/negocios/<business>.md` |
| Designer | LLM | `knowledge/design/geral.md` + `packs/<slug>/` (tecnicas, exemplos, tokens, lessons) |
| Todo o resto | scripts | conversão, render, validação, resolve, upload — zero interpretação |

## Peças

| Peça | Arquivo | Papel |
|------|---------|-------|
| Interface | `engine/design-system.css` + `engine/CATALOG.md` | componentes ds-*, grid 12×12 por slide + `.fita-layer` de travessias, contrato designer↔conversor |
| Conversor | `engine/convert.js` | fita.html → Fabric JSON por slide; travessia emitida nos 2 vizinhos (off-canvas clipado); violação rejeita apontando `data-el-id` |
| Assembler | `engine/assemble.js` | fita.html → strip.png + slide-N.png |
| Runner | `engine/run.py` | estados + gates que EXECUTAM validação; estado em `artifacts/runs/<slug>/run.json` |
| Packs | `packs/<slug>/` | pack.json (tokens/fit) + tecnicas.md + exemplos/ + images.md + reference.png + lessons.md |

## Fluxo de uma run

```
python engine/run.py new <slug> --env dev --pack <pack> --n 6
# resolve  → engine/tools/resolve_tenant.py > resolve.json
# context  → dossie.md (copy specialist — CONTEXT.md + knowledge/copy/)
# compose  → fita.html (designer — CATALOG.md + knowledge/design/ + pack)
# render   → node engine/assemble.js artifacts/runs/<slug>
# convert  → node engine/convert.js artifacts/runs/<slug> artifacts/runs/<slug>/output --slug <slug>
# judge    → judge-report.md (JUDGE.md; strip.png é o objeto julgado)
# finalize → fidelity.md (VEREDITO: FIEL)
# upload   → engine/tools/upload.py → set <slug> template_id <id>
python engine/run.py advance <slug>   # entre cada estágio; gates negam avanço incompleto
```

Leis (ver ARCHITECTURE §5): doutrina do conversor (JSON nunca se edita), lei de
conservação `data-el-id`↔`elId` (conferida no convert E no runner), env
imutável, judge ancorado na reference.png do pack, lessons por pack, variância
entre gerações do mesmo pack é dever do designer.

## Setup local

[SETUP.md](SETUP.md). Credenciais AWS para upload: `.env` apontado por
`SECRETS_DIR`.

## Estado

- Motor fita-v2 funcional (smoke: `artifacts/runs/_fita-smoke/` — travessias
  emitidas nos 2 vizinhos com offset exato, validadas).
- Pack 1 `clinical-photo-editorial` v5 em `status: draft` — baseline visual
  aprovado (fita v26); aguarda certificação v2 (prova real com variância).
