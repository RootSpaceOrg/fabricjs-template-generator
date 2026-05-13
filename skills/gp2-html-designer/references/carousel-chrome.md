# Carousel chrome — progress bar + swipe arrow

UI consistente de navegação para carrosséis longos. Use **somente quando** o `brief.md` tem `## Carousel chrome: yes`.

Adaptado da skill `instagram-carousel` (https://github.com/marcolang/Marketing-Skills) para o contrato HTML→Fabric da pipeline v2:

- Coordenadas em **px reais** do canvas (ex: 1080×1350), não em px de viewport reduzida.
- Sem `inset` (o converter HTML→Fabric pode interpretar mal). Use `top/left/right/bottom` explícitos quando precisar, **mas prefira `position: absolute; left/top/width/height;`** que é a regra dura do `CLAUDE_DESIGN_RULES.md`.
- Sem dependência de variáveis CSS — interpole hexs literais.
- Marcação semântica para o `gp2-template-marker` aplicar `data-static="true"`.

## Quando usar

| Sequência | Default em `auto` |
|-----------|-------------------|
| Standard | `yes` |
| Tutorial | `yes` |
| Listicle | `yes` |
| Comparação | `no` |
| Single-post | `no` (1 slide só, chrome é ruído) |

Quando `yes`:

- Adicione **progress bar** em **todos** os slides.
- Adicione **swipe arrow** em **todos** os slides **exceto o último**.
- O contador "N/T" acompanha a barra.

Quando `no`: nenhum chrome. Pule esta referência.

## Cores adaptadas a slide LIGHT vs DARK

| Elemento | Sobre LIGHT | Sobre DARK |
|----------|-------------|------------|
| Track da progress bar | `rgba(0,0,0,0.08)` | `rgba(255,255,255,0.12)` |
| Fill da progress bar | `<BRAND_PRIMARY>` (hex literal) | `#FFFFFF` |
| Counter "N/T" | `rgba(0,0,0,0.30)` | `rgba(255,255,255,0.40)` |
| Background da swipe arrow | `rgba(0,0,0,0.06)` | `rgba(255,255,255,0.08)` |
| Stroke do chevron | `rgba(0,0,0,0.25)` | `rgba(255,255,255,0.35)` |

Sobre **slide Brand** (primary sólido ou gradient): use as cores de DARK (mais legíveis sobre cor saturada).

## Dimensões para canvas 1080×1350

(Para outros canvas, escale proporcionalmente.)

| Elemento | Coordenadas (1080×1350) |
|----------|-------------------------|
| Container da progress bar | `left: 56px; top: 1280px; width: 968px; height: 16px;` |
| Track (linha cinza) | `left: 56px; top: 1287px; width: 920px; height: 3px; border-radius: 2px;` |
| Fill (barra colorida) | dentro do track, `width: <pct>%` (`pct = (slideIndex+1)/totalSlides * 100`) |
| Counter "N/T" | `left: 990px; top: 1280px; width: 60px; height: 16px; text-align: right;` |
| Container da swipe arrow | `left: 1008px; top: 540px; width: 72px; height: 270px;` (centrado vertical no slide 1350) |
| Chevron SVG | `left: 1032px; top: 663px; width: 24px; height: 24px;` (centrado dentro do container) |

## Snippets HTML prontos

### Progress bar (slide LIGHT, exemplo: slide 3 de 7)

```html
<!-- Track -->
<div data-static="true"
     style="position:absolute; left:56px; top:1287px; width:920px; height:3px;
            background:rgba(0,0,0,0.08); border-radius:2px;"></div>

<!-- Fill (3/7 = 42.86%) -->
<div data-static="true"
     style="position:absolute; left:56px; top:1287px; width:394px; height:3px;
            background:#4285F4; border-radius:2px;"
     data-variable="primary" data-variable-target="background"></div>

<!-- Counter -->
<p data-static="true"
   style="position:absolute; left:990px; top:1280px; width:60px; height:16px;
          font-family:'Inter'; font-size:11px; font-weight:500;
          color:rgba(0,0,0,0.30); text-align:right; line-height:16px;">3/7</p>
```

### Progress bar (slide DARK)

```html
<div data-static="true"
     style="position:absolute; left:56px; top:1287px; width:920px; height:3px;
            background:rgba(255,255,255,0.12); border-radius:2px;"></div>

<div data-static="true"
     style="position:absolute; left:56px; top:1287px; width:394px; height:3px;
            background:#FFFFFF; border-radius:2px;"></div>

<p data-static="true"
   style="position:absolute; left:990px; top:1280px; width:60px; height:16px;
          font-family:'Inter'; font-size:11px; font-weight:500;
          color:rgba(255,255,255,0.40); text-align:right; line-height:16px;">3/7</p>
```

Note: no slide DARK o fill é branco e **não** recebe `data-variable` — branco é neutro literal, não deve trocar com brand preset.

### Swipe arrow (slide LIGHT)

```html
<!-- Background sutil (opcional — pode remover se preferir só o chevron) -->
<div data-static="true"
     style="position:absolute; left:1008px; top:540px; width:72px; height:270px;
            background:rgba(0,0,0,0.06); border-radius:0;"></div>

<!-- Chevron -->
<svg data-static="true"
     style="position:absolute; left:1032px; top:663px; width:24px; height:24px;"
     viewBox="0 0 24 24" fill="none">
  <path d="M9 6l6 6-6 6"
        stroke="rgba(0,0,0,0.25)" stroke-width="2.5"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### Swipe arrow (slide DARK)

```html
<div data-static="true"
     style="position:absolute; left:1008px; top:540px; width:72px; height:270px;
            background:rgba(255,255,255,0.08); border-radius:0;"></div>

<svg data-static="true"
     style="position:absolute; left:1032px; top:663px; width:24px; height:24px;"
     viewBox="0 0 24 24" fill="none">
  <path d="M9 6l6 6-6 6"
        stroke="rgba(255,255,255,0.35)" stroke-width="2.5"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### Último slide

**Não emita** o swipe arrow no último slide. A progress bar fica com `width = 100%` (fill cobrindo o track inteiro).

## Cálculo do fill da progress bar

Para um carrossel com `T` slides (1-indexed), o fill do slide N é:

```
fillWidth = round(920px × N / T)
```

Exemplos para T=7:

| Slide N | fillWidth |
|---------|-----------|
| 1 | 131px |
| 2 | 263px |
| 3 | 394px |
| 4 | 526px |
| 5 | 657px |
| 6 | 789px |
| 7 | 920px (100%) |

## Regras de marcação para o `gp2-template-marker`

Todo elemento do chrome recebe `data-static="true"`. Especificamente:

| Elemento | Atributos |
|----------|-----------|
| Track da progress bar | `data-static="true"` (decoração estática) |
| Fill da progress bar (slide LIGHT) | `data-static="true"` + `data-variable="primary" data-variable-target="background"` |
| Fill da progress bar (slide DARK) | `data-static="true"` (sem variable — branco é neutro) |
| Counter "N/T" | `data-static="true"` |
| Background da swipe arrow | `data-static="true"` |
| Chevron SVG | `data-static="true"` |

Esses elementos **nunca** são `data-template-element` — não mudam por post.

## Por que não usamos `bottom`/`right`/`inset`

O `CLAUDE_DESIGN_RULES.md` exige `position: absolute` com `left/top/width/height` em px. O converter HTML→Fabric calcula `cx = left + width/2` e `cy = top + height/2` para emitir `originX: "center", originY: "center"`. Se você usar `bottom: 20px`, o converter não consegue calcular `top` sem renderizar o DOM.

**Sempre** converta: `bottom: 20px` em canvas 1350 → `top: 1330 - height`. Idem para `right` em canvas 1080 → `left: 1080 - right - width`.

## Adaptação para outras dimensões

| Canvas | Progress bar y | Margem lateral | Swipe arrow x |
|--------|----------------|----------------|---------------|
| 1080×1080 (Feed quadrado) | `top: 1010` | `left: 56` | `left: 1008` |
| 1080×1350 (Feed retrato) | `top: 1280` | `left: 56` | `left: 1008` |
| 1080×1920 (Stories/Reels) | `top: 1830` | `left: 56` | `left: 1008` |

Mantém ~50px de margem do rodapé e ~28px da borda direita em qualquer formato.

## Por que tudo isso vale o esforço

Carrossel longo (5+ slides) sem progress bar deixa o usuário perdido. Slide-counter no rodapé mostra "estou na metade", "falta 1", criando senso de progresso. Seta de swipe é affordance — diz "tem mais aqui". Em conteúdo educativo (Tutorial, Listicle, Standard), isso aumenta retenção entre slides.

Em carrosséis curtos (Comparação 5 slides) ou Single-post, o chrome compete visualmente com o conteúdo principal — daí ser opt-in.
