# Catálogo de componentes (a interface)

Este documento + `design-system.css` são o contrato inteiro entre o html generator
(agente) e o `convert.js`. O agente escreve HTML semântico: componentes deste
catálogo, `grid-area` inline, conteúdo e `data-*`. **Nada além disso.** Classe fora
do catálogo, inline style fora da whitelist ou sobreposição não declarada =
REJEIÇÃO apontando o `data-el-id`; a correção é sempre regenerar o HTML, nunca
editar JSON (doutrina do conversor, herdada como lei).

## Esqueleto obrigatório (a fita inteira — 1 arquivo = 1 run: `fita.html`)

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="hm-fonts" content="<fonts.meta do pack.json>">
</head>
<body>
<main class="fita" data-pack="<slug-do-pack>" data-template-name="..." data-segment="...">
  <section class="slide" data-role="abertura"> <!-- componentes --> </section>
  <section class="slide" data-role="item"> ... </section>
  <section class="slide" data-role="fechamento"> ... </section>
  <div class="fita-layer">
    <!-- TRAVESSIAS: elementos que cruzam fronteiras de slide.
         Grid contínuo da fita: 12·N colunas × 12 linhas (célula 90×112.5).
         Só data-static + data-layer (imagem/forma/watermark) — NUNCA editável.
         Pintam POR CIMA dos slides: só sobre backgrounds limpos, nunca sob texto. -->
    <img class="ds-photo" data-el-id="f1" data-static data-layer
         data-image-type="userAsset" style="grid-area: 2 / 11 / 5 / 16">
  </div>
</main>
</body>
</html>
```

- Tokens, fontes e o design-system.css são **injetados mecanicamente** pelo
  convert/assemble a partir do `pack.json` (`data-pack` resolve o pack). O HTML
  nunca contém cores nem links de CSS.
- `data-role` é obrigatório em toda seção: 1ª `abertura`, última `fechamento`,
  demais `item` (gate do runner).
- Slide invertido (respiro/CTA): `<section class="slide" data-role="..."
  data-invert data-variable="primary" data-variable-target="background">`.
- **Ordem no DOM = ordem de empilhamento no canvas** (watermark primeiro;
  travessias da fita-layer são as últimas — pintam por cima).
- Par de fotos contínuas, decor cruzando a emenda, faixas atravessando slides:
  tudo é simplesmente um elemento na `.fita-layer` sobre a fronteira — o
  conversor emite o objeto nos DOIS slides vizinhos com o centro deslocado e o
  Fabric clipa o que fica fora do canvas.

## Grid declarativo

12 colunas × 12 linhas (1080×1350 → célula 90×112.5px). Posicionamento é SEMPRE
`style="grid-area: R1 / C1 / R2 / C2"` — a única propriedade inline permitida,
além de `transform: rotate(Ndeg)` para rotação declarada. O browser resolve as
coordenadas; o conversor lê o resultado computado.

Sobreposição entre componentes é violação, EXCETO componentes de camada:
`ds-watermark` ou qualquer componente com `data-layer`.

## Componentes → objeto Fabric

| Classe | HTML | Objeto Fabric | Notas |
|--------|------|---------------|-------|
| `ds-eyebrow` | texto | `textbox` | label pequena UPPERCASE |
| `ds-headline` | texto | `textbox` | display UPPERCASE; `<span data-tone="accent">` vira styles por caractere |
| `ds-body` | texto | `textbox` | corpo; `data-tone="muted"` para secundário |
| `ds-number` | texto | `textbox` | `[N]` no acento; `data-size="lg"` = gigante |
| `ds-watermark` | texto | `textbox` | camada (pode sobrepor); `data-static` implícito NÃO — marque `data-static`; `data-vertical` = rotacionada -90° |
| `ds-stamp` | texto | `roundedRect` (stroke) + `textbox` | chip outline 1→2, mesmo `elId`; rotação via `transform: rotate()` |
| `ds-cta` | texto | `roundedRect` (fill) + `textbox` | pill preenchida 1→2 |
| `ds-block` | container | `roundedRect` + filhos | bg do acento (`data-tone="ink"` = preto); filhos são componentes do catálogo |
| `ds-card` | container | `roundedRect` + filhos | cartão no papel, cantos `--radius` |
| `ds-shape` | vazio | `roundedRect` (cantos por lado; anel = stroke) | forma de composição: `data-shape="circle\|ring\|pill"`; cor via `data-tone`; `data-half="left\|right"` na BORDA do slide cria transição — o par complementar no slide vizinho completa a forma na fita |
| `ds-photo` | `<img>` | `ClippableImage` | imagem gerada/evidência; `data-image-type` obrigatório |
| `ds-slot` | `<img>` | `ClippableImage` | slot da plataforma: `data-slot="professionalPhoto\|instagramProfilePicture\|logo"` (vira `imageType`); `data-circle` para avatar, `data-cutout` para cutout ancorado na base |

Modificadores globais: `data-tone` (muted/accent/paper/accent-ink) ·
`data-align` (center/right) · `data-round`/`data-circle` (imagens) ·
`data-overhang="top|bottom|tl|tr|bl|br"` (decor: imagem inteira sem crop, deslocada parcialmente para fora do slide — cortada pela borda, rotação embutida; usar junto com data-cutout) · `data-size="lg"` (ds-number e ds-headline) · `data-face="serif"` (voz serif do pack via `--font-serif`, sentence case).

## data-* de metadados

| Atributo | Efeito no JSON |
|----------|----------------|
| `data-el-id="eN"` | `elId` — obrigatório em TODO componente (lei de conservação) |
| `data-template-element` + `data-te-description` + `data-te-min-chars`/`data-te-max-chars` (texto) | `isTemplateElement: true` + `templateElement{...}` — min/max obrigatórios em texto editável |
| `data-te-remove-bg="true\|false"` (imagem editável) | `templateElement.removeBackground` |
| `data-static` | sem templateElement |
| `data-text-type="instagramName\|instagramHandle\|phone\|address"` | `textType` (exclusivo com template-element) |
| `data-image-type` | `imageType` (em `ds-slot` o default é o valor de `data-slot`) |
| `data-variable="primary\|secondary"` (+ `data-variable-target="background"` na section) | `fillVariableConfig` / background variável |

## REJEITADO (erro, nunca chute)

Classe fora do catálogo · elemento visível sem `data-el-id` · inline style além
de `grid-area`/`transform:rotate` · sobreposição de componentes não-camada ·
SVG/canvas/video/iframe · `background-image:url()` (imagem é `<img>`) ·
gradiente radial/conic · mix-blend-mode/backdrop-filter/mask · pseudo-elemento
com conteúdo · texto editável sem `data-te-min-chars`/`max-chars` · `ds-photo`
sem `data-image-type` · texto com `writing-mode` vertical.

## Composição (designer)

O designer compõe a fita inteira de uma vez, com o conhecimento em camadas:
`knowledge/design/geral.md` (leis de qualquer pack) → `packs/<slug>/`
(tecnicas.md, exemplos/, tokens, lessons.md — o estilo) → o dossiê do copy.
Gerações do mesmo pack DEVEM variar: os exemplos do pack são ponto de partida,
nunca fôrma. O que é lei está neste catálogo e nos gates; o resto é design.
