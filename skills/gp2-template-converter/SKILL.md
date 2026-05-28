---
name: gp2-template-converter
description: "Converte HTML marcado (do gp2-template-marker) em Fabric.js CanvasJSON pronto para o editor HealthMarket. Adota a spec técnica de HTML + sistema de gradientes da pipeline v2 (`skills/_shared/`) como contrato e roda `scripts/validate-slides.js` como gate. Use após gp2-template-marker (audit PASS), antes de gp2-template-uploader."
---

# gp2-template-converter

Migra `template.html` marcado para uma série de `slide-N.json` Fabric.js — um por `<section class="slide">`. Output validado por `scripts/validate-slides.js` (na raiz da pipeline v2).

## Contrato

A pipeline v2 é autocontida. As fontes de verdade do contrato HTML → Fabric vivem **dentro de `getposts-pipeline-v2/`**:

- [`../_shared/HTML_TECHNICAL_SPEC.md`](../_shared/HTML_TECHNICAL_SPEC.md) — regras estruturais do HTML, tabela de `data-*`, anti-patterns.
- [`../_shared/GRADIENT_SYSTEM.md`](../_shared/GRADIENT_SYSTEM.md) — presets de `data-darken` / `data-glow` / `data-gradient` e emissão Fabric.
- [`../../CONTRACT.md`](../../CONTRACT.md) — resumo high-level e mapa dos validadores.

Este SKILL.md sumariza o essencial do mapeamento HTML → Fabric. Quando em dúvida, leia as specs compartilhadas acima.

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

Toda regra abaixo se apoia em `_shared/HTML_TECHNICAL_SPEC.md` (HTML) e `_shared/GRADIENT_SYSTEM.md` (gradientes). Reúno aqui só os erros mais comuns que travam validador/editor:

| Regra | Detalhe |
|-------|---------|
| Versão | `version: "5.5.2"` no root |
| Sem groups | `objects` é array flat — Fabric groups quebram round-trip |
| Sem `rect` | use **sempre** `roundedRect` (cantos `0` quando sem radius). Plain `rect` quebra deserialize com gradiente |
| Origem | todo objeto: `originX: "center"`, `originY: "center"` |
| Conversão de coords | HTML top-left → Fabric center: `left = htmlLeft + width/2`, `top = htmlTop + height/2` |
| Nomes | todo objeto tem `name` (rótulo PT-BR descritivo: `"Título"`, `"Subtítulo"`, `"Corpo"`, `"Eyebrow"`, `"CTA"`, `"Foto"`, `"Foto profissional"`, `"Logo"`, `"Avatar"`, `"Card"`, `"Faixa"`, `"Divisor"`, `"Overlay legibilidade"`, `"Escurecimento atmosferico"`, `"Glow <variable> <posição>"`, etc. — use o rótulo mais específico que ainda fizer sentido para o usuário do editor) |
| **border-radius → corners** | `roundedRect` corners são **percentagens de `min(width, height)/2`**. Fórmula: `corner = (border_radius_px / (min(width, height) / 2)) * 100`, clampado a 0–100. Ex: `border-radius: 46px` num card 964×1210 → `(46 / 482) * 100 = 9.54` → `topLeft: 9.54`. **Nunca passe o valor px direto** — `46` significa 46%, não 46px |
| Textbox | sempre `styles: {}` (mesmo vazio); sem `styles` quebra Fabric |
| `lineHeight` | clampado a >= 1.0 (Fabric 5.x renderiza < 1.0 inconsistente) |
| `charSpacing` | clampado a >= -150 (abaixo, texto colapsa) |
| `text-transform` | aplicado direto na string (`text.toUpperCase()`); **não emita `textTransform`** |
| Cores brand | `data-variable="primary\|secondary"` → `fillVariableConfig`/`strokeVariableConfig`/`backgroundVariableConfig` `{type:"solid", variable, alpha}` |
| `textAlign` | `text-align: center\|right\|left\|justify` → `textAlign: "center"\|"right"\|"left"\|"justify"` no textbox. Default: `"left"`. **Nunca omita** — se o HTML tem `text-align:center`, o JSON **deve** ter `textAlign: "center"` |
| Background brand sólido | `<section data-variable="primary" data-variable-target="background">` → root `backgroundVariableConfig: { type: "solid", variable, alpha }` |
| Background brand com escurecimento | `<section data-variable="primary" data-variable-target="background">` + `<div data-darken="..." data-darken-opacity="...">` → root `background` = hex sólido primary + `backgroundVariableConfig` sólido + roundedRect primeiro objeto com gradient fill neutro (sem `fillVariableConfig` — overlay é neutro) |
| Spans | inline `<span>` em texto editável → **uma** textbox com `styles[lineIndex][charIndex]`; **nunca** uma textbox por span |
| Profile vars | `data-text-type` → `textType: "..."` no objeto, sem `isTemplateElement` |
| Templates | `data-template-element="true"` → `isTemplateElement: true` + bloco `templateElement` |
| Imagens (todas) | toda `<img>` → `ClippableImage` com `originX:"center"`, `originY:"center"`, `src` absoluto, `width`/`height` = dimensões do **frame visual no HTML** (slot), `topLeft/topRight/bottomRight/bottomLeft` em % derivados do `border-radius`. **NÃO calcule `cropX/cropY`, `scaleX/scaleY`, `originWidth/originHeight`** — o script `center-clippable-images.js` faz isso deterministicamente pós-emissão, espelhando o `ClippableImage.replaceImage()` do editor (ver seção dedicada abaixo) |
| Gradientes | `type: "linear"\|"radial"` (NUNCA `linearGradient`); inclui `coords`, `colorStops`, `offsetX`, `offsetY`, `gradientUnits: "percentage"`, `gradientTransform: null` |
| Background gradiente | **Nunca** string CSS `"linear-gradient(...)"`. Overlays com `data-darken` → `roundedRect` com gradient fill neutro. **Nunca** emita `backgroundVariableConfig` gradient — o editor só suporta sólido. `data-variable-stops` foi eliminado — se encontrado, ignore |

## ClippableImage — emissão crua + pós-processo determinístico

A partir da v2, o converter **não calcula crop**. Emita cada `<img>` como `ClippableImage` no estado "cru", e o script [`../../scripts/center-clippable-images.js`](../../scripts/center-clippable-images.js) reaplica deterministicamente o mesmo cover-crop centralizado que o editor da plataforma executa quando o usuário troca a imagem (`ClippableImage.replaceImage()` em `Frontend/mkt-platform-frontend/.../objects/clippable-image.ts`).

**Toda `ClippableImage` é cover crop centrado.** Não existe mais ramo "cutout" / `originY:"bottom"`. Se o HTML usa `object-fit:contain` (ex: PNG cutout de `professionalPhoto`), o pós-processo vai tratar como cover. Isso é intencional: o editor faz a mesma coisa quando o usuário sobe uma foto, então o resultado pós-conversão é exatamente o que o usuário verá depois.

### O que o converter emite

Para cada `<img>`:

```json
{
  "type": "ClippableImage",
  "name": "<rótulo PT-BR>",
  "src": "<URL absoluta>",
  "left": "<htmlLeft + slotWidth / 2>",
  "top":  "<htmlTop  + slotHeight / 2>",
  "width":  "<slotWidth>",
  "height": "<slotHeight>",
  "originX": "center",
  "originY": "center",
  "topLeft": "<0..100>", "topRight": "<0..100>",
  "bottomRight": "<0..100>", "bottomLeft": "<0..100>",
  "crossOrigin": "anonymous",
  "imageType": "professionalPhoto|userAsset|brandLogo",
  "isTemplateElement": "<bool>",
  "templateElement": { "description": "...", "removeBackground": false }
}
```

Regras:

- `width`/`height` = dimensões do **frame visual no HTML** (o slot). Sem `scaleX`/`scaleY` (defaults `1.0`).
- Sem `cropX`/`cropY`/`originWidth`/`originHeight` — o pós-processo preenche.
- `topLeft/topRight/bottomRight/bottomLeft` derivam do `border-radius` do HTML (mesma fórmula `%` de `min(width,height)/2` da tabela acima).
- `left`/`top` em Fabric center conforme tabela geral.

### O que o pós-processo faz

`center-clippable-images.js` itera sobre todos os `slide-*.json` de uma pasta, lê `naturalWidth`/`naturalHeight` de cada `src` (decode direto de magic bytes para `data:` URLs e HTTP genéricos — sem browser; Playwright só como fallback opcional para formatos exóticos) e patcheia o objeto com:

```js
const visualWidth  = width  * scaleX;   // = slot, antes do patch
const visualHeight = height * scaleY;
const objectAspect = visualWidth / visualHeight;
const imageAspect  = naturalW / naturalH;

let cropW, cropH;
if (imageAspect > objectAspect) { cropH = naturalH; cropW = cropH * objectAspect; }
else                            { cropW = naturalW; cropH = cropW / objectAspect; }
const cropX = (naturalW - cropW) / 2;
const cropY = (naturalH - cropH) / 2;
const scale = visualWidth / cropW;

obj.originWidth  = naturalW;
obj.originHeight = naturalH;
obj.width  = cropW;   obj.height = cropH;
obj.cropX  = cropX;   obj.cropY  = cropY;
obj.scaleX = scale;   obj.scaleY = scale;
```

Idempotente: rodar duas vezes produz o mesmo JSON.

### Regra de origin (atualizada)

Todo objeto — **inclusive `ClippableImage`** — usa `originX: "center"` e `originY: "center"`. Não há mais exceção para cutout.

## Gradientes — emissão Fabric via `data-darken`

### REGRA ZERO (CRÍTICO)

**NUNCA use `getComputedStyle()` para extrair cores de gradiente.** A pipeline v2 usa `data-darken` para indicar presets de escurecimento. Leia o atributo e emita o gradiente usando o lookup definitivo em [`../_shared/GRADIENT_SYSTEM.md`](../_shared/GRADIENT_SYSTEM.md) §"Presets de `data-darken`" — sem parsear CSS.

A spec compartilhada cobre: tabela completa de presets → coords Fabric, colorStops padrão (linear vs. vignette), regras de `gradientUnits`/`gradientTransform`, fallback `data-gradient`, glow brand via `data-glow` e self-check pós-emissão.

### Padrão único — Fundo brand com escurecimento atmosférico

A `<section>` tem:
- `data-variable="primary" data-variable-target="background"` (fundo sólido brand)
- Um `<div>` filho com `data-darken="<preset>" data-darken-opacity="<N>"` (overlay)

**Emita:**

1. **`background`** no root: hex sólido da primary (leia do `style` da section)
2. **`backgroundVariableConfig`** no root: `{ type: "solid", variable: "primary", alpha: 1 }`
3. **roundedRect como PRIMEIRO objeto** em `objects[]`: cobre o slide inteiro com gradient fill

```json
{
  "version": "5.5.2",
  "background": "#E0005A",
  "backgroundVariableConfig": { "type": "solid", "variable": "primary", "alpha": 1 },
  "objects": [
    {
      "type": "roundedRect",
      "name": "Escurecimento atmosferico",
      "left": 540, "top": 675,
      "width": 1080, "height": 1350,
      "originX": "center", "originY": "center",
      "topLeft": 0, "topRight": 0, "bottomRight": 0, "bottomLeft": 0,
      "fill": {
        "type": "linear",
        "coords": { "x1": 0, "y1": 0, "x2": 1, "y2": 1 },
        "colorStops": [
          { "offset": 0, "color": "rgba(0,0,0,0)" },
          { "offset": 1, "color": "rgba(0,0,0,0.8)" }
        ],
        "offsetX": 0, "offsetY": 0,
        "gradientUnits": "percentage",
        "gradientTransform": null
      }
    }
  ]
}
```

O overlay **NÃO tem `fillVariableConfig`** — é neutro (preto). Trocar paleta muda o fundo sólido via `backgroundVariableConfig`; o escurecimento se adapta sozinho.

### Overlay de legibilidade sobre foto

`<div>` com `data-darken` sobre `<img>`. Mesmo procedimento: leia preset + opacity, emita roundedRect com gradient fill na posição/tamanho do div.

```json
{
  "type": "roundedRect",
  "name": "Overlay legibilidade",
  "left": 540, "top": 675,
  "width": 1080, "height": 1350,
  "originX": "center", "originY": "center",
  "topLeft": 0, "topRight": 0, "bottomRight": 0, "bottomLeft": 0,
  "fill": {
    "type": "linear",
    "coords": { "x1": 0, "y1": 0, "x2": 0, "y2": 1 },
    "colorStops": [
      { "offset": 0, "color": "rgba(0,0,0,0)" },
      { "offset": 1, "color": "rgba(0,0,0,0.75)" }
    ],
    "offsetX": 0, "offsetY": 0,
    "gradientUnits": "percentage",
    "gradientTransform": null
  },
  "isStatic": true
}
```

### Fallback: `data-gradient` JSON (raro)

Se um elemento tem `data-gradient` ao invés de `data-darken` (overlay customizado), leia o JSON diretamente como `fill`:

1. Parse JSON de `data-gradient`
2. Use como `fill` adicionando: `offsetX: 0, offsetY: 0, gradientUnits: "percentage", gradientTransform: null`

### Glow atmosférico: `data-glow` → radial gradient com `fillVariableConfig`

Elementos com `data-glow` são círculos de iluminação atmosférica com cor brand. O converter lê os atributos e emite um `roundedRect` circular com radial gradient `fill` + gradient `fillVariableConfig`.

**Lookup table: `data-glow` → Fabric radial gradient coords**

| `data-glow` | coords |
|-------------|--------|
| `center`    | `{ x1: 0.5, y1: 0.5, x2: 0.5, y2: 0.5, r1: 0, r2: 0.5 }` |

**Algoritmo de conversão:**

1. Leia `data-glow-variable` (ex: `"secondary"`) e `data-glow-alpha` (ex: `"0.44"`).
2. Obtenha a cor hex da variável brand no manifest/paleta (ex: `#22D3EE` para secondary).
3. Converta hex + alpha para `#RRGGBBAA`: hex da cor brand + alpha como 2 hex digits. Ex: `#22D3EE` com alpha `0.44` → `0.44 × 255 = 112 = 0x70` → `#22d3ee70`.
4. Leia `opacity` do `style` (default `1.0`).
5. Emita:

```json
{
  "type": "roundedRect",
  "name": "Glow <variable> <posição>",
  "left": "<center_x>",
  "top": "<center_y>",
  "width": "<width>",
  "height": "<height>",
  "originX": "center",
  "originY": "center",
  "topLeft": 100,
  "topRight": 100,
  "bottomRight": 100,
  "bottomLeft": 100,
  "opacity": "<opacity_from_style>",
  "fill": {
    "type": "radial",
    "coords": { "x1": 0.5, "y1": 0.5, "x2": 0.5, "y2": 0.5, "r1": 0, "r2": 0.5 },
    "colorStops": [
      { "offset": 0, "color": "#<hex_brand><alpha_hex>" },
      { "offset": 1, "color": "#bebebe00" }
    ],
    "offsetX": 0,
    "offsetY": 0,
    "gradientUnits": "percentage",
    "gradientTransform": null
  },
  "fillVariableConfig": {
    "type": "gradient",
    "colorStops": [
      { "variable": "<data-glow-variable>", "alpha": "<data-glow-alpha as float>" },
      null
    ]
  },
  "isStatic": true
}
```

**Notas críticas (glow):**
- `topLeft/topRight/bottomRight/bottomLeft: 100` → círculo perfeito (equivalente a `border-radius: 50%`).
- `colorStops[1]` no fill é `"#bebebe00"` (cinza totalmente transparente) — cor neutra descartável.
- `fillVariableConfig.colorStops[1]` é `null` porque o segundo stop é neutro.
- `opacity` do elemento vem do CSS `opacity`, separado do `data-glow-alpha` (que controla a intensidade da cor brand dentro do gradiente).

### Self-validation pós-emissão (OBRIGATÓRIO)

Após emitir cada slide, rode o self-check da spec compartilhada (ver [`../_shared/GRADIENT_SYSTEM.md`](../_shared/GRADIENT_SYSTEM.md) §"Self-check (converter, pós-emissão)") + o checklist de `data-variable` específico do converter (próxima seção do workflow). Máximo 2 fixes antes de escalar.

Regras críticas (em qualquer caso): `type` = `"linear"`/`"radial"` (nunca string CSS), `gradientUnits: "percentage"`, `gradientTransform: null`. Cor com alpha: `rgba(R,G,B,A)` em darken/overlay; `#RRGGBBAA` (hex+alpha) **apenas** em glow. Overlay neutro nunca recebe `fillVariableConfig`. `data-variable-stops` é legado — ignore se encontrar.

## Workflow

1. Confirme inputs prontos: `template.html` marcado existe, `marker-audit.json.status === "PASS"`.
2. Crie `artifacts/gp2-template-converter/<slug>/output/`.
3. Para cada `<section class="slide">`, parse e emita `slide-N.json`:
   - Walk DOM em order (z-order).
   - Calcule coordenadas absolute → Fabric center.
   - Aplique mapeamento HTML → Fabric: `<p>`/`<h*>`/`<span>` → `textbox`; `<div>` com `border-radius` ou cor → `roundedRect`; `<img>` → `ClippableImage`; `<section>` define o canvas. Detalhes de cada tipo na tabela acima e em `_shared/HTML_TECHNICAL_SPEC.md`.
   - **Para cada elemento com `data-gradient`:** leia o JSON, use como `fill` diretamente (adicionar `offsetX:0, offsetY:0, gradientUnits:"percentage", gradientTransform:null`). NUNCA use computed styles para estes elementos.
   - Se `<section>` tem `data-gradient` (fallback raro): emita roundedRect com o gradient de `data-gradient` como fill. Sem `fillVariableConfig` — overlays são neutros.
   - Detecte cores brand (explícitas via `data-variable` ou auto-detect).
   - Para textboxes com `<span>`, calcule `styles[lineIndex][charIndex]` contando caracteres exatos (sem aproximar).
   - Adicione `name` PT-BR descritivo a cada objeto.
4. **Checklist de variable configs (OBRIGATÓRIO — rodar após emitir cada slide):**

   Para cada slide emitido, verifique manualmente:

   | Condição no HTML | O que DEVE existir no JSON | Bug se ausente |
   |------------------|---------------------------|----------------|
   | `<section data-variable="X" data-variable-target="background">` | root `backgroundVariableConfig: { type: "solid", variable: "X", alpha: 1 }` | Trocar paleta não muda o fundo |
   | `<div data-darken="Y" data-darken-opacity="Z">` (overlay escurecimento) | roundedRect com gradient fill neutro (lookup table `data-darken`) — SEM `fillVariableConfig` | Escurecimento perdido, fundo parece flat |
   | `<div data-variable="X">` (shape) | `fillVariableConfig: { type: "solid", variable: "X", alpha: 1 }` no objeto | Cor fica literal |
   | `<div data-variable="X" data-variable-target="background">` (não-section) | `fillVariableConfig` no roundedRect correspondente | Cor fica literal |
   | `<p data-variable="X">` / `<h1 data-variable="X">` | `fillVariableConfig` no textbox | Cor do texto fica literal |
   | `<div data-glow="Y" data-glow-variable="X" data-glow-alpha="A">` | `fillVariableConfig: { type: "gradient", colorStops: [{ variable: "X", alpha: A }, null] }` no roundedRect | Glow não adapta com paleta |

   **Se qualquer condição falhar, corrija antes de prosseguir.** Esta checklist pega o bug mais comum da pipeline: `data-variable` presente no HTML mas `variableConfig` ausente no JSON.

5. Escreva `manifest.json`:

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

6. **Rode o pós-processo de centralização** (preenche `cropX/cropY/scaleX/scaleY/originWidth/originHeight` de cada `ClippableImage` baixando a imagem e medindo o natural size):

```bash
node ../../scripts/center-clippable-images.js artifacts/gp2-template-converter/<slug>/output/
```

Exit `0` = todas as imagens centralizadas. Exit `1` = uma ou mais URLs falharam ao carregar (404, CORS, etc.) — leia o stdout, corrija o `src` do objeto ofensor (ou pegue uma URL alternativa) e rode novamente.

7. Rode o validador:

```bash
node ../../scripts/validate-slides.js artifacts/gp2-template-converter/<slug>/output/
```

8. Para cada erro, leia o slide ofensor, corrija com Edit, salve. Loop máximo: **2 fixes**.
9. Quando o validador retornar exit `0`, escreva `conversion-report.md` resumindo.

## Validate-and-fix loop

Erros típicos retornados por `scripts/validate-slides.js` e como corrigir. Loop máximo: **2 fixes** antes de escalar ao orquestrador.

| Erro | Fix |
|------|-----|
| `missing or empty "name"` | adicione `"name": "<rótulo PT-BR>"` |
| `textbox is missing "styles"` | adicione `"styles": {}` |
| `lineHeight X is below 1.0` | clampe para `1.0` |
| `originX/Y must be "center"` | corrija |
| `ClippableImage missing "originWidth"`/`cropX`/`scaleX` etc. | rode `scripts/center-clippable-images.js` (passo 6 do workflow). Se já rodou e ainda falta, a URL do `src` falhou ao baixar — corrija o `src` e rode de novo |
| `roundedRect corner X must be 0–100` | recalcule: `corner = (border_radius_px / (min(width, height) / 2)) * 100` |
| `variable must be "primary"\|"secondary"` | corrija valor |
| `charSpacing X is below -150` | clampe para `-150` |
| `CSS gradient string … is not valid` | substitua por objeto Fabric gradient |
| glow/neon como div translúcido | substitua por `shadow` no objeto alvo: `box-shadow: 0 0 60px 20px rgba(R,G,B,A)` → `shadow: { color, blur, offsetX: 0, offsetY: 0 }`. Remova o div de glow separado |
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
Próximo passo: gp2-template-uploader
```
