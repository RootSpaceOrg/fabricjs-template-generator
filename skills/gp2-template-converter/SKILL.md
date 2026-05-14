---
name: gp2-template-converter
description: "Converte HTML marcado (do gp2-template-marker) em Fabric.js CanvasJSON pronto para o editor HealthMarket. Adota CLAUDE_DESIGN_RULES.md como contrato e roda validate-slides.js (mesma cópia da Estratégia A) como gate. HTML produzido pela v2 é 100% intercambiável com HTML do Claude Design. Use após gp2-template-marker (audit PASS), antes de gp2-template-result-reviewer."
---

# gp2-template-converter

Migra `template.html` marcado para uma série de `slide-N.json` Fabric.js — um por `<section class="slide">`. Output validado por `validate-slides.js`, o **mesmo** validador usado pela Estratégia A (`Pocs/claude_design_to_fabric/`).

## Contrato

A spec completa de mapeamento HTML → Fabric vive em [`../../../claude_design_to_fabric/CLAUDE_DESIGN_RULES.md`](../../../claude_design_to_fabric/CLAUDE_DESIGN_RULES.md) (autoritativo) e [`../../../claude_design_to_fabric/skill.md`](../../../claude_design_to_fabric/skill.md) (mapeamento detalhado). Este SKILL.md sumariza só o essencial. Quando em dúvida, leia o contrato.

Por que isso é crítico:
- HTML produzido pela pipeline v2 segue **exatamente** o mesmo formato do Claude Design.
- O validador (`scripts/validate-slides.js`) é cópia byte-a-byte do validador da Estratégia A.
- Você pode até converter HTML da v2 com o agent `claude-design-to-fabricjs-converter` (Estratégia A) e vice-versa.

## Inputs

```
artifacts/gp2-template-marker/<slug>/
├── template.html          ← marcado, audit PASS
├── marker-audit.json      ← status PASS
├── template-summary.md
└── screenshots/           ← do designer, ainda válido
```

E `marker-audit.json.status === "PASS"`.

## Output

```
artifacts/gp2-template-converter/<slug>/
├── output/
│   ├── slide-1.json
│   ├── slide-2.json
│   └── slide-N.json
├── manifest.json
└── conversion-report.md
```

## Conversion contract (essencial)

Toda regra abaixo está detalhada em `CLAUDE_DESIGN_RULES.md` e `claude_design_to_fabric/skill.md`. Reúno aqui só os erros mais comuns que travam validador/editor:

| Regra | Detalhe |
|-------|---------|
| Versão | `version: "5.5.2"` no root |
| Sem groups | `objects` é array flat — Fabric groups quebram round-trip |
| Sem `rect` | use **sempre** `roundedRect` (cantos `0` quando sem radius). Plain `rect` quebra deserialize com gradiente |
| Origem | todo objeto: `originX: "center"`, `originY: "center"` |
| Conversão de coords | HTML top-left → Fabric center: `left = htmlLeft + width/2`, `top = htmlTop + height/2` |
| Nomes | todo objeto tem `name` (rótulo PT-BR, ver tabela em `claude_design_to_fabric/skill.md` §Object Naming) |
| Textbox | sempre `styles: {}` (mesmo vazio); sem `styles` quebra Fabric |
| `lineHeight` | clampado a >= 1.0 (Fabric 5.x renderiza < 1.0 inconsistente) |
| `charSpacing` | clampado a >= -150 (abaixo, texto colapsa) |
| `text-transform` | aplicado direto na string (`text.toUpperCase()`); **não emita `textTransform`** |
| Cores brand | `data-variable="primary\|secondary"` → `fillVariableConfig`/`strokeVariableConfig`/`backgroundVariableConfig` `{type:"solid", variable, alpha}` |
| Background brand | `<section data-variable="primary" data-variable-target="background">` → root `backgroundVariableConfig` |
| Spans | inline `<span>` em texto editável → **uma** textbox com `styles[lineIndex][charIndex]`; **nunca** uma textbox por span |
| Profile vars | `data-text-type` → `textType: "..."` no objeto, sem `isTemplateElement` |
| Templates | `data-template-element="true"` → `isTemplateElement: true` + bloco `templateElement` |
| Imagens cropadas (cover) | `data-image-crop="true"` ou `border-radius != 0` ou `object-fit:cover` → `ClippableImage` com crop centrado |
| Imagens cutout (contain) | `object-fit:contain` em `data-image-type="professionalPhoto"` → `ClippableImage` **sem crop** + `originY:"bottom"` quando `object-position` inclui `bottom` (ver seção dedicada abaixo) |
| Gradientes | `type: "linear"\|"radial"` (NUNCA `linearGradient`); inclui `coords`, `colorStops`, `offsetX`, `offsetY`, `gradientUnits: "percentage"`, `gradientTransform: null` |
| Background gradiente | emitido como objeto Fabric gradient, NUNCA string `"linear-gradient(...)"` |

## ClippableImage crop (CRÍTICO)

Para qualquer `<img>` com `border-radius`, `object-fit: cover`, ou `data-image-crop="true"`:

1. Use a caixa do HTML como **frame visual** (`visualWidth`, `visualHeight`).
2. Carregue dimensões naturais da imagem (`naturalW`, `naturalH`) → vira `originWidth`, `originHeight`.
3. Calcule centered cover crop:

```js
const objectAspect = visualWidth / visualHeight;
const imageAspect = naturalW / naturalH;
let cropW, cropH;
if (imageAspect > objectAspect) {
  cropH = naturalH;
  cropW = cropH * objectAspect;
} else {
  cropW = naturalW;
  cropH = cropW / objectAspect;
}
const cropX = (naturalW - cropW) / 2;
const cropY = (naturalH - cropH) / 2;
const scale = visualWidth / cropW;
```

4. Emita:

```json
{
  "type": "ClippableImage",
  "name": "Foto",
  "originWidth": naturalW,
  "originHeight": naturalH,
  "cropX": cropX,
  "cropY": cropY,
  "width": cropW,
  "height": cropH,
  "scaleX": scale,
  "scaleY": scale,
  "left": htmlLeft + visualWidth / 2,
  "top": htmlTop + visualHeight / 2,
  "originX": "center", "originY": "center",
  "src": "<URL absoluta>",
  "crossOrigin": "anonymous",
  "imageType": "professionalPhoto|userAsset|brandLogo",
  "topLeft": <0..100>, "topRight": <0..100>, "bottomRight": <0..100>, "bottomLeft": <0..100>
}
```

`width`/`height` são as dimensões do crop **na fonte original**, NÃO o frame visual. O frame visível é `width * scaleX` por `height * scaleY`.

## ClippableImage cutout — `object-fit: contain` (CRÍTICO para `professionalPhoto`)

**Quando aplicar:** `<img>` com `object-fit: contain` (default da pipeline v2 para `data-image-type="professionalPhoto"` — ver `gp2-html-designer/references/professional-photo-placements.md`). O PNG é cutout transparente e a figura inteira deve aparecer dentro do slot, ancorada na borda escolhida via `object-position`.

**A diferença em uma frase:** em `cover` o frame é o slot e a imagem é cropada para preencher; em `contain` o frame é a própria imagem natural e o slot apenas restringe a área onde ela cabe — sem crop.

**Anti-pattern observado em produção:** emitir cutout como se fosse cover (frame = slot, `originWidth/Height` inventados a partir do slot). O placeholder renderiza a figura distorcida ou ocupando metade do slot, e quando o usuário sobe a foto real o `image-variable.ts:84-94` calcula scale com base nas dimensões erradas e arruina o resultado. **Sintoma típico:** `originWidth/originHeight = 1200/1800` (proporção do slot) quando o PNG cutout fonte é ~700×900 (proporção 0.78). A figura aparece ancorada no topo cobrindo só metade do slot.

**Algoritmo correto:**

```js
// 1. Dimensões NATURAIS do PNG (não do slot!).
//    Para placeholders base64, use ImageBitmap/Image API para ler.
const naturalW = imgEl.naturalWidth;   // ex: 700
const naturalH = imgEl.naturalHeight;  // ex: 900

// 2. Slot do HTML (apenas usado para posicionar; NÃO vira originW/H)
const slotW = parsePx(style.width);    // ex: 1200
const slotH = parsePx(style.height);   // ex: 2365.71
const slotL = parsePx(style.left);
const slotT = parsePx(style.top);

// 3. Scale "contain": preserva aspect ratio do PNG dentro do slot
const scale = Math.min(slotW / naturalW, slotH / naturalH);

// 4. Resolver object-position
//    Padrão da pipeline v2: "bottom center"
const objPos = style.objectPosition || 'center center';
const anchorY = objPos.includes('bottom') ? 'bottom'
              : objPos.includes('top')    ? 'top'
              : 'center';
const anchorX = objPos.includes('right') ? 'right'
              : objPos.includes('left')  ? 'left'
              : 'center';

// 5. Calcular left/top em coords Fabric (com originX/Y já considerado)
//    Fabric: left/top é o ponto de origin; com originY:"bottom" o top é a borda inferior visual.
const cx = slotL + slotW / 2;                    // centro horizontal do slot
const topByAnchor = anchorY === 'bottom' ? slotT + slotH
                   : anchorY === 'top'   ? slotT
                   : slotT + slotH / 2;
const fabricOriginY = anchorY === 'bottom' ? 'bottom'
                     : anchorY === 'top'    ? 'top'
                     : 'center';
```

**JSON emitido:**

```json
{
  "type": "ClippableImage",
  "name": "Foto profissional",
  "imageType": "professionalPhoto",
  "isTemplateElement": true,
  "templateElement": {
    "description": "<descrição do marker>",
    "removeBackground": false
  },

  "originWidth":  700,    // ← naturalW do PNG, NÃO do slot
  "originHeight": 900,    // ← naturalH do PNG, NÃO do slot
  "width":        700,    // ← idem (não há crop em contain)
  "height":       900,    // ← idem
  "cropX": 0, "cropY": 0,

  "scaleX": 0.857,        // ← Math.min(slotW/700, slotH/900)
  "scaleY": 0.857,        // ← idem (mesmo valor — preserva ratio)

  "left": 660,            // ← centro horizontal do slot
  "top":  3270.71,        // ← borda inferior do slot (slotT + slotH)
  "originX": "center",
  "originY": "bottom",    // ← chave! reflete object-position: bottom

  "topLeft": 0, "topRight": 0, "bottomRight": 0, "bottomLeft": 0,
  "src": "data:image/png;base64,...",
  "crossOrigin": "anonymous"
}
```

**Por que isso funciona em produção:**

- `originWidth/Height` reflete o PNG real → quando o usuário sobe a foto e o runtime executa `Math.min(maxOriginalWidth/newWidth, maxOriginalHeight/newHeight)` (`image-variable.ts:84`), os ratios batem e a foto entra com escala correta.
- `originY: "bottom"` faz a figura ancorar no rodapé do slot, espelhando o anchor `bottom-center` do runtime para `professionalPhoto`. A face fica na zona superior, sem distorção.
- `width === originWidth` e `cropX/Y = 0` indicam ao Fabric que **não há crop** — toda a textura PNG é desenhada.

**Tabela de exceção da regra geral de origin:**

A regra "todo objeto: `originX: "center"`, `originY: "center"`" aplica-se a todos os tipos exceto `ClippableImage` cutout, que usa `originY: "bottom"` (ou `"top"`) conforme `object-position` do HTML. O validador (`validate-slides.js`) já aceita `originY` ≠ `"center"` para imagens; só textboxes/shapes são forçados a center/center.

**Avatar circular (exceção da exceção):** quando `professionalPhoto` é avatar circular (`border-radius: 50%; object-fit: cover`), volta para a regra de cover acima — usa crop centrado, frame = slot, `originX/Y: "center"`.

## Workflow

1. Confirme inputs prontos: `template.html` marcado existe, `marker-audit.json.status === "PASS"`.
2. Crie `artifacts/gp2-template-converter/<slug>/output/`.
3. Para cada `<section class="slide">`, parse e emita `slide-N.json`:
   - Walk DOM em order (z-order).
   - Calcule coordenadas absolute → Fabric center.
   - Aplique tabela de mapeamento HTML → Fabric (`claude_design_to_fabric/skill.md` §Element Type Mapping).
   - Detecte cores brand (explícitas via `data-variable` ou auto-detect).
   - Emita gradient configs corretos.
   - Para textboxes com `<span>`, calcule `styles[lineIndex][charIndex]` contando caracteres exatos (sem aproximar).
   - Adicione `name` PT-BR descritivo a cada objeto.
4. Escreva `manifest.json`:

```json
{
  "templateName": "<nome>",
  "slug": "<slug>",
  "segment": "<segmento>",
  "convertedAt": "<ISO datetime>",
  "slides": [
    { "file": "slide-1.json", "width": 1080, "height": 1350 }
  ],
  "fonts": ["Inter", "Playfair Display"],
  "detectedColors": { "primary": "#4285F4", "secondary": "#FF6B6B" },
  "warnings": []
}
```

5. Rode o validador:

```bash
node ../../scripts/validate-slides.js artifacts/gp2-template-converter/<slug>/output/
```

6. Para cada erro, leia o slide ofensor, corrija com Edit, salve. Loop máximo: **2 fixes**.
7. Quando o validador retornar exit `0`, escreva `conversion-report.md` resumindo.

## Validate-and-fix loop

Tabela de erros e fixes em [`../../../claude_design_to_fabric/skill.md`](../../../claude_design_to_fabric/skill.md) §Validate-and-Fix Loop. Os comuns:

| Erro | Fix |
|------|-----|
| `missing or empty "name"` | adicione `"name": "<rótulo PT-BR>"` |
| `textbox is missing "styles"` | adicione `"styles": {}` |
| `lineHeight X is below 1.0` | clampe para `1.0` |
| `originX/Y must be "center"` | corrija |
| `ClippableImage missing "originWidth"` etc. | adicione campo, recalcule crop |
| `roundedRect corner X must be 0–100` | recalcule percentual |
| `variable must be "primary"\|"secondary"` | corrija valor |
| `charSpacing X is below -150` | clampe para `-150` |
| `CSS gradient string … is not valid` | substitua por objeto Fabric gradient |
| `gradient type must be "linear" or "radial"` | corrija e adicione campos faltantes |

## O que NÃO fazer

- Não degrade o design do HTML para "facilitar" conversão. Se o HTML está bom e o Fabric está errado, conserte o conversor, não o HTML.
- Não invente objetos que não estão no HTML.
- Não emita Fabric `group` — array flat.
- Não emita `rect` — sempre `roundedRect` (cantos 0 quando sem radius).
- Não emita strings CSS para gradient — sempre objeto Fabric.
- Não emita uma textbox por span — uma textbox com `styles` por caractere.
- Não suba o template — isso é o uploader.

## Resposta final ao orquestrador

```markdown
Conversão Fabric: PASS|FAIL
Slides: <N>
Output: `<path>/output/`
Validador: PASS (exit 0) | FAIL (<N> erros)
Manifest: `<path>/manifest.json`
Próximo passo: gp2-template-result-reviewer
```
