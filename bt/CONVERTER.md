# Conversor determinístico — contrato HTML permitido

Doutrina (bt/README §6): o agente desenha, o `bt/scripts/convert.js` converte **sem consultar ninguém**. Este documento é a whitelist — o design system que o designer conhece e o conversor entende são ESTE MESMO documento. Fora daqui = REJEITADO com erro apontando o `data-el-id`; a correção é regenerar o HTML.

## Estrutura exigida

- `<section class="slide" data-width data-height>` por slide; `<html data-template-name data-segment>`; `<meta name="hm-fonts">`.
- Todo elemento visível com `data-el-id="eN"` único (lei de conservação).
- Posicionamento absoluto com `left/top` em px. Sem flex/grid/float no canvas.

## Elementos permitidos → objeto Fabric

| HTML | Objeto | Notas |
|------|--------|-------|
| `<img>` | `ClippableImage` cru | src absoluto/data-URI; cantos do `border-radius`; `center-clippable-images.js` completa crop/scale |
| Elemento com texto próprio | `textbox` | computed styles: fontSize/família/peso/fill/align/letterSpacing/lineHeight; `<span>` com cor ≠ pai → `styles` por caractere (N→1) |
| `div` com background sólido | `rect`/`roundedRect` | fill do bg; cantos do border-radius |
| `div` com `linear-gradient` | `rect` com fill gradiente Fabric | 2+ stops; direção → coords |
| `div` bg + texto (chip) | `roundedRect` + `textbox` | 1→2, mesmo `btElId` |
| Wrapper transparente sem texto | nada (1→0) | filhos processados normalmente |
| Div full-slide de fundo | `background` do canvas (1→0) | ex: `data-slide-bg` do montador |

## Propriedades honradas

`left/top` (origem center) · `width/height` · `transform: rotate` → `angle` · `opacity` · `border-radius` → cantos · `letter-spacing` → `charSpacing` · `line-height` → `lineHeight` · `text-align`.

## data-* → metadados Fabric

| Atributo | Campo |
|----------|-------|
| `data-template-element` + `data-te-description/-max-chars/-min-chars` | `isTemplateElement: true` + `templateElement{...}` |
| `data-image-type` | `imageType` |
| `data-text-type` | `textType` |
| `data-variable` (+ `data-variable-target`) | `fillVariableConfig {type:'solid', variable, alpha}` (target background em section → background variável) |
| `data-static` | sem templateElement |
| `data-el-id` | `btElId` |

## REJEITADO (erro, nunca chute)

SVG inline · `<canvas>/<video>/<iframe>` · `background-image: url(...)` em div (imagem é `<img>`) · gradientes radial/conic (usar GRADIENT_SYSTEM) · `mix-blend-mode`/`backdrop-filter`/`mask` · pseudo-elementos com conteúdo · elemento visível sem `data-el-id` · texto com `writing-mode` vertical (rotacione com transform) · qualquer coisa fora das tabelas acima.

Erro de conversão NUNCA se corrige editando JSON — regenera o HTML e, se a regra estava ambígua, ela é corrigida AQUI primeiro.
