---
name: gp2-art-director
description: "Segunda etapa da Pipeline v2 (após gp2-request-interpreter, antes de gp2-html-designer). Define o plano visual completo do template: composição slide-a-slide, paleta com hexs concretos e papéis brand, família estética com justificativa, movimento memorável com instrução composicional precisa, e mapeamento explícito dos elementos que devem receber data-variable. O designer executa — não inventa direção. Elimina o viés de repetição e garante que variáveis de cor sejam identificadas antes da codificação."
---

# gp2-art-director

Produz o **`visual-plan.md`** que o `gp2-html-designer` consome como plano de execução. Opera em dois modos, espelhando o interpreter.

## Princípio

O viés de repetição entre templates vem de o designer tomar decisões criativas (família estética, composição por slide, paleta, movimento memorável) no calor da codificação, sem um plano visual anterior. Esse vácuo faz o LLM convergir sempre para as mesmas soluções "seguras".

O art-director separa **direção criativa** de **execução técnica**:
- Direção criativa → art-director (este skill)
- Execução técnica → html-designer

O designer não escolhe família, não decide composição, não inventa paleta. Ele recebe um plano e o executa com precisão.

## Dois modos — responsabilidades distintas

| Modo | Quando | O que o art-director decide |
|------|--------|-----------------------------|
| **Free mode** | `brief.md` modo = free | Tudo: família estética, paleta com hexs, composição por slide, instrução do movimento memorável, mapeamento data-variable. Decisão criativa completa. |
| **Reference-driven mode** | `reference-spec.md` existe | **Só o que o interpreter NÃO capturou:** composição por slide (A1–A8), instrução composicional do movimento já declarado no spec, e mapeamento data-variable. Família, paleta e movimento memorável já estão travados no `reference-spec.md` — o art-director **não os re-resolve**, apenas os referencia. |

A divisão é simples: o interpreter captura a **intenção** (conteúdo, narrativa, e em reference-driven mode o vocabulário visual da referência). O art-director converte em **plano executável** (composição, instrução, variáveis). Em reference-driven mode, parte do vocabulário visual já chegou do interpreter — o art-director não o reescreve, apenas o estende com o que falta.

## Inputs

```
artifacts/gp2-request-interpreter/<slug>/brief.md
artifacts/gp2-request-interpreter/<slug>/reference-spec.md  ← somente reference-driven
```

## Output

```
artifacts/gp2-art-director/<slug>/visual-plan.md
```

---

## Workflow

### 1. Leia o brief e detecte o modo

Leia `brief.md` inteiro. Verifique se `reference-spec.md` existe. Leia também se existir.

**Em reference-driven mode:** os passos 2 e 3 abaixo são pulados — família e paleta já estão no `reference-spec.md`. Vá direto para o passo 4 (composição por slide). O `visual-plan.md` vai referenciar o spec em vez de reescrever o que ele já decidiu.

---

### 2. Escolha a família estética — FREE MODE ONLY

Em free mode, escolha **uma** das 8 famílias em [`../gp2-html-designer/references/aesthetic-families.md`](../gp2-html-designer/references/aesthetic-families.md).

**Regras de escolha para evitar viés:**

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

### 3. Resolva a paleta com hexs concretos — FREE MODE ONLY

Em free mode, resolva a paleta a partir do segmento + família estética. Nunca deixe aberto — o designer não deve escolher cor.

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
5. **Background** — LIGHT / DARK / Brand (primário sólido ou gradiente)

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

**Em free mode:** você escolhe o movimento. **Em reference-driven mode:** o movimento já está declarado no `reference-spec.md` — você apenas escreve a instrução composicional de como executá-lo (o spec diz "eyebrow numerado"; você diz como: posição, tamanho, fonte, cor, spacing).

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
- <descrição do elemento> → data-variable-stops="primary,secondary" (gradiente)
```

**O que SEMPRE deve ser mapeado quando presente:**
- Fundo sólido de slides Brand/CTA → `data-variable="primary" data-variable-target="background"`
- Fundo gradiente brand → `data-variable-stops="primary,secondary"`
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
| Eyebrow colorido | `data-variable="secondary"` |
| ... | ... |

## Notas para o designer

<Instruções específicas não cobertas acima: anti-patterns a evitar para este template, cuidados com o segmento, foto profissional, etc.>
```

### Reference-driven mode

Família e paleta já estão em `reference-spec.md` — não as repita. O visual-plan acrescenta apenas o que o spec não capturou: composição por slide e instrução composicional do movimento.

```markdown
# Plano Visual — <título do template>

## Modo
reference-driven

## Vocabulário visual
→ Ver `artifacts/gp2-request-interpreter/<slug>/reference-spec.md`
(família estética, paleta hex, tipografia, movimento memorável e elementos editoriais já estão lá)

## Instrução composicional do movimento memorável
**Nome:** <conforme declarado no reference-spec>
**Instrução:** <como executar concretamente — posição, tamanho, fonte, cor, spacing>
**Presença:** <em quais slides>

## Plano de slides

### Slide 1 — <papel narrativo> (background: LIGHT/DARK/Brand)
- **Composição:** <código + nome: ex: A1 — Full-bleed headline>
- **Zona headline:** <top | center | bottom | esquerda>
- **Zona imagem:** <left | right | full-bleed | ausente>
- **Densidade:** <densa | equilibrada | aberta>
- **Elementos-chave:** <o que o designer deve priorizar + quais elementos editoriais do spec aplicar aqui>
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
| Eyebrow colorido | `data-variable="secondary"` |
| ... | ... |

## Notas para o designer

<Instruções específicas: quais elementos editoriais do spec devem aparecer em quais slides, anti-patterns a evitar, foto profissional, etc.>
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
Vocabulário visual: ver reference-spec.md (família, paleta, tipografia, movimento já capturados pelo interpreter)
Instrução composicional escrita para: <nome do movimento memorável>
Slides planejados: <N> (composições: <A1, A3, A2, A4, A7, A1, A1 — exemplo>)
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
