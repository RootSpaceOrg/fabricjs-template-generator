# Catálogo de componentes (a interface)

Este documento + `design-system.css` são o contrato inteiro entre o html generator
(agente) e o `convert.js`. O agente escreve HTML semântico: componentes deste
catálogo, `grid-area` inline, conteúdo e `data-*`. **Nada além disso.** Classe fora
do catálogo, inline style fora da whitelist ou sobreposição não declarada =
REJEIÇÃO apontando o `data-el-id`; a correção é sempre regenerar o HTML, nunca
editar JSON (doutrina do conversor, herdada como lei).

## Esqueleto obrigatório (por slide — 1 arquivo = 1 slide)

```html
<!doctype html>
<html data-pack="<slug-do-pack>" data-template-name="..." data-segment="...">
<head>
  <meta charset="utf-8">
  <meta name="hm-fonts" content="<fonts.meta do pack.json>">
  <link rel="stylesheet" href="../../../../engine/design-system.css">
</head>
<body>
  <section class="slide" data-recipe="<recipe>">  <!-- componentes aqui -->
  </section>
</body>
</html>
```

- Tokens e fontes do pack são **injetados mecanicamente** pelo convert/assemble a
  partir do `pack.json` (`data-pack` resolve o pack). O HTML nunca contém cores.
- Slide invertido (respiro/CTA): `<section class="slide" data-invert
  data-variable="primary" data-variable-target="background">`.
- **Ordem no DOM = ordem de empilhamento no canvas** (watermark primeiro).

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
`data-overhang="top|bottom|tl|tr|bl|br"` (decor: imagem inteira sem crop, deslocada parcialmente para fora do slide — cortada pela borda, rotação embutida; usar junto com data-cutout) · `data-pos="left|right"` (imagem: recorte ancorado na lateral — par de slides vizinhos com a MESMA imagem gera transição contínua) · `data-size="lg"` (ds-number e ds-headline) · `data-face="serif"` (voz serif do pack via `--font-serif`, sentence case).

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

## Plano da fita (ANTES de compor qualquer slide)

A fita é a unidade de design; o slide é só materialização. Antes do primeiro
HTML, o compose decide — e registra em `draw.json` — o plano inteiro:

1. **Sorteio do miolo**: quais recipes, quantas e em que ordem (regras do
   `pack.json` §sorteio). Gerações do mesmo pack DEVEM variar entre si.
2. **Pares contínuos**: se `item-foto-direita` for seguido de
   `item-foto-esquerda` (foto na borda comum), declare `"pares": [[i, i+1]]`
   no draw.json e use **UMA foto paisagem** (>=1792x1024) cortada por
   `python engine/tools/split-pair.py <foto> <outL> <outR> --frame WxH` —
   janela esquerda no slide A (`data-pos="left"`), direita no B
   (`data-pos="right"`). O gate do runner reprova par não declarado ou
   incompleto. Fotos diferentes/repetidas nos dois lados = reprovado.
3. **Espelhamento (eixo de variância)**: por slide, sorteie espelhar o grid
   horizontalmente — `"R1 / C1 / R2 / C2"` vira `"R1 / (14−C2) / R2 / (14−C1)"`,
   `rot` inverte o sinal, `data-overhang` troca lado (`tl↔tr`, `bl↔br`);
   `data-align` right↔left. NUNCA espelhar slides de par contínuo.
4. **Decors**: sorteie presença (miolo 0–1, capa/cta 1–2), borda
   (`data-overhang`) e objeto do tema — assets sempre gerados para o post
   (regras em `packs/<slug>/images.md`; exemplares do pack não são estoque).
5. **Costuras** (`seams.json` da run), se a fita pedir transições extras.

## Recipes → HTML (tradução determinística)

O agente NÃO inventa layout: cada slide vem de uma recipe do pack
(`packs/<slug>/recipes/<nome>.json`). Cada entrada de `components[]` vira um
elemento na mesma ordem:

```
{"c": "ds-headline", "area": "2 / 2 / 4 / 9", "slot": "item_headline",
 "editable": {"desc": "...", "min": 25, "max": 70}, "rot": 3,
 "tone": "muted", "size": "lg", "align": "right", "layer": true,
 "vertical": true, "static": true, "variable": "primary",
 "imageType": "generated", "slotName": "professionalPhoto",
 "circle": true, "cutout": true, "round": true, "textType": "instagramHandle"}
```

→ `c` vira a classe · `area` vira `style="grid-area: ..."` · `rot` vira
`transform: rotate(Ndeg)` no mesmo style · demais chaves viram os `data-*`
correspondentes · `slot` diz QUAL conteúdo do dossiê entra ali. O agente
preenche conteúdo e `data-te-description`; não move áreas (única exceção: o
espelhamento sorteado no plano da fita, aplicado à recipe inteira), não muda
classes.
