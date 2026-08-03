---
style: clean-numbered-editorial
status: draft            # vira `certificado` só após o protocolo completo + aprovação do Gustavo
reference: reference.png # colar a imagem-âncora (carrossel branco numerado com acento vermelho)
familia: editorial clean / listicle expert
funil: meio (educação/autoridade); topo se o tema for erro/mito
slides: 6–10
---

# clean-numbered-editorial

Listicle de especialista em fundo claro: **um erro/ponto numerado por slide**, acento único vibrante, palavra-watermark gigante ao fundo, colagem leve de evidências (prints, fotos pequenas, carimbos). Denso mas respirado — autoridade sem peso.

## Tokens

| Token | Valor |
|-------|-------|
| Fundo | off-white `#F5F4F2` (LITERAL — nunca data-variable) |
| Acento | `data-variable="primary"` — no ref: vermelho `#E8291C`; números, setas, sublinhados, carimbos, blocos de destaque |
| Texto | near-black `#141414`; secundário `#5A5A5A` |
| Display | sans condensada bold UPPERCASE (Oswald/Archivo Expanded 700), 40–54px |
| Body | sans neutra 400 (Inter), 26–30px |
| Número do slide | `[N]` entre colchetes, no acento, 48–64px, topo do slide |
| Watermark | palavra-tema do slide em 200–300px, cinza `#E4E2DE` (~8% visível), atravessando o fundo (pode cruzar fronteira — dispositivo de continuidade) |
| Carimbos/badges | pill outline no acento, rotacionada -8° a +6°, texto UPPERCASE pequeno — máx 2 por slide, decoração editorial (não UI) |
| Evidência visual | 1 por slide de miolo: print emoldurado, foto P&B pequena, ou ícone-objeto; com marca ✓/✗ no acento quando couber |

## Papéis de slide (receitas)

### capa (slide 1)
- Número-total gigante no acento ("9") + título do listicle em 2–3 linhas UPPERCASE, coluna esquerda.
- **`professionalPhoto` OBRIGATÓRIO**: cutout ancorado na base, coluna direita (~38–45% da largura, do rodapé até ~70% da altura) — em saúde, rosto vende confiança; a metade inferior da capa nunca fica vazia.
- `instagramProfilePicture` (avatar ~64px) + `instagramName`/`instagramHandle` na base da coluna esquerda.
- 1 elemento gráfico do acento (círculo/carimbo) meio-cortado pela borda, atrás/ao lado da foto.

### item (miolo — papel repetível 4–8×) — TRÊS VARIANTES, nunca duas iguais adjacentes

Item idêntico repetido é a assinatura nº 1 de conteúdo IA — a referência varia a composição a cada slide. O blueprint define **3 variantes de layout** e os itens rotacionam entre elas (nunca a mesma variante em slides adjacentes; numa fita de 4 itens, use as 3):

**Anchors por variante (px, canvas 1080×1350 — desvio máximo ±5%; isto é contrato, não sugestão):**

**Variante A — editorial esquerda** (o layout atual)
- `[N]`: x=90 y=80, 52px · headline: x=90 y=150, largura 620, alinhada à esquerda
- watermark horizontal: y=430 (centro vertical da palavra), 170px, NUNCA acima de y=380 (folga ≥40px da headline)
- body: x=90 y=560, largura 520 · evidência: foto P&B x=600 y=760, ~380px, rotação +2..4° · tag preta: x=110 y=800

**Variante B — invertida à direita**
- `[N]`: x=940 y=80 · headline: alinhada à DIREITA, margem direita 90, y=150, largura 620
- watermark VERTICAL: rotacionada -90°, encostada na lateral esquerda (x≈40), ocupando y=200..1150
- evidência: foto GRANDE ~500px, SANGRANDO a borda esquerda (x=-60), y=620 · body: caixa branca sobre a foto, x=520 y=980, largura 460 · tag preta sobre o canto da foto

**Variante C — número ostentatório**
- `[N]` GIGANTE: 220px no acento, x=70 y=280 · headline: ao lado, x=360 y=330, largura 600
- SEM watermark (o número ocupa o papel) · body: x=360 y=560, largura 560
- evidência: ícone-objeto OU bloco no acento com palavra-chave, x=680 y=880, ~300px

**Regra anti-sobreposição (dura):** watermark nunca intercepta a caixa de headline nem de body (folga mínima 40px); texto nunca sobre texto. Violação = R2, judge QA reprova o slide.

- Elementos comuns a todas (identidade): `[N]` no acento, tipografia, carimbos (máx 2), paleta.
- 1 item do meio pode usar o **respiro invertido** (fundo do acento, texto branco) — conta como variante própria.
- **Evidência visual continua OBRIGATÓRIA** em toda variante (R4).

### cta (último)
- Fundo do acento full-bleed; recap em 1 frase + pedido único (comentar palavra / salvar / seguir — conforme funil).
- **`professionalPhoto` OBRIGATÓRIO**: cutout menor (~30% largura) ancorado na base direita — fecha a peça com o mesmo rosto que abriu.
- `instagramHandle` no rodapé.

## Slots

| Slot | Tipo | Limites |
|------|------|---------|
| `capa_total` | copy | número 1–2 chars |
| `capa_titulo` | copy | 40–80 chars, UPPERCASE |
| `item_headline` (por item) | copy | 25–70 chars, UPPERCASE |
| `item_body` (por item) | copy | 80–200 chars |
| `item_watermark` (por item) | copy | 1 palavra, 6–14 chars |
| `cta_recap` + `cta_pedido` | copy | 60–140 chars total |
| `item_evidencia` (por item) | imagem gerada | `data-bt-generate="<CONCEITO do item> como foto still editorial minimalista OU mockup de interface limpo, fundo neutro claro, sem texto legível"` |
| avatar/nome/handle | slots plataforma | `instagramProfilePicture`, `instagramName`, `instagramHandle` |
| foto do profissional | slot plataforma | `professionalPhoto` (placeholder canônico `professional-photo-1/2.b64.txt`) — capa e CTA, obrigatório |

## Continuidade
- Watermark atravessando fronteiras (palavra começa num slide e termina no outro) — dispositivo principal.
- **Regra dura da costura**: máx 1 palavra-watermark por fronteira, e ≥120px de respiro entre o fim de uma watermark e o início da seguinte — duas palavras se emendando na costura ("HISTORICOSEGURANÇA") é defeito, não continuidade.
- Sistema `[N]` + acento + carimbos = identidade que costura sem monotonia.
- Ritmo tonal: base clara constante com 1 slide de "respiro invertido" opcional (fundo do acento, texto branco) no meio da fita — bloco opcional do blueprint.

## Riscos conhecidos (validar na certificação)
- Densidade: R4 vigia área morta, mas o risco aqui é o oposto — poluição; máx 1 evidência + 2 carimbos por slide é regra dura.
- Watermark cruzando fronteira: conferir no slice que o corte cai bonito (ajustar tracking da palavra no blueprint).
- Prints/mockups gerados não podem imitar UI real de plataforma (Instagram/LinkedIn) a ponto de parecer print verdadeiro de terceiro.
