---
name: gp2-html-reviewer
description: "Critique do HTML produzido por gp2-html-designer antes do marker. Mantém o gate Impeccable, mas separa findings em técnicos (hard-gate, REVISE) e estilísticos (warning, podem passar com justificativa). Use após gp2-html-designer, antes de gp2-template-marker. Não gera HTML, não converte Fabric, não publica."
---

# gp2-html-reviewer

Critica o `template.html` final do designer (Passo 3 high-fi) antes de seguir para o marker.

## Mudança política importante (vs v1)

A v1 tratava qualquer warning Impeccable como `REVISE` obrigatório. Isso forçava revisões que diluíam a intenção do designer (Impeccable detectava "looks like SaaS template" e o designer tinha que ceder mesmo sabendo que o estilo era intencional).

A v2 separa findings em **duas categorias**:

| Categoria | Exemplos | Tratamento |
|-----------|----------|------------|
| **Técnicos** | overflow real, contraste WCAG < 4.5, texto cortado, imagem ausente, texto fora do canvas, sobreposição não-intencional, slide vazio, fonte ausente do `<meta hm-fonts>` | **HARD-GATE** → status `REVISE` |
| **Estilísticos** | Impeccable "looks SaaS", "centered too much", "card spam", "generic typography", densidade decorativa | **WARNING** → reviewer pode aprovar se justificar por escrito (campo `intentional` no relatório) |

Findings estilísticos válidos viram lições para revisões futuras, não bloqueios. Findings técnicos sempre bloqueiam.

## Inputs

```
artifacts/gp2-html-designer/<slug>/
├── template.html          ← high-fi final
├── screenshots/slide-N.png
└── notes.md               ← decisões do designer (família estética, movimento memorável)
```

Se faltar screenshots, renderize antes:

```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/
```

## Workflow

1. Leia `notes.md` para entender as escolhas conscientes do designer.
2. **Detecte o modo:** verifique se `artifacts/gp2-request-interpreter/<slug>/reference-spec.md` existe. Se sim, é reference-driven — você precisa checar aderência ao spec além das checagens normais.
3. Rode o preflight determinístico:

```bash
python3 ../../scripts/review-html-design.py artifacts/gp2-html-designer/<slug>/
```

Esse script gera `html-review.json` + `html-review.md` e roda o gate Impeccable internamente.

4. Inspecione visualmente cada `screenshots/slide-N.png`.
5. Classifique cada finding como **técnico**, **estilístico**, ou **aderência ao spec** (só reference-driven).
6. Para findings estilísticos, decida (com justificativa) se são intencionais — leia `notes.md` para entender. Ex: se o designer comprometeu-se com "Bold educacional" e Impeccable acusou "tipografia muito pesada", a justificativa é que o peso é a assinatura da família escolhida.
7. **Em reference-driven mode:** compare screenshots × `reference-spec.md`. Acuse drift como finding técnico se:
   - Hexs aplicados não batem com a paleta declarada (tolerância: ΔE > 10 entre cor aplicada e cor do spec).
   - Família tipográfica usada está em categoria diferente da declarada (ex: spec pediu serifa display, designer usou sans).
   - Movimento memorável declarado não está visível.
   - Elementos editoriais listados no spec estão ausentes.
   - Se o designer divergiu **e** documentou em `notes.md` (ex: "Bebas Neue indisponível, usei Anton"), trate como warning, não bloqueio.
8. Decida o status final:

| Status | Quando |
|--------|--------|
| `PASS` | zero findings técnicos. Findings estilísticos não-bloqueantes podem existir desde que justificados em `intentional`. |
| `REVISE` | qualquer finding técnico. Pode incluir findings estilísticos que **não** se justificam pelas escolhas do designer. |
| `FAIL` | direção do design é fundamentalmente fraca; volte ao `gp2-html-designer` (ou ao interpreter, se o brief estava errado). |

Nunca devolva `PASS_WITH_WARNINGS` — `PASS` aceita warnings justificados; `REVISE` aceita reabertura.

## Categorização de findings (referência)

### Técnicos (sempre HARD-GATE)

- Texto fora do canvas (left/top + width/height ultrapassa data-width/height).
- Sobreposição não-intencional entre conteúdo e conteúdo (texto sobre texto, foto sobre título).
- Contraste WCAG AA < 4.5:1 para body, < 3.0:1 para títulos grandes (>= 24pt).
- Texto cortado (overflow vertical dentro do `<p>`/`<h*>`).
- `<img>` sem `src` ou com `src` quebrado.
- Slide sem conteúdo principal identificável.
- Fonte usada no CSS ausente do `<meta name="hm-fonts">`.
- Placeholder de imagem complexo (texto, anatomia, ícones) — viola CLAUDE_DESIGN_RULES seção 6.
- Pseudo-elementos `::before`/`::after`, `@keyframes`, `mix-blend-mode`, `backdrop-filter` complexo.
- Posicionamento via flex/grid dentro de `.slide` (deveria ser absoluto).
- `<section class="slide">` sem `data-width` / `data-height`.
- `<img data-image-type="professionalPhoto">` (ou `class="professional-photo"`) com `object-fit: cover` ou `border-radius` arredondado quando o brief não pediu avatar circular — perde o efeito do cutout PNG e quebra o anchor `bottom-center` do runtime. Esperado: `object-fit: contain; object-position: bottom center; border-radius: 0;` (ver [`gp2-html-designer/references/professional-photo-placements.md`](../gp2-html-designer/references/professional-photo-placements.md)).
- `<img data-image-type="professionalPhoto">` posicionada de forma que a face da figura (zona superior do slot, ~30% da altura) é coberta por texto ou outro elemento visível — leitor não consegue avaliar confiança.

### Aderência ao spec (somente reference-driven, HARD-GATE quando não documentado em notes.md)

- Hexs aplicados não batem com paleta declarada (ΔE > 10 sem documentação).
- Família tipográfica em categoria diferente da declarada (serifa ↔ sans, condensada ↔ regular) sem documentação.
- Movimento memorável declarado ausente do design.
- Elementos editoriais listados no spec ausentes (eyebrow numerado faltando, fios horizontais ausentes, etc.).
- Tratamento de foto profissional difere do spec (spec pediu retangular editorial, designer usou avatar circular).

### Estilísticos (warning, justificável)

- "Generic AI template" / "looks like SaaS".
- "Tudo centralizado".
- "Card spam" / "nested cards".
- "Tipografia genérica" (Impeccable acusa quando você usa só Inter).
- "Cores muito saturadas" / "muito sutis".
- "Decoração excessiva" / "desert design" (vazio demais).
- "Movimento memorável ausente".
- "Slides muito similares" (rítmo de carrossel fraco).

Se `notes.md` justifica a escolha (ex: "Brutalist direto pede peso e saturação"), o reviewer aceita como `intentional` e mantém `PASS`.

## Output

Sobrescreva `html-review.json` com a classificação, incluindo o campo `intentional`:

```json
{
  "status": "PASS|REVISE|FAIL",
  "technicalFindings": [
    { "slide": 1, "issue": "...", "severity": "blocker", "fix": "..." }
  ],
  "styleFindings": [
    { "slide": 0, "issue": "Generic SaaS look", "intentional": true,
      "reason": "Designer chose Premium Minimal — restraint is the point" }
  ],
  "impeccable": { "rawFindings": [...], "promotedToTechnical": [], "promotedToStyle": [...] }
}
```

E `html-review.md` para humanos:

```markdown
# Revisão HTML — <slug>

**Status:** PASS|REVISE|FAIL

## Findings técnicos (bloqueantes)
- Slide 2: título sai 30px do canvas direito → reduzir width do `<h1>` para 960px ou font-size para 88px.

## Findings estilísticos (não-bloqueantes)
- Impeccable: "centered too much" — INTENCIONAL: família "Premium minimal" pede simetria silenciosa.

## Próximo passo
- PASS → gp2-template-marker
- REVISE → gp2-html-designer com lista acima
- FAIL → reabrir brief com gp2-request-interpreter
```

## Loop de revisão

Máximo **2 revisões**. Após o segundo `REVISE` ainda falhar, devolva `FAIL` e escale para o orquestrador anotar bloqueio.

## Resposta final ao orquestrador

```markdown
Revisão HTML: PASS|REVISE|FAIL
Artifact: <path>
Findings técnicos: <N>
Findings estilísticos: <N> (sendo <M> intencionais)
Evidência: <path>/html-review.md
Próximo passo: gp2-template-marker | gp2-html-designer (revisão) | gp2-request-interpreter (fail)
```

## O que esta skill NÃO faz

- Não gera HTML novo. Apenas critica.
- Não aplica correções; produz lista para o designer.
- Não roda o validador Fabric (`validate-slides.js`) — esse é o `gp2-template-converter`.
- Não decide se o template tem mercado/funcionalidade — só visual + estrutural.
