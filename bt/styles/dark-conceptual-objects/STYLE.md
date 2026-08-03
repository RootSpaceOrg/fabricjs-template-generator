---
style: dark-conceptual-objects
status: draft            # vira `certificado` só após o protocolo completo + aprovação do Gustavo
reference: reference.png # colar a imagem-âncora (carrossel dark azul com objetos-metáfora)
familia: bold-educacional / brand-forward dark
funil: topo, meio
slides: 5–8
---

# dark-conceptual-objects

Carrossel dark premium onde **cada slide é uma metáfora de objeto**: uma ideia por slide, headline curta + objeto 3D/foto cutout iluminado como protagonista. Alto contraste, atmosfera tecnológica, swipe ritualizado.

## Tokens

| Token | Valor |
|-------|-------|
| Fundo base | gradiente vertical `#05070C → #0B1B33` (near-black → navy) com glow azul radial atrás do objeto (`rgba(43,108,255,0.35)`, raio ~40% do slide) |
| Acento | `data-variable="primary"` — no ref: azul elétrico `#2B6CFF`; palavras-chave da headline, pill de swipe, detalhes |
| Texto | branco `#F4F7FB`; secundário `#9FB0C7` |
| Display | sans bold condensada (Archivo/Barlow Condensed 700–800), UPPERCASE na capa, 56–72px, tracking 0 |
| Body | mesma família 400–500, 28–32px, sentence case |
| Header fixo (todo slide) | logo `data-image-type="brandLogo"` ~90px à esquerda + handle/ícones sociais discretos à direita (texto `instagramHandle`) |
| Pill swipe (todo slide exceto último) | "SWIPE >>" — pill 150×44px, gradiente do acento, canto inferior (esq ou dir alternando), estático |
| Ritmo tonal | base dark constante; o ritmo vem da POSIÇÃO do glow + densidade do objeto (R3 satisfeita por variação de luz — documentado; se o judge apertar, slides 3/5 sobem o glow p/ `#12305E`) |

## Papéis de slide (receitas)

### capa (slide 1)
- Headline UPPERCASE 2–4 linhas no terço superior, esquerda; 1–2 palavras em acento (`data-variable`).
- Sub-headline 1 linha ("vamos explorar os passos") em secundário.
- Objeto-metáfora dominante no meio-inferior (~55% da largura), glow atrás.
- Pill swipe inferior.

### conceito (miolo — papel repetível 3–6×)
- UMA frase (headline OU body destacado), 2–4 linhas, terço superior, centrada ou à esquerda (alternar).
- Objeto-metáfora da frase centralizado no meio-inferior (~45–60% largura), glow.
- Objeto de slides adjacentes NUNCA repete categoria (xadrez → alvo → chave → foguete ✓).

### pessoa (opcional, 1×, slide 2 típico)
- Igual a `conceito`, mas o "objeto" é `data-image-type="professionalPhoto"` (cutout, glow atrás) — dá rosto à peça.

### cta (último)
- Pergunta direta 2–3 linhas centrada no meio ("O que você está fazendo…?").
- Objeto leve como moldura (menor, ~30%), SEM pill de swipe; CTA textual conforme etapa do funil.

## Slots

| Slot | Tipo | Limites |
|------|------|---------|
| `s1_headline` | copy | 40–90 chars, UPPERCASE |
| `s1_sub` | copy | 20–60 chars |
| `sN_frase` (por conceito) | copy | 60–160 chars |
| `cta_pergunta` | copy | 40–100 chars |
| `sN_objeto` (por conceito/capa) | imagem gerada | `data-bt-generate="objeto único de <METAFORA> flutuando, fundo transparente/preto, iluminação azul cinematográfica dramática, estilo render 3D fotorrealista premium, sem texto"` — METAFORA vem da copy do slide |
| logo / handle / foto | slots plataforma | `brandLogo`, `instagramHandle`, `professionalPhoto` |

## Continuidade
- Glow como fio condutor: a mancha de luz muda de posição slide a slide desenhando um arco pela fita.
- Pill de swipe idêntica em posição alternada = ritual de navegação.
- (Blueprint pode adicionar 1 elemento cruzando fronteira — traço de luz horizontal — a decidir na certificação.)

## Riscos conhecidos (validar na certificação)
- R3 (monocromia): a variação de luz precisa convencer o judge — senão introduzir os 2 fundos elevados.
- Consistência dos objetos gerados: mesma fórmula de prompt + mesmo registro em TODOS (gerar em sequência, hero primeiro).
