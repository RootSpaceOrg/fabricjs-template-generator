# HTML → Fabric.js Contract

A pipeline v2 produz HTML que migra deterministicamente para Fabric.js no editor da plataforma. Toda a especificação vive dentro deste repositório — a pipeline é autocontida.

## Fonte de verdade

Os documentos autoritativos vivem em [`skills/_shared/`](./skills/_shared/):

- [`skills/_shared/HTML_TECHNICAL_SPEC.md`](./skills/_shared/HTML_TECHNICAL_SPEC.md) — regras estruturais do HTML, tabela de `data-*`, anti-patterns, verificações estruturais.
- [`skills/_shared/GRADIENT_SYSTEM.md`](./skills/_shared/GRADIENT_SYSTEM.md) — presets de `data-darken`/`data-glow`, fallback `data-gradient`, emissão Fabric.
- [`skills/_shared/COMPOSITIONS.md`](./skills/_shared/COMPOSITIONS.md) — arquétipos A1–A8 usados pelo art-director.
- [`skills/_shared/CAROUSEL_MOVES.md`](./skills/_shared/CAROUSEL_MOVES.md) — moves M* do art-director.

Toda regra de markup do `gp2-html-designer`, `gp2-template-marker` e `gp2-template-converter` aponta para essas specs. Não duplique regras nas SKILLs individuais — só referencie. Quando o contrato evoluir, ele evolui em um único lugar.

## Resumo do que o contrato exige

| Aspecto | Regra |
|---------|-------|
| Estrutura | `<section class="slide" data-width data-height>` por slide |
| Posicionamento | `position: absolute` com `left/top/width/height` em px para tudo no canvas |
| Cor de marca | `data-variable="primary\|secondary"` (+ `data-variable-target` opcional) |
| Imagens | uma `<img>` por região; `data-image-type="brandLogo\|professionalPhoto\|userAsset"` |
| Texto multiestilo | `<span>` por trecho com estilo distinto |
| Formas | `<div>` com `border-radius` para retângulos arredondados; `<svg>` para vetores |
| Estilo | Todo CSS inline nos elementos (`style="..."`). Proibido `<style>` blocks com classes |
| Gradientes | `linear-gradient(...)` inline + `data-gradient` JSON obrigatório. `data-variable-stops="primary,secondary"` quando aplicável |
| Fontes | `<meta name="hm-fonts" content="...">` listando todas |
| Segmento | `<html data-segment="...">` (um dos segmentos suportados pela plataforma) |
| Elementos AI-fillable | `data-template-element`, `data-te-description`, `data-te-max-chars` etc. |
| Variáveis de perfil | `data-text-type="instagramHandle\|instagramName\|phone\|address"` |
| Estáticos | `data-static="true"` |

## Validadores que enforçam o contrato

- **`scripts/audit-template-markup.py`** — confere os `data-*` no HTML marcado (estrutura semântica). Roda dentro do `gp2-template-marker`.
- **`scripts/validate-slides.js`** — confere o Fabric JSON emitido (tipos, campos, gradientes, variable configs, ClippableImage etc.). Roda dentro do `gp2-template-converter` (self-validation pós-emissão).

Os dois validadores são autoritativos. Status `PASS` em ambos = HTML válido e Fabric JSON pronto para o editor.

## Onde o contrato pode mudar

Mudanças no contrato (novos `data-*`, novos tipos de objeto Fabric, novos validadores) acontecem em **três lugares simultaneamente, todos dentro deste repositório**:

1. `skills/_shared/HTML_TECHNICAL_SPEC.md` e/ou `skills/_shared/GRADIENT_SYSTEM.md` (especificação).
2. `scripts/validate-slides.js` (validador do Fabric JSON) e/ou `scripts/audit-template-markup.py` (auditor do HTML marcado).
3. `skills/gp2-template-converter/SKILL.md` (mapeamento HTML → Fabric) e/ou `skills/gp2-template-marker/SKILL.md` (regras de marcação).
