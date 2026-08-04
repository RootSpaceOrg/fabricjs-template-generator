# bt/ — Business Template Pipeline

Pipeline de templates **finais, específicos de negócio** (`template_type: userReady`), separada da pipeline genérica (`skills/gp2-*`, que permanece intocada).

Gatilho: a skill fina [`skills/gp2-business-template/SKILL.md`](../skills/gp2-business-template/SKILL.md) aponta para cá.

## Mapa

| Arquivo | Papel |
|---------|-------|
| [`PIPELINE.md`](./PIPELINE.md) | Orquestrador: resolve → contexto → N candidatos → judge → finaliza → publica |
| [`styles/`](./styles/README.md) | **A fábrica**: estilos certificados (blueprint pré-anotado + tokens + receitas) — geração determinística por estilo; alvo 20–30 estilos |
| [`CONTEXT.md`](./CONTEXT.md) | Cérebro de copy: dossiê por business_type, funil, storyline (espinha narrativa) |
| [`DESIGN.md`](./DESIGN.md) | Um candidato de design: direção de arte + HTML em 3 renders, composição autoral |
| [`JUDGE.md`](./JUDGE.md) | Juiz independente (pairwise, rubrica, exemplares) + eval harness de regressão |
| [`FINALIZE.md`](./FINALIZE.md) | Imagens geradas, marcação, conversão Fabric, upload |
| `references/rubric.md` | Rubrica visual do judge |
| `references/compliance/` | Regras de conselho profissional **curadas por humano** |
| `evals/` | Golden set + prompts fixos de regressão + histórico de scores |
| `knowledge/` | Dossiês por business_type (30 dias de validade) |
| `scripts/` | `run.py` (runner com estado — TODA execução passa por ele), `resolve_tenant.py`, `generate-image.py`, `slice-strip.js`, `svg_assets.py`, `aws_auth.py` |

## O que é reusado da pipeline genérica (não duplicar)

- Contrato técnico HTML→Fabric: `skills/_shared/HTML_TECHNICAL_SPEC.md` + `GRADIENT_SYSTEM.md`
- Marcação/descrições: `skills/gp2-template-marker/`
- Conversão + validação: `skills/gp2-template-converter/` + `scripts/validate-slides.js` + `scripts/center-clippable-images.js`
- Upload: `skills/gp2-template-uploader/scripts/import-template.py`
- Render headless: `scripts/render-html-screenshots.js`

## Princípios desta pipeline

1. **Best-of-N no modo livre** (3 candidatos + juiz pairwise); **N=1 + judge QA no modo estilo certificado** — a estrutura já foi julgada na certificação. Nunca single-shot SEM judge.
1b. **Precedência**: onde um documento reusado da pipeline genérica (DESIGN_PRINCIPLES, skills gp2-*) conflitar com um arquivo de `bt/`, **o de `bt/` vence** — os reusados são maquinaria/protocolo base, não autoridade de regra.
2. **Juiz ≠ autor**: o judge roda em contexto limpo, com rubrica e exemplares, comparação pairwise com troca de posição. Se o runtime permitir, modelo de outra família.
3. **Eval-driven**: toda mudança nestes arquivos roda a regressão de `evals/` antes de valer.
4. **Grounding**: copy nasce do dossiê; compliance nasce de fonte curada, não de pesquisa do modelo.
5. **Autonomia medida**: `status: review` sempre — humano aprova; motivos de rejeição voltam para `evals/lessons.md`.
6. **Doutrina do conversor (norte, definido pelo Gustavo)**: o agente é DESIGNER, nunca conversor. Ele desenha dentro de um design system com regras duras e limitações explícitas (whitelist de elementos/CSS permitidos — tudo fora dela é proibido, não "desaconselhado"). Um script determinístico converte qualquer HTML que siga as regras em Fabric JSON **sem consultar o agente** — posicionamento, cor, tipografia: tudo sai dos computed styles, nunca de transcrição. HTML que viola a whitelist é REJEITADO pelo conversor com erro apontando o elemento — a correção é sempre regenerar o HTML (e a lição vira regra/lesson), jamais editar o JSON na mão. Estado atual: transição — `fix-fabric-fills.js` + lei de conservação são os embriões; o `convert.js` completo substitui a emissão manual do FINALIZE §3 quando construído (teste de ouro: artifacts da certificação r3).
