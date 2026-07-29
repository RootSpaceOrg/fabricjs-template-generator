# bt/ — Business Template Pipeline

Pipeline de templates **finais, específicos de negócio** (`template_type: userReady`), separada da pipeline genérica (`skills/gp2-*`, que permanece intocada).

Gatilho: a skill fina [`skills/gp2-business-template/SKILL.md`](../skills/gp2-business-template/SKILL.md) aponta para cá.

## Mapa

| Arquivo | Papel |
|---------|-------|
| [`PIPELINE.md`](./PIPELINE.md) | Orquestrador: resolve → contexto → N candidatos → judge → finaliza → publica |
| [`CONTEXT.md`](./CONTEXT.md) | Cérebro de copy: dossiê por business_type, funil, storyline (espinha narrativa) |
| [`DESIGN.md`](./DESIGN.md) | Um candidato de design: direção de arte + HTML em 3 renders, composição autoral |
| [`JUDGE.md`](./JUDGE.md) | Juiz independente (pairwise, rubrica, exemplares) + eval harness de regressão |
| [`FINALIZE.md`](./FINALIZE.md) | Imagens geradas, marcação, conversão Fabric, upload |
| `references/rubric.md` | Rubrica visual do judge |
| `references/compliance/` | Regras de conselho profissional **curadas por humano** |
| `evals/` | Golden set + prompts fixos de regressão + histórico de scores |
| `knowledge/` | Dossiês por business_type (30 dias de validade) |
| `scripts/` | `resolve_tenant.py`, `generate-image.py`, `aws_auth.py` |

## O que é reusado da pipeline genérica (não duplicar)

- Contrato técnico HTML→Fabric: `skills/_shared/HTML_TECHNICAL_SPEC.md` + `GRADIENT_SYSTEM.md`
- Marcação/descrições: `skills/gp2-template-marker/`
- Conversão + validação: `skills/gp2-template-converter/` + `scripts/validate-slides.js` + `scripts/center-clippable-images.js`
- Upload: `skills/gp2-template-uploader/scripts/import-template.py`
- Render headless: `scripts/render-html-screenshots.js`

## Princípios desta pipeline

1. **Best-of-N**: 3 candidatos de design independentes por pedido; um juiz escolhe. Nunca single-shot.
2. **Juiz ≠ autor**: o judge roda em contexto limpo, com rubrica e exemplares, comparação pairwise com troca de posição. Se o runtime permitir, modelo de outra família.
3. **Eval-driven**: toda mudança nestes arquivos roda a regressão de `evals/` antes de valer.
4. **Grounding**: copy nasce do dossiê; compliance nasce de fonte curada, não de pesquisa do modelo.
5. **Autonomia medida**: `status: review` sempre — humano aprova; motivos de rejeição voltam para `evals/lessons.md`.
