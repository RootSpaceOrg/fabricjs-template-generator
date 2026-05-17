---
name: gp2-art-director
description: "Segunda etapa da Pipeline v2 (após gp2-request-interpreter, antes de gp2-html-designer). Único dono de toda a direção visual do template. Em free mode: inventa família estética, paleta, composição, movimento memorável. Em reference-driven mode: analisa a(s) imagem(ns) de referência e extrai família, paleta hex, tipografia, movimento memorável e elementos editoriais, depois planeja composição slide-a-slide. Em ambos os modos: produz visual-plan.md completo com hexs concretos, instrução composicional precisa e mapeamento de data-variable. O designer executa — não inventa direção. Elimina o viés de repetição e garante que variáveis de cor sejam identificadas antes da codificação."
---

# gp2-art-director

Produz o **`visual-plan.md`** que o `gp2-html-designer` consome como plano de execução. Opera em dois modos, espelhando o interpreter.

## Princípio

O viés de repetição entre templates vem de o designer tomar decisões criativas (família estética, composição por slide, paleta, movimento memorável) no calor da codificação, sem um plano visual anterior. Esse vácuo faz o LLM convergir sempre para as mesmas soluções "seguras".

O art-director separa **direção criativa** de **execução técnica**:
- Direção criativa → art-director (este skill)
- Execução técnica → html-designer

O designer não escolhe família, não decide composição, não inventa paleta. Ele recebe um plano e o executa com precisão.

## Dois modos — responsabilidades consistentes

| Modo | Quando | O que o art-director decide |
|------|--------|-----------------------------|
| **Free mode** | `brief.md` modo = free | Tudo: família estética, paleta com hexs, composição por slide, instrução do movimento memorável, mapeamento data-variable. Decisão criativa completa — inventada a partir do brief. |
| **Reference-driven mode** | `brief.md` modo = reference-driven | Tudo: analisa a(s) imagem(ns) de referência e **extrai** família estética, paleta hex, tipografia, movimento memorável e elementos editoriais. Depois planeja composição por slide (A1–A8), escreve instrução composicional do movimento, e mapeia data-variable. Decisão criativa completa — extraída da referência. |

A divisão com o interpreter é simples: o interpreter captura **intenção de conteúdo** (narrativa, segmento, hook, chrome, foto profissional). O art-director é o **único dono de toda a direção visual** — em free mode inventa, em reference-driven mode extrai da referência. Resultado: o `visual-plan.md` é sempre o documento completo de direção visual, independente do modo.

## Inputs

```
artifacts/gp2-request-interpreter/<slug>/brief.md
Imagem(ns) de referência (passadas pelo orquestrador no contexto)  ← somente reference-driven
```

## Output

```
artifacts/gp2-art-director/<slug>/visual-plan.md
```

---

## Workflow

### 1. Leia o brief e detecte o modo

Leia `brief.md` inteiro. O campo `## Modo` indica `free` ou `reference-driven`.

**Em reference-driven mode:** antes de qualquer decisão criativa, execute o **passo 1b** abaixo (análise visual da referência). Depois siga os passos 2–6 normalmente — mas preenchendo família, paleta e movimento a partir do que extraiu da referência em vez de inventar.

---

### 1b. Analise a(s) imagem(ns) de referência — REFERENCE-DRIVEN MODE ONLY

O orquestrador passa as imagens de referência no contexto. Use a image tool para inspecioná-las e extraia **com precisão**:

#### Paleta
- Identifique os 2-4 hexs dominantes (ignore brancos puros e pretos puros). Use a image tool para ler cores se possível; senão, estime visualmente com a melhor precisão (`#RRGGBB`).
- Marque qual hex parece ser **primário** (acento dominante, CTA, ou fundo de marca) e qual é **secundário** (apoio).
- Anote neutros usados (off-white quente? cinza quente? preto profundo?) — o designer precisa saber para não trocar por neutros frios genéricos.

#### Tipografia
- Identifique a família **display** (títulos): serifa? sans? condensada? alto contraste? geométrica?
- Identifique a família **body** (corpo): sans neutra? humanista? mono?
- Se reconhecer a fonte, nomeie (ex: "Playfair Display", "Bebas Neue", "DM Sans"). Se não, descreva a categoria com precisão suficiente para o designer escolher uma família próxima.
- Capture pesos (display 700? 800? body 400? 500?) e casing (UPPERCASE? Title Case? lowercase deliberado?).
- Capture letter-spacing visivelmente diferente do default (eyebrow super-tracked? título com kerning negativo?).

#### Composição e ritmo
- Tipo de grade: 1 coluna? 2 colunas? assimétrica?
- Alinhamentos dominantes: tudo à esquerda? centrado? direita?
- Margens aparentes (densas? amplas?).
- Hierarquia tipográfica: eyebrow + título gigante? título + corpo + CTA? número editorial gigante?

#### Elementos editoriais e movimento memorável
- Listar **todos** os elementos visuais distintivos: eyebrow numerado, fios horizontais finos, faixa diagonal, número de slide gigante, ícone repetido, badge no canto, divisor vertical, bullet customizado, etc.
- Identificar **o** movimento memorável (o elemento que dá identidade ao design).

#### Gradientes
- Há overlay de escurecimento sobre foto (transparent→preto para legibilidade do texto)? Se sim: direção (to bottom / to right / to top), opacidade máxima (~0.65–0.80).
- Há **escurecimento atmosférico do fundo** (fundo parece escurecer nas bordas/cantos criando profundidade)? Se sim: anote como `escurecimento-atmosférico radial|linear, opacidade máxima N`. **NUNCA descreva com nomes de cor brand** (vinho, magenta, rosa) — o escurecimento é sempre `transparent→rgba(0,0,0,N)`. Se a referência mostra um fundo colorido que escurece, isso é fundo brand sólido + overlay transparente→preto.
- Há fundo de slide com escurecimento atmosférico (fundo sólido que escurece nas bordas criando profundidade)? Se sim: anotar como `escurecimento-atmosférico` com direção e opacidade.
- Há faixa decorativa com fade-out (cor sólida → transparent)? Se sim: posição, direção, cor.
- Se não há gradientes visíveis, anote "sem gradientes" — para que o designer não invente.

#### Imagens / fotos
- Há foto profissional/retrato? Se sim: tratamento (retangular editorial? circular avatar? full-bleed?), posição, proporção.
- Há foto contextual (produto, ambiente, ilustração)? Se sim: tratamento.
- Placeholder/textura?

#### Tom geral → família estética
- Premium silencioso? Bold direto-resposta? Editorial clínico? Soft wellness? — classifique na família estética mais próxima de [`../gp2-html-designer/references/aesthetic-families.md`](../gp2-html-designer/references/aesthetic-families.md).

#### O que **não** copiar literalmente
- Conteúdo/copy específico da referência (vai ser substituído).
- Logo/marca da referência.
- Fotos específicas (vão ser placeholders ou assets do usuário).
- Eventuais erros visuais da referência (overflow, contraste ruim) — corrija no plano.

Use os dados extraídos para preencher os passos 2, 3 e 5 abaixo (em vez de inventar).

---

### 2. Escolha a família estética

**Em free mode:** escolha **uma** das 8 famílias em [`../gp2-html-designer/references/aesthetic-families.md`](../gp2-html-designer/references/aesthetic-families.md).

**Em reference-driven mode:** use a família identificada no passo 1b (análise da referência). Classifique o estilo da referência na família mais próxima do catálogo. Se a referência não se encaixa perfeitamente, escolha a mais próxima e documente a diferença.

Regras de escolha para free mode:

**Regras de escolha para evitar viés (free mode):**

Não há lista fixa de segmentos — o vertical vem do brief e pode ser qualquer marca. Use o **tom do brief** como critério primário de seleção, e o **contexto do vertical** como refinamento. Force diversidade: se você perceber que está escolhendo sempre a mesma família para verticais similares, opte por uma alternativa compatível.

**Critério primário — tom do brief:**

| Tom declarado no brief | Famílias compatíveis |
|------------------------|----------------------|
| Educativo técnico / dados / autoridade científica | data-dense-profissional, magazine-authority, editorial-clinico |
| Premium / sofisticado / silencioso | luxury-refinado, premium-minimal |
| Acolhedor / emocional / bem-estar | soft-wellness, premium-minimal |
| Urgente / promocional / direto-resposta | bold-educacional, brutalist-direto |
| Editorial / jornalístico / autoridade de marca | magazine-authority, editorial-clinico |

**Refinamento por contexto do vertical:**

Dentro das famílias compatíveis com o tom, prefira:
- Vertical com apelo visual forte (moda, gastronomia, beleza, wellness) → famílias com mais respiração e foto (soft-wellness, luxury-refinado, premium-minimal)
- Vertical técnico ou regulado (saúde, finanças, jurídico, educação) → famílias com estrutura e rigor (editorial-clinico, data-dense-profissional, magazine-authority)
- Vertical de venda direta / e-commerce / promoção → famílias de impacto (bold-educacional, brutalist-direto)
- Vertical premium de nicho (odontologia estética, arquitetura, joalheria) → luxury-refinado ou premium-minimal

**Regra anti-viés:** se você está escolhendo editorial-clinico ou premium-minimal pela terceira vez consecutiva para pedidos similares, escolha uma família diferente que ainda seja compatível com o tom. Diversidade entre templates é um objetivo explícito do pipeline.

Documente a família escolhida **com justificativa de 1-2 linhas** no visual-plan.md.

---

### 3. Resolva a paleta com hexs concretos

**Em free mode:** resolva a paleta a partir do segmento + família estética. Nunca deixe aberto — o designer não deve escolher cor.

**Em reference-driven mode:** use os hexs extraídos no passo 1b. Atribua papéis (primary, secondary, neutros) conforme as regras abaixo. Se a referência tem cores ambíguas, resolva com base no uso observado (fundo brand = primary; acento de apoio = secondary).

**Regras de paleta:**
- Primary: o hex que vai nos fundos brand, CTA, elementos de destaque máximo
- Secondary: o hex de apoio — palavras-chave em destaque inline, acentos sutis, eyebrow colorido
- Neutros: pelo menos 2 — claro (fundo LIGHT slides) e escuro (fundo DARK slides). Nunca use #FFFFFF puro nem #000000 puro — use tons com personalidade.
- Neutros **nunca** são brand variables — são literais.

**Paletas por família (ponto de partida, não repetir sem variação):**

| Família | Primary | Secondary | Neutro claro | Neutro escuro |
|---------|---------|-----------|--------------|---------------|
| editorial-clinico | variar entre azul-petróleo, vinho, verde-sagê | acento complementar sutil | #F7F3EE | #1A1816 |
| premium-minimal | variar tons únicos em baixo volume | acento da mesma família, +20% saturação | #F5F5F0 | #1C1C1A |
| bold-educacional | primário saturado vibrante | neutro ou acento contrastante | #FFFFFF | #111111 |
| soft-wellness | verde-musgo, coral, vinho suave, oliva | acento suave complementar | #FAF8F5 | #2B2420 |
| magazine-authority | preto #111 como primary | um único acento forte saturado | #FAFAFA | #111111 |
| data-dense-profissional | azul-petróleo ou verde-laboratorio | vermelho-acento ou laranja-alerta | #F8F9FA | #1E2530 |
| luxury-refinado | dourado muito sutil, off-white profundo | acento em tons neutros frios | #F9F6F0 | #14120F |
| brutalist-direto | amarelo, magenta ou vermelho saturado | preto ou branco como secondary | #FFFFFF | #0D0D0D |

---

### 4. Planeje a composição de cada slide

Para **cada slide** do brief, defina:

1. **Tipo compositivo** — escolha um dos padrões abaixo
2. **Zona do headline** — onde fica o título principal (top / center / bottom / esquerda / direita)
3. **Zona da imagem** — onde fica a foto/placeholder (left / right / full-bleed / ausente / background)
4. **Densidade** — densa (pouco espaço, muita informação) / equilibrada / aberta (muito espaço, pouca informação)
5. **Background** — LIGHT / DARK / Brand+darken
6. **Gradientes** (se aplicável) — especifique quais gradientes este slide usa (ver catálogo abaixo)

### Catálogo de gradientes — use com parcimônia

O designer conhece **3 padrões legítimos** de gradiente. Se o plano não especifica gradiente, o designer usa cor sólida. Seja explícito:

| Padrão | Quando usar | O que especificar no plano |
|--------|------------|---------------------------|
| **Overlay de legibilidade** | Slides com foto full-bleed (A5) onde o texto precisa de contraste | Direção (to bottom / to right / to top / to left), opacidade máxima (0.65–0.80 para texto 400; 0.45–0.60 para texto 700+) |
| **Fundo brand gradiente** | **ELIMINADO** — use Escurecimento atmosférico em vez disso. Fundo sólido primary + overlay `data-darken` cria profundidade sem quebrar adaptabilidade de paleta | N/A — ver "Escurecimento atmosférico" |
| **Escurecimento atmosférico de fundo** | Fundo brand sólido que precisa de profundidade/vinheta sem perder adaptabilidade a outras paletas | Cor sólida brand no background (`data-variable="primary" data-variable-target="background"`) + overlay transparente→escuro por cima (`transparent → rgba(0,0,0,0.6–0.85)`). **Não use cores brand no gradiente** — use preto/transparente. Assim, trocar a primary muda o fundo sólido e o escurecimento se adapta naturalmente |
| **Faixa decorativa fade-out** | Transição suave entre blocos visuais (raro — só se a referência usa ou se resolve um problema de layout) | Posição (top/bottom), direção, cor, altura |

**Regras:**
- **Gradiente brand (primary→secondary visível) foi ELIMINADO da pipeline** — slides Brand usam primary sólido. Para profundidade, adicione overlay `data-darken` (escurecimento atmosférico neutro).
- **Overlay de legibilidade é obrigatório** em A5 (full-bleed foto) — sem overlay o texto fica ilegível. Mas o art-director deve escolher a direção com base na zona do texto (texto no rodapé → `to bottom`; texto no topo → `to top`).
- **Escurecimento atmosférico — regra (CRÍTICO para adaptabilidade):**
  - Para criar profundidade/vinheta (fundo escurece nas bordas, centro mais claro), use **escurecimento atmosférico**: fundo sólido brand + overlay `transparent→rgba(0,0,0,N)`. Isso adapta a qualquer paleta porque o overlay é neutro.
  - Gradiente brand (primary→secondary visível) foi **eliminado** da pipeline. Toda profundidade = cor sólida + overlay neutro.
  - **Anti-pattern observado:** usar cores brand literais (`#FF0066→#7A0730→#120711`) em gradientes que servem para escurecer. Quando o usuário troca a paleta para azul, o gradiente continua rosa→vinho→escuro. Use `transparent→rgba(0,0,0,N)` para escurecimento.
- **Faixa decorativa é rara** — só use se a referência mostra ou se resolve um problema concreto de layout. Nunca como enfeite gratuito.
- **Em reference-driven mode:** se a referência usa gradientes, capture-os no passo 1b. Se não usa, anote "sem gradientes". **Classifique cada gradiente observado** como atmosférico (escurecimento/vinheta — transparent→dark). Se a referência mostra gradiente brand (duas cores visíveis), converta para escurecimento atmosférico no plano (pipeline não suporta gradiente brand).

**Catálogo de tipos compositivos — use variedade, nunca repita o mesmo tipo em slides consecutivos sem motivo:**

| Código | Nome | Descrição | Quando usar |
|--------|------|-----------|-------------|
| `A1` | **Full-bleed headline** | Título gigante ocupando 60-80% do canvas, sem imagem lateral, fundo brand ou escuro. Toda a força na tipografia. | Capa de impacto, slide de dado único |
| `A2` | **Split 50/50** | Canvas dividido verticalmente em dois blocos iguais — esquerda texto, direita imagem (ou vice-versa). | Slides de miolo educativo com foto contextual |
| `A3` | **Split assimétrico** | Divisão 40/60 ou 35/65 — bloco de texto menor, imagem maior (ou vice-versa). Mais dinâmico que o 50/50. | Slides em que a imagem é mais importante que o texto |
| `A4` | **Coluna central com respiração** | Texto centralizado na coluna central (~680px) com margens amplas. Sem imagem lateral. | Slides de citação, insight único, dado numérico |
| `A5` | **Full-bleed foto com overlay** | Imagem ocupa 100% do canvas, overlay de gradiente para legibilidade do texto. Texto no rodapé ou no topo. | Slide emocional, CTA com foto de ambiente |
| `A6` | **Número editorial gigante** | Número de slide ou dado ocupa 40-60% do canvas como elemento visual principal. Texto ao lado ou abaixo. | Dados, estatísticas, numeração de listicle |
| `A7` | **Coluna esquerda alinhada** | Todo o conteúdo alinhado à esquerda, margem direita vazia (ou preenchida com elemento decorativo). | Slides de corpo educativo denso, bulletpoints |
| `A8` | **Stack vertical com divisores** | Conteúdo empilhado verticalmente com fios/divisores separando seções. | Slides comparação, características, specs |

**Regra de diversidade obrigatória:**
- Em carrosséis de ≥ 4 slides: não repita o mesmo código compositivo em mais de 2 slides consecutivos.
- Capa (slide 1) deve ter código diferente do slide 2.
- CTA (slide final) deve ter código diferente do slide anterior.

### 5. Escreva a instrução composicional do movimento memorável

O movimento memorável não pode ser apenas um nome — deve ser uma instrução executável que o designer implementa sem ambiguidade.

**Em free mode:** você escolhe o movimento e escreve a instrução. **Em reference-driven mode:** você identifica o movimento na referência (passo 1b) e escreve a instrução composicional de como executá-lo (posição, tamanho, fonte, cor, spacing).

**CUIDADO com vocabulário de cor na descrição do movimento:** Se o movimento inclui uma moldura/fundo que escurece, descreva como "fundo sólido primary com escurecimento atmosférico" — NUNCA como "gradiente vinho/magenta" ou "gradiente [nome-de-cor]→escuro". Usar nomes de cor brand na descrição do movimento faz o designer implementar com hex literais em vez de overlay adaptável.

**Formato:**
```
Movimento memorável: <nome>
Instrução: <como aplicar exatamente — posição, tamanho, fonte, cor, spacing>
Presença: <em quais slides aparece — todos | capa+CTA | slides de miolo | etc.>
```

**Exemplos de instruções composicionais precisas:**

- Eyebrow numerado:
  > `Instrução: div eyebrow esquerda, font-size 13px, CAPS, letter-spacing 3px, cor = secondary (ou primary em slides DARK). Formato "NN / TEMA" onde NN tem zero-padding. Margin-bottom 16px do título. Presença: todos os slides exceto CTA.`

- Número de slide gigante:
  > `Instrução: div posição absoluta top-right, font-size 280px, opacity 0.08, color = primary em LIGHT slides / white em DARK slides. Numeral alinhado à direita, saindo 40px do canvas. Presença: todos os slides de miolo.`

- Fio horizontal duplo:
  > `Instrução: dois div com height 1px, largura 80px, cor primary. O primeiro 24px acima do título, o segundo 16px abaixo do eyebrow. Presença: todos os slides.`

- Faixa diagonal de cor:
  > `Instrução: div rotacionado 8deg, position absolute, top -20px, left -60px, width 220px, height 100%, background secondary opacity 0.12. Ficando atrás do texto principal. Presença: slides de miolo LIGHT.`

- Badge no canto:
  > `Instrução: div 64x64px, border-radius 50%, background primary, posição top-right, margin 32px. Texto de 2 letras (sigla do tema) em white, font-size 18px, font-weight 700. Presença: todos os slides.`

### 6. Mapeie os elementos que devem receber data-variable

Este mapeamento é o **contrato com o marker**. Liste explicitamente quais elementos recebem atributo de variável de cor, para que o designer já adicione `data-variable` e o marker apenas confirme.

**Formato de lista:**
```
Elementos data-variable:
- <descrição do elemento> → data-variable="primary" data-variable-target="background"
- <descrição do elemento> → data-variable="secondary" (target padrão = color/fill)
- <descrição do elemento com escurecimento> → data-darken="<preset>" data-darken-opacity="<0.1-1.0>" (overlay neutro)
```

**O que SEMPRE deve ser mapeado quando presente:**
- Fundo sólido de slides Brand/CTA → `data-variable="primary" data-variable-target="background"`
- Fundo brand com escurecimento atmosférico → `data-variable="primary" data-variable-target="background"` na section + `<div data-darken="..." data-darken-opacity="...">` como overlay (converter emite roundedRect com gradient fill neutro)
- Eyebrow colorido (quando não é neutro) → `data-variable="secondary"` ou `"primary"`
- CTA button / bloco de destaque → `data-variable="primary" data-variable-target="background"`
- Número de slide ou dado colorido → `data-variable="primary"`
- Fio/divisor de cor brand → `data-variable="primary"` ou `"secondary"`
- Bloco de acento em palavra-chave (span inline) → `data-variable="secondary"`
- Fill do progress bar do carousel chrome (slides LIGHT) → `data-variable="primary"`
- Elemento de movimento memorável colorido → conforme cor usada

**O que NUNCA recebe data-variable:**
- Brancos, pretos, off-whites, cinzas — são neutros literais
- Overlays de legibilidade (gradiente rgba sobre foto) — são sempre literais
- Textos em cores neutras

---

## Output: visual-plan.md

O formato varia levemente por modo.

### Free mode

Escreva em `artifacts/gp2-art-director/<slug>/visual-plan.md`:

```markdown
# Plano Visual — <título do template>

## Modo
free

## Família estética
<nome> — <justificativa de 1-2 linhas>

## Paleta resolvida
- **Primary:** `#RRGGBB` — <papel: ex: "fundo dos slides Brand e CTA, destaque máximo">
- **Secondary:** `#RRGGBB` — <papel: ex: "eyebrow, palavras-chave em destaque inline, acento">
- **Neutro claro:** `#RRGGBB` — usado em slides LIGHT
- **Neutro escuro:** `#RRGGBB` — usado em slides DARK

## Movimento memorável
**Nome:** <ex: eyebrow numerado editorial>
**Instrução:** <instrução composicional completa — posição, tamanho, fonte, cor, spacing>
**Presença:** <em quais slides>

## Plano de slides

### Slide 1 — <papel narrativo> (background: LIGHT/DARK/Brand)
- **Composição:** <código + nome: ex: A1 — Full-bleed headline>
- **Zona headline:** <top | center | bottom | esquerda>
- **Zona imagem:** <left | right | full-bleed | ausente>
- **Densidade:** <densa | equilibrada | aberta>
- **Gradientes:** <nenhum | overlay to bottom 0.70 | escurecimento-atmosférico radial opacidade 0.85 | escurecimento-atmosférico diagonal-se opacidade 0.80 | faixa decorativa...>
- **Elementos-chave:** <o que o designer deve priorizar neste slide>
- **Copy orientativo:** <copy real do brief para este slide>

### Slide 2 — <papel narrativo> (background: LIGHT/DARK/Brand)
- **Composição:** <código + nome>
...

### Slide N (CTA) — <papel narrativo> (background: Brand)
...

## Mapeamento de data-variable

| Elemento | Atributo |
|----------|----------|
| Fundo slides Brand/CTA | `data-variable="primary" data-variable-target="background"` |
| Overlay de escurecimento (profundidade em fundo brand) | `data-darken="<preset>" data-darken-opacity="<N>"` no `<div>` overlay (converter → roundedRect com gradient fill neutro) |
| Eyebrow colorido | `data-variable="secondary"` |
| ... | ... |

## Notas para o designer

<Instruções específicas não cobertas acima: anti-patterns a evitar para este template, cuidados com o segmento, foto profissional, etc.>
```

### Reference-driven mode

O visual-plan contém TUDO — não há mais `reference-spec.md` separado. O art-director analisa a referência e grava o vocabulário visual extraído diretamente no plano.

```markdown
# Plano Visual — <título do template>

## Modo
reference-driven

## Vocabulário visual (extraído da referência)

### Família estética
<nome> — <justificativa baseada na análise da referência>

### Paleta (da referência)
- **Primary:** `#RRGGBB` — <papel observado: fundo? CTA? acento?>
- **Secondary:** `#RRGGBB` — <papel>
- **Neutro claro:** `#RRGGBB` — <off-white quente / cinza quente / etc.>
- **Neutro escuro:** `#RRGGBB` — <near-black / etc.>
- **Não usar:** <cinzas frios genéricos, gradientes default, etc., se a referência os evita>

### Tipografia (da referência)
- **Display:** <família reconhecida ou descrição categórica> — peso <N> — <UPPERCASE | Title Case | lowercase>
- **Body:** <família ou categoria> — peso <N>
- **Letter-spacing notável:** <ex: eyebrow tracking +200; título kerning -2%>
- **Stack fallback (se Google Fonts não disponível):** <ver aesthetic-families.md>

### Elementos editoriais a replicar
- <ex: eyebrow numerado em todos os slides>
- <ex: fio horizontal fino abaixo de cada título>
- <ex: número de slide gigante no canto inferior direito>

### Gradientes observados
- <ex: overlay to bottom rgba(0,0,0,0.70) nos slides com foto full-bleed>
- <ex: escurecimento-atmosférico radial transparent→rgba(0,0,0,0.85) no fundo externo de todos os slides>
- <ex: escurecimento-atmosférico diagonal-se transparent→rgba(0,0,0,0.80) nos slides Brand>
- <ex: sem gradientes>

**REGRA CRÍTICA:** Se a referência mostra um fundo que "escurece" criando profundidade/vinheta, classifique SEMPRE como `escurecimento-atmosférico` — nunca descreva com cores brand (ex: "gradiente vinho/magenta"). O fundo escurecido = cor sólida brand + overlay neutro `transparent→rgba(0,0,0,N)`. Descrever como "gradiente vinho→escuro" faz o designer usar hex literais e o template não se adapta a outras paletas.

### Tratamento de imagem observado
- **Foto profissional:** <cutout PNG full-figure | retangular editorial | circular avatar | full-bleed | ausente>
- **Foto contextual:** <ausente | crop editorial | ilustração>

## Movimento memorável
**Nome:** <identificado na referência>
**Instrução:** <como executar concretamente — posição, tamanho, fonte, cor, spacing>
**Presença:** <em quais slides>

## Plano de slides

### Slide 1 — <papel narrativo> (background: LIGHT/DARK/Brand)
- **Composição:** <código + nome: ex: A1 — Full-bleed headline>
- **Zona headline:** <top | center | bottom | esquerda>
- **Zona imagem:** <left | right | full-bleed | ausente>
- **Densidade:** <densa | equilibrada | aberta>
- **Gradientes:** <nenhum | overlay to bottom 0.70 | escurecimento-atmosférico radial opacidade 0.85 | escurecimento-atmosférico diagonal-se opacidade 0.80 | conforme referência>
- **Elementos-chave:** <o que o designer deve priorizar + quais elementos editoriais aplicar aqui>
- **Copy orientativo:** <copy real do brief para este slide>

### Slide 2 — <papel narrativo> (background: LIGHT/DARK/Brand)
- **Composição:** <código + nome>
...

### Slide N (CTA) — <papel narrativo> (background: Brand)
...

## Mapeamento de data-variable

| Elemento | Atributo |
|----------|----------|
| Fundo slides Brand/CTA | `data-variable="primary" data-variable-target="background"` |
| Overlay de escurecimento (profundidade em fundo brand) | `data-darken="<preset>" data-darken-opacity="<N>"` no `<div>` overlay (converter → roundedRect com gradient fill neutro) |
| Eyebrow colorido | `data-variable="secondary"` |
| ... | ... |

## Notas para o designer

<Instruções específicas: quais elementos editoriais devem aparecer em quais slides, anti-patterns a evitar, foto profissional, o que NÃO copiar da referência (logo, copy literal, fotos específicas), erros visuais da referência a corrigir.>
```

---

## Resposta final ao orquestrador

**Free mode:**
```markdown
Plano visual gerado: `artifacts/gp2-art-director/<slug>/visual-plan.md`
Modo: free
Família estética: <nome> — <justificativa em 1 linha>
Paleta: primary <hex> / secondary <hex> / neutro claro <hex> / neutro escuro <hex>
Slides planejados: <N> (composições: <A1, A3, A2, A4, A7, A1, A1 — exemplo>)
Movimento memorável: <nome>
Elementos data-variable mapeados: <N>
Próximo passo: gp2-html-designer
```

**Reference-driven mode:**
```markdown
Plano visual gerado: `artifacts/gp2-art-director/<slug>/visual-plan.md`
Modo: reference-driven
Família estética: <nome> — <extraída da referência>
Paleta: primary <hex> / secondary <hex> / neutro claro <hex> / neutro escuro <hex>
Tipografia: display <família/categoria> / body <família/categoria>
Slides planejados: <N> (composições: <A1, A3, A2, A4, A7, A1, A1 — exemplo>)
Movimento memorável: <nome> (identificado na referência)
Elementos data-variable mapeados: <N>
Próximo passo: gp2-html-designer
```

---

## O que esta skill NÃO faz

- Não escreve HTML. Apenas planeja.
- Não aplica `data-variable` no HTML — mapeia o que deve receber; o designer aplica, o marker confirma.
- Não decide copy por slide — usa o copy do brief.
- Não escolhe tamanhos exatos de fonte — isso é Passo 3 do designer.
- Não escolhe posições absolutas em px — define zonas, o designer escolhe as coordenadas.
