# HTML → Fabric.js Contract

A pipeline v2 produz HTML que respeita o mesmo contrato do Claude Design (Estratégia A). Isto garante migração determinística para Fabric.js no editor HealthMarket.

## Fonte de verdade

[`../claude_design_to_fabric/CLAUDE_DESIGN_RULES.md`](../claude_design_to_fabric/CLAUDE_DESIGN_RULES.md) é o documento autoritativo. Toda regra de markup do `gp2-html-designer` e do `gp2-template-marker` aponta para ele.

Não duplique regras aqui — só referencie. Quando o contrato evoluir, ele evolui em um único lugar.

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
| Segmento | `<html data-segment="...">` (um dos 8 segmentos HealthMarket) |
| Elementos AI-fillable | `data-template-element`, `data-te-description`, `data-te-max-chars` etc. |
| Variáveis de perfil | `data-text-type="instagramHandle\|instagramName\|phone\|address"` |
| Estáticos | `data-static="true"` |

## Validadores que enforçam o contrato

- **`scripts/audit-template-markup.py`** — confere os `data-*` no HTML marcado (estrutura semântica). Roda dentro do `gp2-template-marker`.
- **`scripts/validate-slides.js`** — confere o Fabric JSON emitido (tipos, campos, gradientes, variable configs, ClippableImage etc.). Roda dentro do `gp2-template-converter` e do `gp2-template-result-reviewer`.

Os dois validadores são autoritativos. Status `PASS` em ambos = HTML válido e Fabric JSON pronto para o editor.

## Intercambialidade com a Estratégia A

Por seguirem o mesmo contrato:

1. HTML emitido pela v2 pode ser convertido com o agent `claude-design-to-fabricjs-converter` (Estratégia A) sem mudanças.
2. HTML emitido pelo Claude Design (Estratégia A) pode ser marcado e convertido pela v2 sem mudanças.
3. O mesmo `validate-slides.js` valida ambos.

Isto é por design: o objetivo é nunca depender exclusivamente de uma fonte de design.

## Onde o contrato pode mudar

Mudanças no contrato (novos `data-*`, novos tipos de objeto Fabric, novos validadores) acontecem em **três lugares simultaneamente**:

1. `claude_design_to_fabric/CLAUDE_DESIGN_RULES.md` (especificação).
2. `claude_design_to_fabric/validate-slides.js` + `getposts-pipeline-v2/scripts/validate-slides.js` (validador — manter as cópias em sincronia).
3. `claude_design_to_fabric/skill.md` + skill do converter da v2 (mapeamento).

Qualquer mudança que afete o editor HealthMarket também precisa refletir em `Frontend/healthmarket-frontend/app/src/app/shared/fabricjs-editor/core/types.ts` e `utilities/colors.ts`.
