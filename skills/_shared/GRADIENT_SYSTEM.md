# Sistema de gradientes — fonte única

Spec compartilhada entre designer, marker e converter. **Não duplique este conteúdo nas SKILLs** — referencie.

## Regra zero

**NUNCA use cores brand hex em gradientes lineares.** Background brand = fundo sólido na cor `primary` + overlay neutro de escurecimento. Gradientes `primary→secondary` são proibidos.

Os únicos gradientes legais na pipeline são:
- **`data-darken`** — escurecimento neutro (preto translúcido) para profundidade ou legibilidade.
- **`data-glow`** — círculo radial com cor brand (atmosférico, opcional).
- **`data-gradient`** — fallback JSON cru (raro, só para overlays customizados que escapam dos presets).

## Presets de `data-darken`

| `data-darken` | Direção visual | CSS equivalente (designer escreve) | Fabric coords (converter emite) |
|---------------|----------------|-------------------------------------|----------------------------------|
| `bottom` | ↓ | `linear-gradient(to bottom, transparent, rgba(0,0,0,N))` | linear `{ x1:0, y1:0, x2:0, y2:1 }` |
| `top` | ↑ | `linear-gradient(to top, transparent, rgba(0,0,0,N))` | linear `{ x1:0, y1:1, x2:0, y2:0 }` |
| `right` | → | `linear-gradient(to right, transparent, rgba(0,0,0,N))` | linear `{ x1:0, y1:0, x2:1, y2:0 }` |
| `left` | ← | `linear-gradient(to left, transparent, rgba(0,0,0,N))` | linear `{ x1:1, y1:0, x2:0, y2:0 }` |
| `diagonal-se` | ↘ | `linear-gradient(135deg, transparent, rgba(0,0,0,N))` | linear `{ x1:0, y1:0, x2:1, y2:1 }` |
| `diagonal-ne` | ↗ | `linear-gradient(45deg, transparent, rgba(0,0,0,N))` | linear `{ x1:0, y1:1, x2:1, y2:0 }` |
| `vignette` | radial centro | `radial-gradient(circle at 50% 50%, transparent, rgba(0,0,0,N))` | radial `{ x1:0.5, y1:0.5, x2:0.5, y2:0.5, r1:0, r2:1 }` |
| `vignette-top-left` | radial canto sup. esq. | `radial-gradient(circle at 20% 10%, transparent, rgba(0,0,0,N))` | radial `{ x1:0.2, y1:0.1, x2:0.2, y2:0.1, r1:0, r2:1 }` |

**ColorStops padrão (linear):** `[{ offset:0, color:"rgba(0,0,0,0)" }, { offset:1, color:"rgba(0,0,0,<opacity>)" }]`
**ColorStops padrão (vignette):** `[{ offset:0, color:"rgba(0,0,0,0)" }, { offset:0.7, color:"rgba(0,0,0,<opacity>)" }]`

`<opacity>` vem de `data-darken-opacity` (ex: `"0.8"` → `rgba(0,0,0,0.8)`).

Opacidade orientativa: `0.65–0.80` para texto 400; `0.45–0.60` para texto 700+.

## Mapeamento CSS → preset (para marker como safety net)

Quando um elemento tem `linear-gradient(`/`radial-gradient(` no `style` mas falta `data-darken`, o marker infere a direção:

| CSS observado | Preset |
|---------------|--------|
| `to bottom` / `180deg` | `bottom` |
| `to top` / `0deg` | `top` |
| `to right` / `90deg` | `right` |
| `to left` / `270deg` | `left` |
| `135deg` | `diagonal-se` |
| `45deg` | `diagonal-ne` |
| `radial-gradient(circle at center` | `vignette` |
| `radial-gradient(circle at` com offset | `vignette-top-left` |

**Sem `data-darken` E sem `data-gradient`** → marker adiciona `data-darken` + `data-darken-opacity` (e loga em `marker-audit.md`).
**`<section>` com cores brand hex em gradiente** → FAIL, devolve ao designer.

## Emissão Fabric — darken

Padrão único: section com fundo sólido brand + `<div>` filho de overlay.

HTML:
```html
<section class="slide" data-width="1080" data-height="1350"
         data-variable="primary" data-variable-target="background"
         style="position:relative; width:1080px; height:1350px; background:#E0005A;">
  <div data-darken="diagonal-se" data-darken-opacity="0.8"
       style="position:absolute; left:0; top:0; width:1080px; height:1350px;
              background:linear-gradient(135deg, transparent 0%, rgba(0,0,0,0.8) 100%);">
  </div>
</section>
```

JSON emitido:
- `background`: hex sólido da primary.
- `backgroundVariableConfig`: `{ type:"solid", variable:"primary", alpha:1 }`.
- Primeiro `objects[]`: `roundedRect` cobrindo o slide com gradient fill (lookup acima).
- Overlay **não** carrega `fillVariableConfig` — é neutro (preto translúcido).

```json
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
```

## Glow — `data-glow`

Círculo radial translúcido com cor brand. Sempre opt-in.

HTML (designer escreve):
```html
<div data-glow="center"
     data-glow-variable="secondary"
     data-glow-alpha="0.44"
     data-static="true"
     style="position:absolute; left:900px; top:-620px; width:560px; height:560px;
            border-radius:50%;
            background:radial-gradient(circle, rgba(34,211,238,0.44) 0%, transparent 100%);
            opacity:0.11;">
</div>
```

Atributos obrigatórios:
| Atributo | Valor |
|----------|-------|
| `data-glow` | `center` (única coord canônica hoje) |
| `data-glow-variable` | `primary` ou `secondary` |
| `data-glow-alpha` | `0.0`–`1.0` (intensidade da cor brand dentro do gradiente) |
| `data-static="true"` | sempre |

Lookup coords: `center` → `{ x1:0.5, y1:0.5, x2:0.5, y2:0.5, r1:0, r2:0.5 }`.

Algoritmo de emissão:
1. Leia `data-glow-variable` e `data-glow-alpha`.
2. Obtenha o hex da variável brand no manifest/paleta.
3. Converta hex + alpha para `#RRGGBBAA` (ex: `#22D3EE` + alpha `0.44` → `0x70` → `#22d3ee70`).
4. Leia `opacity` do `style` (default `1.0`) — separado do alpha do gradiente.
5. Emita `roundedRect` circular (`topLeft/Right/Bottom: 100`) com radial gradient fill **e** `fillVariableConfig: gradient` referenciando o stop colorido.

JSON emitido:
```json
{
  "type": "roundedRect",
  "name": "Glow <variable> <posicao>",
  "left": "<center_x>", "top": "<center_y>",
  "width": "<width>", "height": "<height>",
  "originX": "center", "originY": "center",
  "topLeft": 100, "topRight": 100, "bottomRight": 100, "bottomLeft": 100,
  "opacity": "<opacity_from_style>",
  "fill": {
    "type": "radial",
    "coords": { "x1": 0.5, "y1": 0.5, "x2": 0.5, "y2": 0.5, "r1": 0, "r2": 0.5 },
    "colorStops": [
      { "offset": 0, "color": "#<hex_brand><alpha_hex>" },
      { "offset": 1, "color": "#bebebe00" }
    ],
    "offsetX": 0, "offsetY": 0,
    "gradientUnits": "percentage",
    "gradientTransform": null
  },
  "fillVariableConfig": {
    "type": "gradient",
    "colorStops": [
      { "variable": "<data-glow-variable>", "alpha": "<float>" },
      null
    ]
  },
  "isStatic": true
}
```

Notas:
- `colorStops[1]` no fill é `"#bebebe00"` (neutro descartável, alpha 0).
- `fillVariableConfig.colorStops[1] = null` porque o segundo stop é neutro.
- Glow é o **único** caso em que usamos `#RRGGBBAA` (hex+alpha) em colorStops. Em darken/overlay, mantém `rgba(R,G,B,A)`.
- Círculo sólido com `background:#22D3EE; opacity:0.11` sem `data-glow` **não vira glow** — vira fill sólido.

## Regras críticas (válidas em qualquer caso)

- `type` no fill = `"linear"` ou `"radial"`. Nunca string CSS, nunca `"linearGradient"`.
- `gradientUnits: "percentage"` sempre.
- `gradientTransform: null` sempre presente.
- Overlay neutro (darken puro) **nunca** recebe `fillVariableConfig`.
- `data-variable-stops` é legado — eliminado da pipeline. Marker remove se encontrar.
- `<style>` block com gradientes — converter não lê. Designer deve manter tudo inline.

## Sombras (anexo)

`box-shadow` sempre com `rgba(0,0,0, <opacity>)`. Nunca com hex brand. Opacidade típica: `0.08–0.20` para cards; `0.25–0.40` para decorativo.

## Self-check (converter, pós-emissão)

| Condição no HTML | O que DEVE existir no JSON |
|------------------|----------------------------|
| `<section data-variable="X" data-variable-target="background">` | `background` = hex de X + `backgroundVariableConfig: { type:"solid", variable:"X", alpha:1 }` |
| `<div data-darken="Y" data-darken-opacity="Z">` dentro de section | roundedRect com linear/radial gradient fill (lookup Y, opacity Z), sem `fillVariableConfig` |
| `<div data-darken="Y">` overlay sobre `<img>` | roundedRect com gradient fill, sem `fillVariableConfig` |
| `<div data-glow="Y" data-glow-variable="X" data-glow-alpha="A">` | roundedRect radial + `fillVariableConfig: { type:"gradient", colorStops: [{ variable:"X", alpha:A }, null] }` |

Falha → corrigir antes de prosseguir. Máximo 2 fixes.
