---
name: gp2-html-designer
description: "Coração da Pipeline v2: gera HTML/CSS para posts e carrosséis HealthMarket em 3 iterações renderizadas (low-fi → mid-fi → high-fi). Cada passo emite um snapshot, roda render headless via Playwright, faz auto-check sobre os screenshots, e refaz uma vez se falhar. Reproduz o loop visual do Claude Design dentro do openclaw. Aplica data-variable conforme mapeamento do art-director (o marker confirma). Não converte para Fabric, não publica. Use após gp2-art-director, antes de gp2-html-reviewer."
---

# gp2-html-designer

Geração de HTML/CSS para templates de social media usando o **protocolo de 3 renders** descrito em [`../../DESIGN_PRINCIPLES.md`](../../DESIGN_PRINCIPLES.md).

## Princípio

O design ruim da pipeline v1 não vem de regras erradas — vem de o designer escrever HTML sem nunca ver o que produziu até o reviewer fechar o ciclo. Claude Design ganha porque o autor itera no DOM renderizado durante o design.

A v2 explicita esse loop: low-fi → render → mid-fi → render → high-fi → render. O LLM passa a operar sobre evidência visual.

## Inputs

- **`visual-plan.md`** produzido por `gp2-art-director` — **é o contrato principal**. Define família estética, paleta com hexs, composição de cada slide, movimento memorável com instrução composicional, e mapeamento de data-variable.
- `brief.md` produzido por `gp2-request-interpreter` — copy por slide, tom, foto profissional, carousel chrome.
- Opcionalmente em reference-driven mode: imagens de referência originais no contexto — o `visual-plan.md` já contém todo o vocabulário visual extraído (família, paleta, tipografia, movimento, elementos editoriais), mas você pode re-inspecionar as imagens para detalhes visuais se necessário.

**Ordem de leitura obrigatória:** leia `visual-plan.md` primeiro. Ele é mais específico que o brief. Em caso de conflito, visual-plan.md prevalece (exceto em violações técnicas do CLAUDE_DESIGN_RULES.md).

## Dois modos (reflexo do art-director)

| Modo | Comportamento do designer |
|------|---------------------------|
| **Free mode** | Você **executa** o plano do art-director. Não escolhe família, paleta ou movimento memorável — eles já estão decididos no `visual-plan.md`. As 3 iterações servem para executar o plano bem. |
| **Reference-driven mode** | Idem — o `visual-plan.md` já contém o vocabulário visual completo extraído da referência (família, paleta, tipografia, movimento, elementos editoriais). Não há `reference-spec.md` separado. |

**Você NÃO decide mais:**
- Família estética — está no visual-plan.
- Paleta (hexs) — está no visual-plan.
- Composição de cada slide — está no visual-plan.
- Movimento memorável — instrução composicional completa no visual-plan.
- Quais elementos recebem `data-variable` — mapeamento explícito no visual-plan.

**Você ainda decide:**
- Tamanhos exatos de fonte (ajuste fino no Passo 3).
- Coordenadas absolutas em px (dentro das zonas definidas no plano).
- Tipografia exata (família definida no plano; você escolhe os pesos específicos e line-height).
- Detalhes de micro-alinhamento (Passo 3).

## Output esperado

```
artifacts/gp2-html-designer/<slug>/
├── template.html                ← versão final (high-fi)
├── template-v1.html             ← low-fi
├── template-v2.html             ← mid-fi
├── screenshots/
│   ├── v1-slide-1.png
│   ├── v2-slide-1.png
│   └── slide-1.png              ← final
└── notes.md                     ← decisões marcantes (família estética, papel cores, movimento memorável)
```

## Protocolo de 3 passos (OBRIGATÓRIO)

### Antes de começar: leia o visual-plan.md

Antes de escrever uma linha de HTML, leia `artifacts/gp2-art-director/<slug>/visual-plan.md` inteiro. Internalizo:
- A família estética e sua lógica visual
- Os hexs exatos de primary, secondary, neutros
- O tipo compositivo de cada slide (A1–A8) e as zonas de headline/imagem
- A instrução composicional do movimento memorável
- A tabela de mapeamento de data-variable

Execute o plano. Não improvise direção criativa.

### Passo 1 — Esboço estrutural (low-fi)

Objetivo: travar layout e ritmo respeitando as **composições do visual-plan** antes de pensar em estética.

Escreva `template-v1.html` com:

- `<!doctype html>` + `<html lang="pt-BR" data-template-name="<nome>" data-segment="<segmento>">`.
- `<meta charset="utf-8">` + `<meta name="hm-fonts" content="...">` (mesmo provisório).
- Uma `<section class="slide" data-width="W" data-height="H">` por slide, com `style="position:relative; width:Wpx; height:Hpx; background:#FFFFFF;"`.
- Posicionamento absoluto para todo elemento visual dentro de `.slide` (`position: absolute; left/top/width/height`).
- **Caixas cinzas placeholder** `#E5E5E5` no lugar de áreas de foto, ícone, bloco colorido. Sem `<img>` ainda — apenas `<div>` com background.
- Tipografia provisória: uma única família neutra (Aptos, Segoe UI, system-ui).
- **Copy real do brief** em cada slide (nada de Lorem Ipsum — você precisa sentir densidade real).
- **Zero cor de marca, zero gradiente, zero textura.**
- **Implemente o tipo compositivo** de cada slide conforme o visual-plan (A1–A8): se o plano diz A3 (split assimétrico) para o slide 2, o esboço já deve ter a divisão 40/60 com imagem e texto nas zonas corretas.

**⚠️ Gate de diferenciação v1 (OBRIGATÓRIO):** O template-v1 DEVE ter estas características que o diferenciam visivelmente dos passos seguintes:
- Fundo de todos os slides = `#FFFFFF` (branco puro). Nenhum fundo escuro, brand ou gradiente.
- Toda tipografia = uma única família system-ui. Sem Google Fonts, sem `<link>` de fonte.
- Toda cor de texto = `#333333`. Sem cores brand, sem variação tonal.
- Áreas de foto = `<div>` com `background: #E5E5E5`. Sem `<img>`, sem URLs.
- Nenhum `data-variable`, `data-variable-stops`, ou `data-variable-target`. Zero variáveis.
- Nenhum efeito: sem `box-shadow`, sem `opacity` parcial, sem gradiente, sem glow.
- CSS inline simples — sem `<style>` block complexo com classes reutilizáveis.

Se o template-v1 já tiver cores brand, gradientes, fontes finais ou imagens, **ele não é low-fi — é o template final disfarçado**. Refaça.

Renderize com:

```bash
node ../../scripts/render-html-screenshots.js artifacts/gp2-html-designer/<slug>/
```

(Importante: o script espera `template.html`. No passo 1, copie temporariamente `template-v1.html` → `template.html` antes de renderizar, depois renomeie. Alternativa: rode o script apontando para uma pasta temporária.)

Olhe os screenshots e auto-check:

| Critério | OK se… |
|----------|--------|
| Hierarquia | título > subtítulo > corpo é instantâneo |
| Alinhamento | tudo encaixa numa grade implícita |
| Densidade | nenhum slide tem texto cortado ou apertado contra borda |
| Ritmo | slides têm composições visivelmente diferentes entre si (conforme os tipos A1–A8 do plano) |
| Respiração | margem útil ≥ 60px em todas as bordas (canvas 1080) |
| Fidelidade ao plano | cada slide usa a composição definida no visual-plan |

Se algo falhar, refaça **uma vez** (template-v1.1.html). Se ainda falhar, anote em `notes.md` e siga.

### Passo 2 — Atmosfera visual (mid-fi)

Objetivo: aplicar a paleta, tipografia e movimento memorável **conforme o visual-plan**.

**⚠️ Pré-condição:** Antes de começar o Passo 2, confirme que `template-v1.html` **não** tem cores brand, gradientes ou fontes finais. Se tem, o Passo 1 foi feito errado — o Passo 2 não tem o que evoluir. Volte ao Passo 1.

**⚠️ REGRA DE ESTILO INLINE (OBRIGATÓRIO em TODOS os passos):** Todo CSS deve estar nos atributos `style="..."` dos elementos. **PROIBIDO usar `<style>` blocks** no `<head>` com classes CSS. O conversor Fabric não consegue ler estilos de classes — apenas inline styles. Se você usar `.card { background: ... }`, o conversor perde cor, posição e gradiente desse elemento. O audit-template-markup.py bloqueia a pipeline se encontrar `<style>` blocks.

Em cima do `template-v1.html`, gere `template-v2.html` aplicando:

- **Paleta de marca — use os hexs do visual-plan, sem substituição:**
  - Slides LIGHT: fundo = neutro claro do plano
  - Slides DARK: fundo = neutro escuro do plano
  - Slides Brand: fundo = primary do plano (sempre sólido; para profundidade, usar overlay `data-darken`)
  - Neutros (branco, preto, cinza) **nunca** são brand variables.

- **Tipografia:**
  - Família display + body conforme a família estética do visual-plan (ver [`references/aesthetic-families.md`](./references/aesthetic-families.md) para stacks sugeridos por família).
  - Pesos explícitos (400, 600, 700, 800 — nunca só `bold`).
  - Se reference-driven: use as famílias nomeadas na seção "Tipografia (da referência)" do `visual-plan.md`. Se não disponível no Google Fonts, escolha a mais próxima da mesma categoria e anote em `notes.md`.

- **Movimento memorável — execute a instrução composicional do visual-plan:**
  - Aplique exatamente como descrito (posição, tamanho, fonte, cor, spacing).
  - Nos slides indicados em "Presença" do plano.
  - **Não invente um movimento diferente** — o plano já decidiu.

- **data-variable — aplique conforme o mapeamento do visual-plan:**
  - Para cada elemento listado na tabela de mapeamento, adicione os atributos `data-variable` e `data-variable-target` já no HTML do Passo 2.
  - Exemplo: se o plano diz "Fundo slides Brand/CTA → `data-variable="primary" data-variable-target="background"`", a `<section>` dos slides Brand já deve ter esse atributo desde o template-v2.html.
  - O marker vai **confirmar** esse mapeamento — não descobrir do zero. Não deixe para o marker deduzir o que o plano já explicitou.

- **Fotos**: uma `<img>` por região de imagem real. Se não tem asset real, siga o fluxo obrigatório: tente URL pública (picsum.photos), senão use `image-placeholder.b64.txt` (ver "Imagens contextuais" abaixo). **Nunca** SVG gerado inline, nunca divs fingindo foto.
- **Foto profissional**: respeite a decisão do brief + posição do visual-plan.
- **Carousel chrome (opt-in, não default)**: leia o valor exato em `## Carousel chrome` no `brief.md`. Se `yes`, consulte [`references/carousel-chrome.md`](./references/carousel-chrome.md) e adicione progress bar + seta de swipe (seta omitida no último slide), usando cores adaptadas a slide LIGHT/DARK/Brand e fill proporcional a `N/total`. Se `no`, **não invente chrome**.

Renderize e auto-check:

| Critério | OK se… |
|----------|--------|
| Contraste | texto sobre fundo respeita WCAG AA (≥ 4.5:1 para body) |
| Line-height | corpo ≥ 1.3; títulos podem ser 1.0–1.2 |
| Paleta | hexs do plano aplicados corretamente; primary tem papel consistente |
| Tipografia | display ≠ body; pesos explícitos; sem usar Inter/Arial/Roboto como única família |
| Movimento memorável | instrução do plano executada nos slides corretos |
| data-variable | elementos do mapeamento têm os atributos corretos no HTML |
| Composição | cada slide mantém o tipo A1–A8 definido no plano |
| Sem AI tells | não é tudo centralizado; não é card-spam; não é nested card |

Refaça **uma vez** (template-v2.1.html) se falhar. Se ainda falhar, anote e siga.

### Passo 3 — Polimento (high-fi)

Objetivo: detalhes finos que separam design "ok" de "publicável".

**⚠️ Gate de diferenciação v2→v3 (OBRIGATÓRIO):** O template.html DEVE ter pelo menos 3 diferenças visíveis em relação ao template-v2.html. Mudanças típicas do Passo 3: letter-spacing ajustado, tamanhos de fonte afinados, micro-alinhamentos corrigidos, opacidades sutis adicionadas, espaçamentos refinados. Se `diff template-v2.html template.html` não mostrar diferenças, o Passo 3 não aconteceu — refaça.

Em cima de `template-v2.html`, escreva `template.html` aplicando:

- **Tipografia fina**: letter-spacing negativo (-1% a -3%) em títulos grandes; pesos certos em pontos críticos (display 700-800, body 400-500); tamanhos ajustados para evitar quebras esquisitas.
- **Micro-alinhamentos**: pixel-perfect entre elementos relacionados (eyebrow alinhado com início do título, etc.).
- **Ritmo vertical**: aplicar escala 4/8/16/24/48/96 em vez de números aleatórios.
- **Profundidade tonal**: opacidades sutis (80%, 65%) em textos secundários quando faz sentido.
- **Verificação final** das regras invioláveis de HTML (ver abaixo).

Renderize uma última vez. Os screenshots em `screenshots/slide-N.png` (sem sufixo) são o que vai para o reviewer.

## Regras de HTML invioláveis (todos os 3 passos)

Vêm direto de [`../../CONTRACT.md`](../../CONTRACT.md) que aponta para `CLAUDE_DESIGN_RULES.md`:

1. Uma `<section class="slide" data-width="N" data-height="M">` por slide.
2. `position: absolute` com `left/top/width/height` em px dentro de `.slide`. **Sem flex/grid no canvas.**
3. Uma `<img>` por região de imagem real. **Sem CSS shapes simulando foto** (nada de `<div class="fake-person"><div class="head"></div></div>`).
4. Sem pseudo-elementos (`::before`, `::after`).
5. Sem `@keyframes`/animations.
6. Sem `mix-blend-mode`, `backdrop-filter`, `mask-image` complexo.
7. Pesos de fonte explícitos (400, 600, 700) — **nunca só `bold`**.
8. Copy em português, verbatim do brief.
9. `<meta name="hm-fonts" content="Fonte1,Fonte2">` no `<head>` listando **todas** as famílias usadas.
10. `<html data-template-name="..." data-segment="...">` com o slug do vertical inferido do brief (kebab-case, ex: `clinicas-medicas`, `ecommerce-moda`, `academias`).
11. Rotação só via `transform: rotate(Ndeg)` (origin default 50% 50%).
12. **Todo CSS deve ser inline (`style="..."`) — PROIBIDO usar `<style>` blocks ou classes CSS.** O conversor lê estilos diretamente dos atributos `style` de cada elemento. Bloco `<style>` no `<head>` impede o conversor de detectar gradientes, posições, cores e tamanhos. Única exceção: um reset mínimo `* { margin:0; box-sizing:border-box; }` é tolerado mas não recomendado.
13. Todo elemento com `linear-gradient` ou `radial-gradient` no `style` DEVE ter `data-darken="<preset>"` + `data-darken-opacity="<0.1-1.0>"` (ver seção "Gradientes" abaixo). NUNCA use cores brand em gradientes — fundo brand = sólido + darken overlay.

## Imagens contextuais (userAsset) — fluxo obrigatório

Para slots de `userAsset` (foto contextual, foto de ambiente, imagem ilustrativa), siga esta ordem:

### 1. Tente buscar uma imagem online estável

Antes de usar o placeholder, tente usar uma URL pública **estável e determinística** (mesma URL = mesma imagem em todo carregamento). Fontes aceitas:

```
https://picsum.photos/id/{ID}/{width}/{height}              ← foto fixa por ID (determinística)
```

**Regras de URL de imagem (OBRIGATÓRIAS):**
- **Sempre use URLs determinísticas** — a mesma URL deve retornar a mesma imagem em todo carregamento. Isso é crítico para cache do navegador e para que o editor não regenere imagens a cada abertura.
- **Nunca use query parameters de randomização** (`?random=N`, `?grayscale`, `?blur`). Eles fazem o CDN/browser tratar cada request como novo.
- **Nunca use `https://picsum.photos/{W}/{H}` sem ID** — sem `/id/{N}/`, o picsum retorna foto diferente a cada request.
- **Nunca use `https://source.unsplash.com/`** — este endpoint é deprecated e instável.
- Para picsum, use IDs numéricos fixos (ex: `/id/10/`, `/id/237/`, `/id/1015/`). Escolha IDs variados entre slides para diversidade visual.

Use no `src` diretamente — não embuta base64 de imagens online:

```html
<img class="image-placeholder" alt="Foto contextual"
     style="position:absolute; left:60px; top:200px; width:480px; height:580px; object-fit:cover;"
     src="https://picsum.photos/id/1015/480/580">
```

Se o ambiente não tiver acesso à internet ou a URL retornar erro: **vá para o passo 2**.

### 2. Use o placeholder pré-definido (fallback obrigatório)

Um único PNG com listras diagonais cinza/branco está em [`references/placeholders/image-placeholder.b64.txt`](./references/placeholders/image-placeholder.b64.txt). Cole o conteúdo do arquivo no `src`:

```html
<img class="image-placeholder" alt="Imagem a substituir"
     style="position:absolute; left:60px; top:200px; width:480px; height:580px; object-fit:cover;"
     src="data:image/png;base64,iVBORw0KGgoAAAANS...">
```

**Regras:**
- **Nunca gere SVG inline inventado** — cores, paths, formas. O placeholder é fixo e pré-definido.
- **Nunca use CSS shapes fingindo foto** (`<div class="fake-person">`, círculos, retângulos coloridos pretendendo ser imagem).
- O mesmo placeholder serve para qualquer proporção — `object-fit: cover` o adapta ao slot.
- Em Passo 1 (low-fi) use um `<div>` cinza `#E5E5E5` no lugar do `<img>` — sem base64 ainda. Nos Passos 2 e 3 use o fluxo acima.

Inaceitável em qualquer passo:

```html
<!-- NUNCA -->
<div class="fake-person"><div class="head"></div><div class="body"></div></div>
<svg><!-- SVG complexo inventado --></svg>
```

## Fotos profissionais (quando o brief pediu)

Tratamento padrão: **PNG cutout** (figura com fundo transparente). Use `object-fit: contain; object-position: bottom center; border-radius: 0;`. Avatar circular **só** se a referência/pedido pedir explicitamente.

Posições disponíveis e snippets prontos: [`references/professional-photo-placements.md`](./references/professional-photo-placements.md). Padrões cobertos:

1. **Hero cover full-figure** — slide 1, foto na coluna direita/esquerda ocupando ~50% largura × 88% altura.
2. **CTA final lateral** — último slide, foto ~37% largura ao lado do CTA.
3. **Overlap sobre foto contextual** — foto profissional sobreposta no canto da imagem de apoio (`userAsset`), criando sensação de "presença humana ancorando a cena".

Placeholders visuais (base64): [`references/placeholders/`](./references/placeholders/). O `brief.md` do interpreter sugere qual usar:

- `professional-photo-1.b64.txt` — masculino, traje formal/jaleco.
- `professional-photo-2.b64.txt` — feminino, traje casual/blazer.

O `brief.md` do interpreter indica qual usar. O designer pode trocar se a composição/tom do template pedir o outro perfil. Em produção, o `data-image-type="professionalPhoto"` faz o runtime substituir pela foto real do usuário no editor — o placeholder serve só para o reviewer e o auto-check avaliarem composição.

Marque com classe e alt semânticos:

```html
<img class="professional-photo" alt="Foto profissional"
     data-image-type="professionalPhoto"
     style="position:absolute; left:540px; top:80px; width:540px; height:1200px;
            object-fit:contain; object-position:bottom center; border-radius:0;"
     src="data:image/png;base64,<conteúdo de professional-photo-N.b64.txt>">
```

Anti-patterns críticos:

- **`object-fit: cover` em cutout** corta pés/cabeça e perde o efeito.
- **`border-radius` arredondado em cutout** mostra o fundo recortado por cima da figura sem fundo.
- **Texto sobre a face** (zona superior do slot, ~30%) cobre o que dá confiança ao leitor.

## Gradientes — quando e como usar

Gradiente tem **dois usos legítimos** na pipeline. Fora desses, não use.

**REGRA ZERO:** NUNCA use cores brand hex em gradientes. Background brand = fundo SÓLIDO na cor primary + overlay de escurecimento neutro (`transparent→rgba(0,0,0,N)`). Gradientes primary→secondary são **PROIBIDOS** (`data-variable-stops` não existe mais).

**Se o visual-plan descreve o fundo como "gradiente vinho/magenta/escuro"**, interprete SEMPRE como: fundo sólido primary + overlay `data-darken`. O art-director quer profundidade adaptável, não cores literais no gradiente.

### Sistema `data-darken` (OBRIGATÓRIO para todo gradiente)

Todo elemento com gradiente CSS DEVE ter `data-darken="<preset>"` + `data-darken-opacity="<0.1-1.0>"`. O converter lê estes atributos para gerar o Fabric JSON — se faltarem, o gradiente é **perdido**.

**Presets válidos:**

| `data-darken` | Direção | CSS equivalente |
|---------------|---------|-----------------|
| `bottom` | ↓ | `linear-gradient(to bottom, transparent, rgba(0,0,0,N))` |
| `top` | ↑ | `linear-gradient(to top, transparent, rgba(0,0,0,N))` |
| `right` | → | `linear-gradient(to right, transparent, rgba(0,0,0,N))` |
| `left` | ← | `linear-gradient(to left, transparent, rgba(0,0,0,N))` |
| `diagonal-se` | ↘ | `linear-gradient(135deg, transparent, rgba(0,0,0,N))` |
| `diagonal-ne` | ↗ | `linear-gradient(45deg, transparent, rgba(0,0,0,N))` |
| `vignette` | radial centro | `radial-gradient(circle at 50% 50%, transparent, rgba(0,0,0,N))` |
| `vignette-top-left` | radial tl | `radial-gradient(circle at 20% 10%, transparent, rgba(0,0,0,N))` |

### 1. Fundo brand com profundidade (uso mais comum)

Fundo sólido na cor primary + overlay `data-darken` para criar escurecimento atmosférico:

```html
<section class="slide" data-width="1080" data-height="1350"
         data-variable="primary" data-variable-target="background"
         style="position:relative; width:1080px; height:1350px; background:#E0005A;">

  <!-- Overlay de escurecimento — o converter lê data-darken e gera roundedRect com gradient fill -->
  <div data-darken="diagonal-se" data-darken-opacity="0.8"
       style="position:absolute; left:0; top:0; width:1080px; height:1350px;
              background:linear-gradient(135deg, transparent 0%, rgba(0,0,0,0.8) 100%);">
  </div>

  <!-- Card, textos, etc. por cima -->
</section>
```

O converter emite:
- `background`: hex primary sólido
- `backgroundVariableConfig`: `{ type: "solid", variable: "primary", alpha: 1 }`
- Primeiro objeto: roundedRect full-canvas com fill gradient (preset diagonal-se, opacity 0.8)

**⚠️ HARD GATE:** Se o visual-plan diz "gradiente" no fundo, interprete SEMPRE como solid primary + darken overlay. NUNCA emita `linear-gradient(135deg, #E0005A 0%, #A0033F 55%, #300816 100%)` — isso usa cores brand no gradiente e quebra adaptabilidade.

### 2. Overlay de legibilidade sobre foto

`<div>` sobre `<img>` para contraste de texto. Direção conforme posição do texto:

```html
<img style="position:absolute; left:0; top:0; width:1080px; height:1350px; object-fit:cover;"
     src="https://picsum.photos/id/10/1080/1350">

<div data-static="true" data-darken="bottom" data-darken-opacity="0.75"
     style="position:absolute; left:0; top:0; width:1080px; height:1350px;
            background:linear-gradient(to bottom, transparent 30%, rgba(0,0,0,0.75) 100%);">
</div>

<h1 style="position:absolute; left:60px; top:980px; ...">Título legível</h1>
```

Direções típicas:
- Texto no rodapé → `data-darken="bottom"`
- Texto no topo → `data-darken="top"`
- Texto na coluna esquerda → `data-darken="left"`
- Texto na coluna direita → `data-darken="right"`

**Opacidade orientativa:** `0.65–0.80` para texto peso 400; `0.45–0.60` para texto pesado (700+). Não passe de `0.85`.

### Glow / neon — como fazer no Fabric (CRÍTICO)

Efeito de glow **não funciona** como círculo translúcido no Fabric. Use `box-shadow` no CSS:

```html
<div style="position:absolute; left:123px; top:260px; width:834px; height:770px;
            border-radius:34px; background:#10151D; border:2px solid #1B2028;
            box-shadow: 0 0 60px 20px rgba(255,0,102,0.25);">
</div>
```

O converter traduz `box-shadow` para `shadow: { color, blur, offsetX, offsetY }` no objeto Fabric.

### Anti-patterns de gradiente (nunca faça)

- **Cores brand hex em qualquer gradiente** — PROIBIDO. Use transparent→rgba(0,0,0,N) sobre fundo sólido brand.
- **`data-variable-stops`** — eliminado da pipeline. Não use.
- **Gradiente sem `data-darken`** — o converter não parseia CSS. Sem o atributo, o gradiente vira cor sólida.
- **Gradiente multi-cor decorativo** (roxo→rosa→laranja) — kitsch, não editorial.
- **`linear-gradient` em `color:` de texto** — CSS inválido.
- **`<style>` block com gradientes** — converter não lê. Tudo inline.

## Famílias tipográficas seguras

Use Google Fonts via `<link>` no `<head>`. Quando preferir stack do sistema, sugestões em [`references/aesthetic-families.md`](./references/aesthetic-families.md). **Nunca** use Inter/Arial/Roboto/system-ui como **única** família para o design todo — emparelhe.

## O que esta skill NÃO faz

- Não adiciona `data-template-element`, `data-image-type`, `data-text-type`, `data-static`. Isso é trabalho do `gp2-template-marker`. (Exceção: `data-variable` é aplicado pelo designer conforme mapeamento do visual-plan.)
- Não gera Fabric JSON.
- Não faz upload.
- Não inventa scripts/frameworks/dependências externas.
- Não cria múltiplos arquivos HTML por slide — sempre **um** `template.html` com todas as `<section class="slide">`.

## Resposta final ao orquestrador

```markdown
Modo: <free | reference-driven>
HTML gerado em: `<path>/template.html`
Slides: <N>
Formato: <W>x<H>
Família estética: <nome — conforme visual-plan>
Movimento memorável: <nome — conforme visual-plan>
Composições usadas: <lista de códigos A1–A8 por slide, ex: slide1=A1, slide2=A3, slide3=A2, ...>
Cores de marca aplicadas: <primária somente | primária+secundária>
Elementos data-variable aplicados: <N elementos marcados — conforme mapeamento do visual-plan>
Foto profissional: <usada | não usada | reservada>
Divergências do plano: <nenhuma | lista — ver notes.md>
Screenshots: <path>/screenshots/slide-N.png
Notes: <path>/notes.md
Próximo passo: gp2-html-reviewer
```

## Quando refazer dentro do mesmo passo

- Passo 1 falhou no auto-check → refaz uma vez.
- Passo 2 falhou no auto-check → refaz uma vez.
- Passo 3 não tem refazer interno; se você notar problema visual grave, recomece do Passo 2.

Em todos os casos, registre o motivo em `notes.md` para o reviewer saber o que foi tentado.

Se o visual-plan estiver incompleto ou ausente, retorne ao art-director antes de prosseguir.
