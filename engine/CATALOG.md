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
         Só data-static + data-layer (imagem/forma/watermark). Editável é
         proibido por padrão: a travessia é DUPLICADA nos slides vizinhos, e
         dois campos independentes no editor dessincronizam. `data-split-ok`
         na camada libera — para packs cujo conteúdo É a travessia (cartões
         contínuos), assumindo que quem edita sabe que são duas metades.
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
  demais `item` (gate do runner). **Peça única** (fita de 1 slide, ex. data
  comemorativa): a seção usa `data-role="unica"`.
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
| `ds-cta` | texto | `roundedRect` (fill) + `textbox` | pill preenchida 1→2, com respiro lateral. **É AÇÃO** — usar só onde o leitor pode agir (capa: "arrasta"; fechamento: salvar/comentar/compartilhar). Rótulo decorativo em cartão de miolo é `ds-eyebrow`/`ds-stamp`, nunca CTA |
| `ds-block` | container | `roundedRect` + filhos | bg do acento (`data-tone="ink"` = preto); filhos são componentes do catálogo; `data-overlay` (+`data-layer`) = véu escurecedor (ink 42%) sobre foto full-bleed — nunca tinge de acento; `data-overlay-gradient="primary|secondary"` (+`data-layer`) = véu em GRADIENTE transparente→cor VARIÁVEL do usuário (recolorido por stop na plataforma) |
| `ds-card` | container | `roundedRect` + filhos | cartão no papel, cantos `--radius`; `data-elevated` = sombra de cartão empilhado (shadow no Fabric) |
| `ds-shape` | vazio | `roundedRect` (cantos por lado; anel = stroke) | forma de composição: `data-shape="circle\|ring\|pill"`; cor via `data-tone`; `data-half="left\|right"` na BORDA do slide cria transição — o par complementar no slide vizinho completa a forma na fita |
| `ds-photo` | `<img>` | `ClippableImage` | imagem gerada/evidência; `data-image-type` obrigatório. Aceita `.svg` como arquivo — **só para geometria, ver regra abaixo** |
| `ds-slot` | `<img>` | `ClippableImage` | slot da plataforma: `data-slot="professionalPhoto\|instagramProfilePicture\|logo"` (vira `imageType`); `data-circle` para avatar, `data-cutout` para cutout ancorado na base. **`professionalPhoto` NUNCA leva `data-round`** (gate no conversor): o runtime troca o slot por um recorte de pessoa com fundo transparente, e canto arredondado corta a figura. **`data-cutout` ancora na base DA ÁREA, não do slide**: a célula tem que terminar na linha 13, senão a figura flutua no meio |

Modificadores globais: `data-tone` (ink/muted/accent/paper/accent-ink) ·
`data-align` (center/right) · `data-round`/`data-circle` (imagens) ·
`data-overhang="top|bottom|tl|tr|bl|br"` (decor: imagem inteira sem crop, deslocada parcialmente para fora do slide — cortada pela borda, rotação embutida; usar junto com data-cutout. **Sangra para FORA da fita, não na emenda**: overhang com `r`/`br`/`tr` num slide que tem vizinho à direita corta a imagem no meio da fita e ela não continua no próximo — para atravessar a emenda, o elemento vai na `.fita-layer`) · `data-case="sentence"` (desliga uppercase) · `data-square` (ds-cta vira tarja de cantos retos) · `data-inset="bottom|top"` (respiro de 36px da borda sem mudar a célula) · `data-fit="start|end"` (**ds-card/ds-block**: a caixa encolhe até o conteúdo em vez de esticar na célula — a célula vira o espaço máximo; `end` ancora no rodapé da célula, `start` no topo. Use sempre que o texto for curto para a área: é o que impede cartão com 60% de vão) · `data-size="lg"` (ds-number e ds-headline) · `data-face="serif"` (voz serif do pack via `--font-serif`, sentence case).

## data-* de metadados

| Atributo | Efeito no JSON |
|----------|----------------|
| `data-el-id="eN"` | `elId` — obrigatório em TODO componente (lei de conservação) |
| `data-template-element` + `data-te-description` + `data-te-min-chars`/`data-te-max-chars` (texto) | `isTemplateElement: true` + `templateElement{...}` — min/max obrigatórios em texto editável |
| `data-te-remove-bg="true\|false"` (imagem editável) | `templateElement.removeBackground` |
| `data-static` | sem templateElement |
| `data-text-type="instagramName\|instagramHandle\|phone\|address"` | `textType` (exclusivo com template-element) |
| `data-image-type` | `imageType` (em `ds-slot` o default é o valor de `data-slot`) |
| `data-variable="primary\|accent"` (+ `data-variable-target="background"` na section) | `fillVariableConfig` / background variável. Vale em caixa, forma, texto E **em `<span>` dentro de texto** — o span vira `fillVariableConfig` por caractere no `styles`, que é como o duo-tom recolore com a marca. **`accent` sai como `secondary` no JSON** — a fábrica fala pelo PAPEL (cor principal / cor de destaque), a plataforma guarda como primary/secondary. Variável fora dessas duas é rejeição. `data-variable-alpha="0.85"` (também no span) dá um SEGUNDO PESO da mesma cor — é como se faz duo-tom sem depender de `secondary`, que na maioria dos tenants é uma cor bem diferente da primary |

## SVG — só geometria de composição, NUNCA imagem

SVG entra como **arquivo** num `<img class="ds-photo" data-static src="arcos.svg">`
(inline, `<svg>` no HTML, segue rejeitado).

Vira **`group` de vetores** no JSON — `circle`/`path`/`line` de verdade, cada um
com seu `stroke`, com `name: "SVG"`. É o mesmo objeto que o editor produz quando
o usuário insere um SVG (`loadSVGFromURL` + `groupSVGElements`), então o motor
usa o **fabric 5.5.2**, a mesma versão do frontend. Traço permanece nítido em
qualquer escala; como imagem ele rasterizaria.

`group` é o ÚNICO caso em que o validador aceita grupo — qualquer outro continua
proibido (grupo vira objeto que o usuário não edita por slot). Dois gates no
convert: SVG **precisa** de `data-static` (editável = imagem, use png/jpg) e não
pode conter `<image>`, `xlink:href` ou `<text>`.

**Use para** o que CSS não expressa: arco parcial, traço que entra e sai do
quadro, curva em ângulo, moldura de formato irregular, cartão com recorte
próprio, divisória diagonal. É geometria de composição — fundo, forma, moldura.

**NUNCA use para imagem**: ilustração, figura, ícone desenhado, textura, cena,
qualquer coisa que devesse ser foto ou asset gerado. Já houve problema com
imagem em SVG na plataforma; imagem é `.png`/`.jpg` gerado, sem exceção.

A régua na dúvida: se o arquivo tem mais que formas geométricas simples
(`circle`, `rect`, `path`, `line`) com traço ou preenchimento chapado, não é
geometria — é imagem, e está no lugar errado.

## REJEITADO (erro, nunca chute)

Texto (filho direto do slide) cujo conteúdo é mais alto que a própria célula —
o render invadiria o vizinho ·

Classe fora do catálogo · elemento visível sem `data-el-id` · inline style além
de `grid-area`/`transform:rotate` · sobreposição de componentes não-camada ·
SVG **inline** (`<svg>` no HTML)/canvas/video/iframe · `background-image:url()` (imagem é `<img>`) ·
gradiente radial/conic · mix-blend-mode/backdrop-filter/mask · pseudo-elemento
com conteúdo · texto editável sem `data-te-min-chars`/`max-chars` · `ds-photo`
sem `data-image-type` · texto com `writing-mode` vertical.

## Composição (designer)

O designer compõe a fita inteira de uma vez, com o conhecimento em camadas:
`knowledge/design/geral.md` (leis de qualquer pack) → `packs/<slug>/`
(tecnicas.md, exemplos/, tokens, lessons.md — o estilo) → o dossiê do copy.
Gerações do mesmo pack DEVEM variar: os exemplos do pack são ponto de partida,
nunca fôrma. O que é lei está neste catálogo e nos gates; o resto é design.
