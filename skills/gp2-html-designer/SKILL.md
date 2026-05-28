---
name: gp2-html-designer
description: "Coração da Pipeline v2: gera HTML/CSS para posts e carrosséis em 3 passos materializados — Passo 1 low-fi (estrutura + copy + tipografia, neutros), Passo 2 mid-fi (paleta + data-variable + imagens reais), Passo 3 high-fi (carousel moves + delight details). Cada passo produz template-vN.html + screenshots e auto-critique antes de avançar. Consome arquétipos A* (_shared/COMPOSITIONS.md) e moves M* (_shared/CAROUSEL_MOVES.md) declarados pelo art-director. Quando ambiguidade do plano trava execução, pode reportar status: blocked-on-art-director. Não converte para Fabric, não publica. Use após gp2-art-director, antes de gp2-html-reviewer."
---

# gp2-html-designer

Geração de HTML/CSS para templates de social media.

## Princípio

O designer lê o brief e o visual-plan como orientação — não como contrato de execução linha a linha. O objetivo é produzir um template visualmente forte, coerente e publicável. Se a direção do visual-plan faz sentido, siga-a. Se durante a construção surgir uma solução melhor, use-a e documente em `notes.md`.

## Inputs

- **`brief.md`** produzido por `gp2-request-interpreter` — copy por slide, tom, segmento, arco narrativo, foto profissional.
- **`visual-plan.md`** produzido por `gp2-art-director` — orientação visual: paleta com hexs concretos, **escala tipográfica resolvida**, **arquétipo A* por slide** ([`../_shared/COMPOSITIONS.md`](../_shared/COMPOSITIONS.md)), **carousel moves M*** ([`../_shared/CAROUSEL_MOVES.md`](../_shared/CAROUSEL_MOVES.md)), mapeamento de data-variable. Use como ponto de partida — designer adapta na execução, mas mantém arquétipos e tipografia.
- Opcionalmente em reference-driven mode: imagens de referência no contexto para detalhe visual.

**Leia os dois antes de escrever qualquer HTML.**

## Output esperado

```
artifacts/gp2-html-designer/<slug>/
├── template-v1-lowfi.html          ← Passo 1: estrutura + copy + tipografia
├── screenshots-v1-lowfi/slide-N.png
├── template-v2-midfi.html          ← Passo 2: paleta + data-variable
├── screenshots-v2-midfi/slide-N.png
├── template.html                   ← Passo 3: high-fi final
├── screenshots/slide-N.png
└── notes.md                        ← 3 critiques + decisões + desvios
```

## Workflow — 3 passos materializados

A pipeline executa 3 passos com entregáveis distintos, cada um renderizado e auto-criticado antes de avançar. **Não pule passos.** O ganho do loop de 3 etapas é exatamente a revisão entre elas — replica o ciclo "ver → corrigir → ver" do Claude Design.

### 0. Leia e internalize

Antes de qualquer passo, leia `brief.md` + `visual-plan.md` inteiros e abra [`../_shared/COMPOSITIONS.md`](../_shared/COMPOSITIONS.md) nos arquétipos declarados + [`../_shared/CAROUSEL_MOVES.md`](../_shared/CAROUSEL_MOVES.md) nos moves declarados. Entenda:
- O arco narrativo (slide a slide)
- A paleta concreta (hexs)
- A escala tipográfica resolvida (famílias, pesos, tamanhos)
- O arquétipo A* declarado para cada slide
- Os 1–2 carousel moves M* e em quais slides aparecem
- O mapeamento de data-variable
- Tom, segmento, foto profissional

---

### Passo 1 — Low-fi: estrutura + copy + tipografia

Produza `template-v1-lowfi.html`. Aplique:
- **Estrutura HTML completa** (section por slide, position:absolute, todo o esqueleto que vai virar o final).
- **Esqueleto do arquétipo A* declarado** para cada slide. Consulte os anchors em `COMPOSITIONS.md` e posicione headline-zone, image-zone, decorator-zone, cta-zone conforme. Adapte coords exatas, mantenha as proporções.
- **Copy real do brief** já posicionado nos slots.
- **Tipografia resolvida do visual-plan** aplicada (famílias via `<link>` Google Fonts, pesos, tamanhos, tracking).
- **Sem cor de marca**, **sem movimento decorativo M***. Fundos: off-white claro (`#F5F3EF`) e near-black (`#1C1A18`). Acentos: cinza médio com tint do brief.
- Blocos de imagem como retângulos neutros placeholder (`#D8D4CC`), sem fotos reais ainda.

Esqueleto inicial:
```html
<!doctype html>
<html lang="pt-BR" data-template-name="<slug>" data-segment="<segmento-kebab-case>">
<head>
  <meta charset="utf-8">
  <meta name="hm-fonts" content="FonteDisplay,FonteBody">
  <link href="https://fonts.googleapis.com/css2?family=FonteDisplay:wght@700;800&family=FonteBody:wght@400;500&display=swap" rel="stylesheet">
</head>
<body style="margin:0; padding:0;">
  <section class="slide" data-width="1080" data-height="1350"
           style="position:relative; width:1080px; height:1350px; overflow:hidden; background:#F5F3EF;">
    <!-- aplique anchors do arquétipo A1/A2/A3... declarado para slide 1 -->
  </section>
  <!-- demais slides, cada um com seu arquétipo -->
</body>
</html>
```

Renderize:
```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/ --variant v1-lowfi
```

**Auto-critique do Passo 1** — escreva em `notes.md` seção `## Passo 1 — critique`:
- Hierarquia tipográfica é instantânea em cada slide?
- Copy cabe nos slots sem overflow?
- Cada slide reflete claramente o arquétipo A* declarado (anchors visíveis)?
- Slides têm composições distintas (variedade de arquétipos visível)?
- Respiração ≥60px nas bordas?

Se algum NÃO → corrija no v1-lowfi antes de avançar. **Máx 1 retry.** Se a falha for em decisão do plano (não algo que você possa corrigir sozinho), siga para "Pedidos ao art-director" abaixo.

---

### Passo 2 — Mid-fi: paleta + data-variable

Copie `template-v1-lowfi.html` → `template-v2-midfi.html`. Aplique:
- **Paleta do visual-plan** nos fundos brand/CTA, eyebrow, acentos, fios.
- **`data-variable`** + `data-variable-target` em todos os elementos do mapeamento (`primary` / `secondary`).
- **`data-darken`** em overlays de escurecimento (fundo brand + atmosférico, legibilidade sobre foto). **`data-glow`** se o plano pediu glow atmosférico.
- **Imagens reais**:
  - `userAsset` → URL determinística `picsum.photos/id/{N}/{w}/{h}` ou base64 de `references/placeholders/image-placeholder.b64.txt`.
  - `professionalPhoto` → base64 de `references/placeholders/professional-photo-1.b64.txt` ou `professional-photo-2.b64.txt`.
- Ainda **sem** os moves M* nem ornamentação decorativa (próximo passo).

Renderize:
```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/ --variant v2-midfi
```

**Auto-critique do Passo 2** — escreva em `notes.md` seção `## Passo 2 — critique`:
- Contraste WCAG OK em todos os slides (texto sobre fundo)?
- `data-variable` cobre todos os elementos mapeados?
- Slides parecem do mesmo carrossel (coerência visual com a paleta aplicada)?
- Foto profissional ancorada corretamente (object-fit:contain, object-position:bottom center, sem texto sobre face)?
- Overlays escurecimento têm `data-darken` + opacidade adequada?

Se algum NÃO → corrija no v2-midfi antes de avançar. **Máx 1 retry.**

---

### Passo 3 — High-fi: carousel moves + delight

Copie `template-v2-midfi.html` → `template.html` (entrega final). Aplique:
- **Carousel moves M*** declarados no visual-plan, nos slides indicados:
  - `M2-numero-ostentatorio` → número 300–500px no canto.
  - `M4-cta-arrow-ritualistico` → seta "→" em todos exceto último, mesma posição.
  - `M8-fio-tipografico` → fio 1–3px abaixo de cada eyebrow/título.
  - etc. (consultar `CAROUSEL_MOVES.md` para snippets).
- **Delight details** — pelo menos 1 identificável: tracking notável no eyebrow (+12% / +20%), contraste forte de peso (400 vs 800 juntos), número editorial sobreposto, color block intencional, ligadura/ornamento, sobreposição calculada.
- Ajustes finais de spacing, alinhamento, micro-tipografia.

Renderize sem `--variant` (output final):
```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/
```

**Auto-critique do Passo 3** — escreva em `notes.md` seção `## Passo 3 — critique`:
- Cada move M* declarado tem evidência visual nos slides indicados?
- Há pelo menos 1 delight detail identificável? Liste qual(is).
- O carrossel tem identidade — não parece template default de IA?
- Ainda respeita estrutura e contraste do passo 2 (nenhuma regressão)?

Se algum NÃO → corrija no final antes de devolver ao reviewer. **Máx 1 retry.**

---

### Pedidos ao art-director (uso parco)

Se durante qualquer passo você encontrar ambiguidade real no visual-plan que trava a execução, escreva em `notes.md` seção `## Pedidos ao art-director`:

```markdown
## Pedidos ao art-director
- [Slide 3] Arquétipo A1-hero-split foi declarado mas o copy do brief tem 4 linhas longas — não cabe no slot. Sugestão: trocar para A10-headline-massive-solo neste slide, ou encurtar copy.
- [Geral] Paleta primary=#FF6B35 + secondary=#FF8C42 dá contraste fraco entre acentos. Confirma se foi intencional ou se um deles deve mudar.
```

Não invente respostas. Pare o passo, reporte ao orquestrador `status: blocked-on-art-director` e aguarde.

**Use com parcimônia.** Pedidos válidos: contradição factual no plano, copy que não cabe, contraste impossível, arquétipo incompatível com conteúdo. Pedidos inválidos: preferência estética sua, dúvida que você pode resolver lendo o plano com atenção.

---

### Verificação estrutural (rodar antes de cada render)

| Verificação | Esperado |
|-------------|----------|
| `<html data-template-name="..." data-segment="...">` | Presente |
| `<meta name="hm-fonts" content="...">` | Presente com todas as famílias usadas |
| Cada slide tem `<section class="slide" data-width="N" data-height="M">` | Presente |
| Cada slide tem `style="position:relative; width:Npx; height:Mpx;"` | Presente |
| Cada elemento interno tem `style="position:absolute; left:Xpx; top:Ypx; ..."` | Presente |
| Sem `<style>` block no `<head>` com regras CSS | Ausente |
| Sem `class="..."` dependendo de `<style>` block | Ausente |

Se qualquer item falhar → corrija antes de renderizar. Screenshots de HTML inválido não têm valor de revisão.

## Regras de HTML invioláveis

As 13 regras técnicas (estrutura, CSS inline, gradientes obrigatoriamente com `data-darken`/`data-glow`, fontes declaradas em `<meta hm-fonts>`, etc.) vivem em [`../_shared/HTML_TECHNICAL_SPEC.md`](../_shared/HTML_TECHNICAL_SPEC.md). **Leia antes de escrever HTML.** Resumo do que o designer aplica diretamente:

- `<html data-template-name="<slug>" data-segment="<segmento-kebab-case>">` + `<meta name="hm-fonts">` listando todas as famílias.
- Uma `<section class="slide" data-width data-height>` por slide; tudo dentro com `position: absolute` em px.
- CSS sempre inline; sem `<style>` blocks, sem classes CSS, sem pseudo-elementos/animations/blend-modes.
- `font-weight` numérico (400/600/700) — nunca `bold`.
- Imagens reais (`<img>`), nunca CSS shapes simulando foto.
- Gradiente em qualquer elemento → obrigatório `data-darken` (escurecimento neutro) ou `data-glow` (brand atmosférico). Cores brand hex em `linear-gradient` são proibidas.

## Imagens — fluxo determinístico via buckets B1–B4

**Antes de qualquer decisão de imagem, leia `visual-plan.md → ### Imagens declaradas`.** O art-director já classificou cada imagem em B1 (slot da plataforma), B2 (URL picsum determinística), B3 (placeholder obrigatório) ou B4 (não replicar). Seu papel é **executar** a classificação, não revisitar.

Se a tabela `### Imagens declaradas` está ausente ou incompleta, **pare e reporte `status: blocked-on-art-director`** com `## Pedidos ao art-director: tabela de Imagens declaradas faltando` no `notes.md`. Não improvise.

### B1 — slot da plataforma

Use o atributo declarado pelo art-director. O conteúdo é preenchido pelo usuário em runtime; no template, use o placeholder visual correspondente:

| `data-image-type` | Placeholder a embutir |
|-------------------|------------------------|
| `professionalPhoto` | `references/placeholders/professional-photo-{1\|2}.b64.txt` (o brief sugere qual) |
| `brandLogo` | `references/placeholders/logo-quadrada.b64.txt` |
| `instagramProfilePicture` | `references/placeholders/logo-quadrada.b64.txt` (genérico circular) |

```html
<img data-image-type="professionalPhoto" alt="Foto do profissional"
     style="position:absolute; left:0; top:300px; width:540px; height:1050px;
            object-fit:contain; object-position:bottom center;"
     src="data:image/png;base64,iVBORw0KGgo...">
```

### B2 — imagem genérica buscável (URL picsum)

Use a URL `picsum.photos/id/{ID}/{width}/{height}` **exatamente como declarada** no `visual-plan.md`. Não troque o `id`, não adicione query string.

**Regras:**
- Sempre use URLs determinísticas — mesma URL = mesma imagem em todo carregamento.
- Nunca use `?random=N`, `?grayscale`, `?blur` — fazem o CDN tratar cada request como novo.
- Nunca use `https://picsum.photos/{W}/{H}` sem `/id/{N}/` — retorna foto diferente a cada request.
- Nunca use `https://source.unsplash.com/` — deprecated.

```html
<img class="image-placeholder" alt="Foto contextual"
     style="position:absolute; left:60px; top:200px; width:480px; height:580px; object-fit:cover;"
     src="https://picsum.photos/id/1015/480/580">
```

Se a URL falhar em renderização local, **não** caia para placeholder silenciosamente — reporte ao art-director em `notes.md → ## Pedidos ao art-director: URL picsum id={N} não renderizou; sugira id alternativo ou mude para B3?`. O fallback automático mascara o problema.

### B3 — imagem específica não-reproduzível (placeholder obrigatório)

O art-director declarou `image-source: placeholder-required` porque o elemento da referência (símbolo de campanha, ilustração autoral, mascote, infográfico específico) **não existe** em banco público e **não** é slot. Use [`references/placeholders/image-placeholder.b64.txt`](./references/placeholders/image-placeholder.b64.txt) direto, com `alt` descritivo:

```html
<img class="image-placeholder" alt="Símbolo Março Amarelo - laço de campanha"
     style="position:absolute; left:660px; top:80px; width:380px; height:1200px; object-fit:contain;"
     src="data:image/png;base64,iVBORw0KGgoAAAANS...">
```

**Regras hard de B3:**
- **Nunca** tente URL picsum para um slot B3 — o art-director já decidiu que é não-reproduzível.
- **Nunca** gere `<svg>` inline para "imitar" o símbolo (laço, fita, mascote, ilustração).
- **Nunca** use `<div>` com `background-color` / `background-image` / formas CSS para fingir o elemento.
- **Nunca** baixe base64 alternativo de outro arquivo que não seja `image-placeholder.b64.txt`.
- `alt` deve descrever o que o elemento representava na referência — ajuda o reviewer e o futuro humano que substituir a imagem.

Violar qualquer uma dessas regras é finding `b3-placeholder-violation` blocker no reviewer.

### B4 — não replicar

O elemento foi descartado pelo art-director (handle de outra marca, métrica de UI, selo verificado, etc.). **Não inclua no HTML.** Não tente "neutralizar" o elemento com texto genérico — simplesmente omita.

### Regra hard geral

**Nunca gere SVG inline inventado. Nunca use CSS shapes fingindo foto.** Imagem ausente no `### Imagens declaradas` do visual-plan = imagem ausente no HTML. Se faltou alguma, devolva ao art-director.

## Fotos profissionais (quando o brief pediu)

`professionalPhoto` é um slot **B1** declarado no `### Imagens declaradas` do visual-plan. Esta seção complementa B1 com positioning + anti-patterns específicos do cutout.

Tratamento padrão: **PNG cutout** (figura com fundo transparente). Use `object-fit: contain; object-position: bottom center; border-radius: 0;`. Avatar circular **só** se a referência/pedido pedir explicitamente.

Posições disponíveis e snippets prontos: [`references/professional-photo-placements.md`](./references/professional-photo-placements.md). Padrões cobertos:

1. **Hero cover full-figure** — slide 1, foto na coluna direita/esquerda ocupando ~50% largura × 88% altura.
2. **CTA final lateral** — último slide, foto ~37% largura ao lado do CTA.
3. **Overlap sobre foto contextual** — foto profissional sobreposta no canto da imagem de apoio.

Placeholders visuais (base64): [`references/placeholders/`](./references/placeholders/).
- `professional-photo-1.b64.txt` — masculino, traje formal/jaleco.
- `professional-photo-2.b64.txt` — feminino, traje casual/blazer.

```html
<img class="professional-photo" alt="Foto profissional"
     data-image-type="professionalPhoto"
     style="position:absolute; left:540px; top:80px; width:540px; height:1200px;
            object-fit:contain; object-position:bottom center; border-radius:0;"
     src="data:image/png;base64,<conteúdo de professional-photo-N.b64.txt>">
```

Anti-patterns críticos:
- **`object-fit: cover` em cutout** — corta pés/cabeça.
- **`border-radius` arredondado em cutout** — mostra fundo recortado sobre a figura.
- **Texto sobre a face** (zona superior do slot, ~30%) — cobre o que gera confiança.

## Gradientes — quando e como usar

Spec completa (8 presets de `data-darken`, glow brand via `data-glow`, sombras, anti-patterns) em [`../_shared/GRADIENT_SYSTEM.md`](../_shared/GRADIENT_SYSTEM.md). Em resumo:

- **Background brand** = fundo sólido `primary` na `<section>` + `<div>` overlay com `data-darken="<preset>" data-darken-opacity="N"`. Nunca brand hex dentro de `linear-gradient`.
- **Overlay de legibilidade sobre foto** = `<div data-static="true" data-darken="bottom"...>`. Opacidade orientativa: `0.65–0.80` para texto 400; `0.45–0.60` para texto 700+.
- **Glow atmosférico** (opt-in) = `<div data-glow="center" data-glow-variable="primary|secondary" data-glow-alpha="0.x" data-static="true">` com `radial-gradient(circle, rgba(...), transparent)` + `border-radius:50%`. Sem esses atributos, círculo translúcido vira fill sólido no Fabric.
- **Sombras**: `box-shadow` sempre `rgba(0,0,0, opacity)`. Nunca hex brand.

Exemplo — fundo brand com escurecimento atmosférico:

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

## Logo da marca (`brandLogo`)

**Default canônico**: aplique logo em **slide 1 (capa)** e **último slide (CTA)**. Em outros slides, só se houver espaço limpo sobrando. Quando o `visual-plan.md` declarar posições específicas ou o brief pedir explicitamente outras presenças, siga o plano — caso contrário, este default é o piso.

Use [`references/placeholders/logo-quadrada.b64.txt`](./references/placeholders/logo-quadrada.b64.txt) como `src`. Em produção o runtime substitui pelo logo real do brand config do usuário.

```html
<img class="brand-logo" alt="Logo da marca"
     data-image-type="brandLogo"
     style="position:absolute; left:60px; top:1150px; width:140px; height:140px;
            object-fit:contain; object-position:center; border-radius:0;"
     src="data:image/png;base64,<conteúdo de logo-quadrada.b64.txt>">
```

**Regras essenciais** (catálogo completo de padrões e coords em [`references/placeholders/README.md`](./references/placeholders/README.md) §"Logo da marca"):

- **Tamanho:** quadrado entre 80–240px. Default 120–140px nas extremidades.
- **Sempre ancorado em uma borda real**: encosta na esquerda OU direita do slide (margem ≤ 32px da borda). Logo centralizado horizontalmente fica como "selo solto".
- **Vertical:** rodapé para CTA (`top + height ≥ data-height − 32px`); header para capa (`top ≤ 32px`). Nunca no meio do slide (compete com headline).
- **Nunca** sobre headline, body ou foto profissional. Se o único espaço limpo conflita com texto, prefira não colocar logo nesse slide.
- **Object-fit:** `contain` + `object-position: center`. **Border-radius:** `0` (slot neutro).

## Famílias tipográficas

Use as famílias declaradas em `visual-plan.md → ## Tipografia resolvida`. Carregue ambas (display + body) via `<link>` Google Fonts no `<head>` e liste em `<meta name="hm-fonts">`. Pesos e tamanhos seguem a escala resolvida — designer ajusta detalhe (±10% no tamanho, kerning fino) mas não troca família nem inverte hierarquia. Para inspiração de combinações editoriais por estilo, consulte [`references/aesthetic-families.md`](./references/aesthetic-families.md).

## Anti-patterns de composição

O reviewer flagra cada item abaixo como finding determinístico. Evite no design:

- **Card spam**: ≥3 elementos no mesmo slide com `border` + `border-radius` + `box-shadow` simultaneamente.
- **Nested cards**: cartão com `border` contendo outro card com `border`.
- **Lazy centering**: 100% dos textos do slide com `text-align: center` E posicionados na coluna central.
- **Cinzas frios**: literais `#CCCCCC`, `#999999`, `#666666` em fundo ou texto principal (sem saturação, percebido como frio).
- **Gradiente genérico**: roxo→rosa, azul→roxo, sem propósito declarado.
- **Slides idênticos**: 3+ slides consecutivos com mesmo arquétipo A*.
- **Move ausente**: M* declarado no plano mas sem evidência visual no HTML.
- **Arquétipo silencioso**: HTML que não corresponde ao A* declarado, sem nota em `notes.md`.

## O que esta skill NÃO faz

- Não adiciona `data-template-element`, `data-image-type`, `data-text-type`, `data-static`. Isso é trabalho do `gp2-template-marker`. (Exceção: `data-variable` é aplicado pelo designer conforme mapeamento do visual-plan.)
- Não gera Fabric JSON.
- Não faz upload.

## Resposta final ao orquestrador

Caminho normal (após Passo 3 concluído):
```markdown
HTML final: `<path>/template.html`
HTML intermediários: `<path>/template-v1-lowfi.html`, `<path>/template-v2-midfi.html`
Slides: <N>
Formato: <W>x<H>
Família(s) tipográfica(s): <display> + <body>
Paleta aplicada: primary <hex> / secondary <hex> / neutros <hexs>
Arquétipos executados: slide1=A?, slide2=A?, ... (diversidade: <N> tipos distintos)
Moves aplicados: <M?, M?>
Desvios de arquétipo: <nenhum | slide N: A? declarado → A? executado por razão Y (ver notes.md)>
Delight details: <lista — ex: tracking-eyebrow-tight, numero-decorativo-slide-3>
Elementos data-variable aplicados: <N>
Foto profissional: <usada | não usada>
Screenshots finais: `<path>/screenshots/slide-N.png`
Screenshots intermediários: `<path>/screenshots-v1-lowfi/`, `<path>/screenshots-v2-midfi/`
Próximo passo: gp2-html-reviewer
```

Caminho bloqueado (pedido ao art-director):
```markdown
status: blocked-on-art-director
Passo onde parou: <1 | 2 | 3>
Pedidos: ver notes.md §"Pedidos ao art-director"
HTML produzido até aqui: `<path>/template-vN-*.html`
Screenshots: `<path>/screenshots-vN-*/`
Próximo passo: gp2-art-director (modo resposta)
```
